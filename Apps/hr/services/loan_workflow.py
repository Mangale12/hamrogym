from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from Apps.hr.models import LoanAccount, LoanApplication, LoanApprovalHistory, LoanDisbursement, LoanInstallment, LoanLedger, LoanRepayment


ZERO = Decimal("0.00")


def _quantize(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _add_months(base_date: date, months: int) -> date:
    month = base_date.month - 1 + months
    year = base_date.year + month // 12
    month = month % 12 + 1
    day = min(base_date.day, monthrange(year, month)[1])
    return date(year, month, day)


def _approval_chain_for_employee(employee, max_levels: int = 5):
    approvers = []
    seen_user_ids = set()
    current_manager = employee.reporting_manager
    while current_manager is not None and len(approvers) < max_levels:
        user_id = getattr(current_manager, "user_id", None)
        if not user_id or user_id in seen_user_ids:
            break
        approvers.append(current_manager.user)
        seen_user_ids.add(user_id)
        current_manager = current_manager.reporting_manager
    return approvers


def _ensure_loan_approvals(loan_application: LoanApplication):
    if not loan_application.loan_type.requires_approval:
        LoanApprovalHistory.objects.filter(loan_application=loan_application).delete()
        return []
    existing = list(LoanApprovalHistory.objects.filter(loan_application=loan_application).order_by("level", "id"))
    if existing:
        return existing
    approvers = _approval_chain_for_employee(loan_application.employee)
    if not approvers:
        raise ValidationError({"employee": "No reporting-manager approval chain found for this employee."})
    approvals = [
        LoanApprovalHistory(loan_application=loan_application, approved_by=approver, level=index, status="pending")
        for index, approver in enumerate(approvers, start=1)
    ]
    return LoanApprovalHistory.objects.bulk_create(approvals)


def _pending_approval(loan_application: LoanApplication):
    return loan_application.approvals.filter(status="pending").order_by("level", "id").first()


def _effective_interest_rate(loan_application: LoanApplication) -> Decimal:
    policy = loan_application.loan_type.policies.filter(is_active=True).order_by("priority", "id").first()
    if policy and policy.interest_rate is not None:
        return _quantize(policy.interest_rate)
    return _quantize(loan_application.loan_type.default_interest_rate)


def calculate_loan_emi(*, principal_amount, interest_rate, tenure_months, interest_type) -> Decimal:
    principal = _quantize(principal_amount)
    rate = _quantize(interest_rate)
    tenure = int(tenure_months or 0)
    if principal <= 0 or tenure <= 0:
        return ZERO
    if interest_type == "none" or rate <= 0:
        return _quantize(principal / tenure)
    if interest_type == "flat":
        total_interest = principal * (rate / Decimal("100")) * Decimal(tenure / 12)
        return _quantize((principal + total_interest) / tenure)
    monthly_rate = (rate / Decimal("100")) / Decimal("12")
    factor = (Decimal("1") + monthly_rate) ** tenure
    emi = (principal * monthly_rate * factor) / (factor - Decimal("1"))
    return _quantize(emi)


def _build_schedule_rows(*, loan_account: LoanAccount):
    principal = _quantize(loan_account.principal_amount)
    rate = _quantize(loan_account.interest_rate)
    emi = _quantize(loan_account.emi_amount)
    remaining = principal
    rows = []
    for installment_no in range(1, loan_account.tenure_months + 1):
        due_date = _add_months(loan_account.start_date, installment_no - 1)
        if loan_account.interest_type == "none" or rate <= 0:
            interest_amount = ZERO
            principal_amount = emi
        elif loan_account.interest_type == "flat":
            interest_amount = (principal * (rate / Decimal("100")) / Decimal("12")).quantize(Decimal("0.01"))
            principal_amount = _quantize(emi - interest_amount)
        else:
            interest_amount = _quantize(remaining * ((rate / Decimal("100")) / Decimal("12")))
            principal_amount = _quantize(emi - interest_amount)
        if installment_no == loan_account.tenure_months:
            principal_amount = remaining
        total_amount = _quantize(principal_amount + interest_amount)
        remaining = _quantize(max(remaining - principal_amount, ZERO))
        rows.append(
            LoanInstallment(
                loan_account=loan_account,
                installment_no=installment_no,
                due_date=due_date,
                principal_amount=principal_amount,
                interest_amount=interest_amount,
                total_amount=total_amount,
                paid_amount=ZERO,
                balance_amount=total_amount,
                status="pending",
            )
        )
    return rows


def _create_loan_account(loan_application: LoanApplication):
    if hasattr(loan_application, "loan_account"):
        return loan_application.loan_account
    interest_rate = _effective_interest_rate(loan_application)
    emi = calculate_loan_emi(
        principal_amount=loan_application.requested_amount,
        interest_rate=interest_rate,
        tenure_months=loan_application.requested_tenure,
        interest_type=loan_application.loan_type.interest_type,
    )
    start_date = timezone.localdate()
    end_date = _add_months(start_date, loan_application.requested_tenure - 1)
    loan_account = LoanAccount.objects.create(
        loan_application=loan_application,
        employee=loan_application.employee,
        loan_type=loan_application.loan_type,
        principal_amount=loan_application.requested_amount,
        interest_rate=interest_rate,
        interest_type=loan_application.loan_type.interest_type,
        tenure_months=loan_application.requested_tenure,
        emi_amount=emi,
        start_date=start_date,
        end_date=end_date,
        outstanding_balance=_quantize(emi * loan_application.requested_tenure),
        status="active",
        remarks=loan_application.remarks,
    )
    LoanInstallment.objects.bulk_create(_build_schedule_rows(loan_account=loan_account))
    return loan_account


def create_loan_ledger_entry(*, loan_account: LoanAccount, transaction_type: str, amount, balance_after, reference=None, remarks=""):
    return LoanLedger.objects.create(
        loan_account=loan_account,
        transaction_type=transaction_type,
        amount=_quantize(amount),
        balance_after=_quantize(balance_after),
        reference_id=getattr(reference, "id", None),
        reference_type=reference.__class__.__name__ if reference is not None else "",
        date=timezone.localdate(),
        remarks=remarks,
    )


@transaction.atomic
def prepare_loan_application(*, loan_application: LoanApplication):
    loan_application.full_clean()
    if loan_application.status not in {"approved", "rejected", "cancelled"}:
        loan_application.status = "submitted"
    _ensure_loan_approvals(loan_application)
    return loan_application


@transaction.atomic
def approve_loan_application(*, loan_application: LoanApplication, acting_user):
    if loan_application.status == "approved":
        raise ValidationError("This loan application is already approved.")
    prepare_loan_application(loan_application=loan_application)
    if not loan_application.loan_type.requires_approval:
        loan_account = _create_loan_account(loan_application)
        loan_application.status = "approved"
        loan_application.approved_by = acting_user
        loan_application.approved_date = timezone.now()
        loan_application.rejected_by = None
        loan_application.save(update_fields=["status", "approved_by", "approved_date", "rejected_by", "updated_at"])
        return {"finalized": True, "loan_account_id": loan_account.id}
    pending_approval = _pending_approval(loan_application)
    if pending_approval is None:
        raise ValidationError("This loan application has no pending approval step.")
    if pending_approval.approved_by_id != acting_user.id:
        raise ValidationError("You are not the current approver for this loan application.")
    pending_approval.status = "approved"
    pending_approval.action_date = timezone.now()
    pending_approval.save(update_fields=["status", "action_date"])
    next_pending = _pending_approval(loan_application)
    if next_pending is not None:
        loan_application.status = "submitted"
        loan_application.approved_by = None
        loan_application.approved_date = None
        loan_application.rejected_by = None
        loan_application.save(update_fields=["status", "approved_by", "approved_date", "rejected_by", "updated_at"])
        return {"finalized": False, "level": pending_approval.level, "next_level": next_pending.level}
    loan_account = _create_loan_account(loan_application)
    loan_application.status = "approved"
    loan_application.approved_by = acting_user
    loan_application.approved_date = timezone.now()
    loan_application.rejected_by = None
    loan_application.save(update_fields=["status", "approved_by", "approved_date", "rejected_by", "updated_at"])
    return {"finalized": True, "level": pending_approval.level, "loan_account_id": loan_account.id}


@transaction.atomic
def reject_loan_application(*, loan_application: LoanApplication, acting_user):
    prepare_loan_application(loan_application=loan_application)
    pending_approval = _pending_approval(loan_application)
    if loan_application.loan_type.requires_approval:
        if pending_approval is None:
            raise ValidationError("This loan application has no pending approval step.")
        if pending_approval.approved_by_id != acting_user.id:
            raise ValidationError("You are not the current approver for this loan application.")
        pending_approval.status = "rejected"
        pending_approval.action_date = timezone.now()
        pending_approval.save(update_fields=["status", "action_date"])
        loan_application.approvals.exclude(id=pending_approval.id).update(status="cancelled", action_date=timezone.now())
    loan_application.status = "rejected"
    loan_application.rejected_by = acting_user
    loan_application.approved_by = None
    loan_application.approved_date = None
    loan_application.save(update_fields=["status", "rejected_by", "approved_by", "approved_date", "updated_at"])
    return {"finalized": True, "level": getattr(pending_approval, "level", None)}


@transaction.atomic
def record_loan_disbursement(*, loan_account: LoanAccount, amount=None, disbursed_date=None, payment_mode="bank", reference_no="", remarks="", disbursement=None):
    if disbursement is None:
        disbursement = LoanDisbursement.objects.create(
            loan_account=loan_account,
            amount=_quantize(amount),
            disbursed_date=disbursed_date,
            payment_mode=payment_mode,
            reference_no=reference_no,
            remarks=remarks,
        )
    else:
        loan_account = disbursement.loan_account
    loan_account.disbursement_date = disbursed_date
    loan_account.save(update_fields=["disbursement_date", "updated_at"])
    create_loan_ledger_entry(
        loan_account=loan_account,
        transaction_type="disbursement",
        amount=disbursement.amount,
        balance_after=loan_account.outstanding_balance,
        reference=disbursement,
        remarks=remarks or "Loan disbursed.",
    )
    return disbursement


@transaction.atomic
def record_loan_repayment(*, loan_installment: LoanInstallment, amount_paid=None, payment_date=None, payment_mode="bank", reference_no="", remarks="", repayment=None):
    if repayment is None:
        amount_paid = _quantize(amount_paid)
    else:
        loan_installment = repayment.loan_installment
        amount_paid = _quantize(repayment.amount_paid)
        payment_date = repayment.payment_date
        payment_mode = repayment.payment_mode
        reference_no = repayment.reference_no
        remarks = repayment.remarks
    if amount_paid <= 0:
        raise ValidationError({"amount_paid": "Repayment amount must be greater than zero."})
    if amount_paid > loan_installment.balance_amount:
        raise ValidationError({"amount_paid": "Repayment amount exceeds installment balance."})
    if repayment is None:
        repayment = LoanRepayment.objects.create(
            loan_installment=loan_installment,
            payment_date=payment_date,
            amount_paid=amount_paid,
            payment_mode=payment_mode,
            reference_no=reference_no,
            remarks=remarks,
        )
    loan_installment.paid_amount = _quantize(loan_installment.paid_amount + amount_paid)
    loan_installment.balance_amount = _quantize(loan_installment.total_amount - loan_installment.paid_amount)
    loan_installment.status = "paid" if loan_installment.balance_amount <= 0 else "partial"
    loan_installment.save(update_fields=["paid_amount", "balance_amount", "status", "updated_at"])
    loan_account = loan_installment.loan_account
    loan_account.outstanding_balance = _quantize(loan_account.outstanding_balance - amount_paid)
    if loan_account.outstanding_balance <= 0:
        loan_account.outstanding_balance = ZERO
        loan_account.status = "closed"
    loan_account.save(update_fields=["outstanding_balance", "status", "updated_at"])
    create_loan_ledger_entry(
        loan_account=loan_account,
        transaction_type="repayment",
        amount=amount_paid,
        balance_after=loan_account.outstanding_balance,
        reference=repayment,
        remarks=remarks or f"Repayment for installment {loan_installment.installment_no}.",
    )
    return repayment
