from django.utils import timezone

from core.config import EntityConfig
from core.registry import register_entity
from nepanest.modules.loans.datatables import (
    LOAN_ACCOUNT_COLUMNS,
    LOAN_APPLICATION_COLUMNS,
    LOAN_DISBURSEMENT_COLUMNS,
    LOAN_INSTALLMENT_COLUMNS,
    LOAN_LEDGER_COLUMNS,
    LOAN_REPAYMENT_COLUMNS,
    LoanAccountDataTableView,
    LoanApplicationDataTableView,
    LoanDisbursementDataTableView,
    LoanInstallmentDataTableView,
    LoanLedgerDataTableView,
    LoanRepaymentDataTableView,
)
from nepanest.modules.loans.forms import (
    LoanAccountForm,
    LoanApplicationForm,
    LoanDisbursementForm,
    LoanInstallmentForm,
    LoanLedgerForm,
    LoanRepaymentForm,
)
from nepanest.modules.loans.models import (
    LoanAccount,
    LoanApplication,
    LoanDisbursement,
    LoanInstallment,
    LoanLedger,
    LoanRepayment,
)
from nepanest.modules.loans.services import (
    approve_loan_application,
    prepare_loan_application,
    record_loan_disbursement,
    record_loan_repayment,
    reject_loan_application,
)


APPROVAL_HISTORY_SECTION = {
    "title": "Approval History",
    "layout": "table",
    "allow_add": False,
    "allow_remove": False,
    "fields": [
        {"name": "level", "label": "Level", "type": "text", "readonly": True},
        {"name": "approver_name", "label": "Approver", "type": "text", "readonly": True},
        {"name": "status", "label": "Status", "type": "text", "readonly": True},
        {"name": "action_date_display", "label": "Action At", "type": "text", "readonly": True},
        {"name": "remarks", "label": "Remarks", "type": "textarea", "readonly": True},
    ],
}


def _load_loan_application_sections(loan_application: LoanApplication):
    rows = []
    for approval in loan_application.approvals.select_related("approved_by").order_by("level", "id"):
        rows.append(
            {
                "id": approval.id,
                "level": approval.level,
                "approver_name": approval.approved_by.get_full_name() or approval.approved_by.username,
                "status": approval.status,
                "action_date_display": approval.action_date.strftime("%Y-%m-%d %H:%M") if approval.action_date else "",
                "remarks": approval.remarks,
            }
        )
    return {"approval_history": rows}


def _post_save_loan_application(_request, loan_application: LoanApplication) -> None:
    prepare_loan_application(loan_application=loan_application)
    loan_application.save(update_fields=["status", "updated_at"])


def _approve_loan_application(request, loan_application: LoanApplication):
    result = approve_loan_application(loan_application=loan_application, acting_user=request.user)
    if result.get("finalized"):
        return {"message": "Loan application fully approved and loan account created."}
    return {"message": f"Level {result.get('level')} approved. Forwarded to level {result.get('next_level')}."}


def _reject_loan_application(request, loan_application: LoanApplication):
    reject_loan_application(loan_application=loan_application, acting_user=request.user)
    return {"message": "Loan application rejected successfully."}


def _post_loan_disbursement(_request, loan_disbursement: LoanDisbursement):
    record_loan_disbursement(
        loan_account=loan_disbursement.loan_account,
        disbursement=loan_disbursement,
        disbursed_date=loan_disbursement.disbursed_date,
        remarks=loan_disbursement.remarks,
    )


def _post_loan_repayment(_request, loan_repayment: LoanRepayment):
    record_loan_repayment(loan_installment=loan_repayment.loan_installment, repayment=loan_repayment)


_loan_application_columns = [
    {"name": "employee", "title": "Employee"},
    {"name": "loan_type", "title": "Loan Type"},
    {"name": "requested_amount", "title": "Requested Amount"},
    {"name": "requested_tenure", "title": "Tenure"},
    {
        "name": "status",
        "title": "Status",
        "render": (
            "function(data){"
            "const map={draft:'secondary',submitted:'warning',approved:'success',rejected:'danger',cancelled:'dark'};"
            "const cls=map[data]||'light';"
            "return `<span class=\"badge bg-${cls}\">${data||''}</span>`;"
            "}"
        ),
    },
    {"name": "applied_date", "title": "Applied At"},
    {"name": "approved_date", "title": "Approved At"},
]

_loan_account_columns = [{"name": key, "title": key.replace("_", " ").title()} for key, _ in LOAN_ACCOUNT_COLUMNS if key != "id"]
_loan_installment_columns = [{"name": key, "title": key.replace("_", " ").title()} for key, _ in LOAN_INSTALLMENT_COLUMNS if key != "id"]
_loan_disbursement_columns = [{"name": key, "title": key.replace("_", " ").title()} for key, _ in LOAN_DISBURSEMENT_COLUMNS if key != "id"]
_loan_repayment_columns = [{"name": key, "title": key.replace("_", " ").title()} for key, _ in LOAN_REPAYMENT_COLUMNS if key != "id"]
_loan_ledger_columns = [{"name": key, "title": key.replace("_", " ").title()} for key, _ in LOAN_LEDGER_COLUMNS if key != "id"]


register_entity(
    EntityConfig(
        name="loan_application",
        url_path="loan-applications",
        verbose_name="Loan Application",
        model=LoanApplication,
        form_class=LoanApplicationForm,
        datatable_view=LoanApplicationDataTableView,
        fields=[],
        tabs=[
            {
                "key": "request",
                "label": "Application Details",
                "fields": [
                    {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 6, "url_name": "employee_select"},
                    {"name": "loan_type", "label": "Loan Type", "type": "select", "required": True, "col": 6, "url_name": "loan_type_select"},
                    {"name": "requested_amount", "label": "Requested Amount", "type": "number", "required": True, "col": 6},
                    {"name": "requested_tenure", "label": "Requested Tenure (Months)", "type": "number", "required": True, "col": 6},
                    {"name": "reason", "label": "Business Reason", "type": "textarea", "required": True, "col": 12},
                    {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
                ],
            },
            {
                "key": "approvals",
                "label": "Approval Trail",
                "fields": [],
                "requires_id": True,
                "sections": ["approval_history"],
            },
        ],
        dynamic_sections={"approval_history": APPROVAL_HISTORY_SECTION},
        dynamic_sections_loader=_load_loan_application_sections,
        post_save=_post_save_loan_application,
        row_actions={"approve": _approve_loan_application, "reject": _reject_loan_application},
        action_state_field="status",
        hide_edit_on_values=["approved", "rejected", "cancelled"],
        hide_delete_on_values=["approved"],
        action_buttons=[
            {"action_name": "approve", "title": "Approve Loan", "label": "", "icon_class": "fas fa-check", "class_name": "btn-outline-success", "confirm_text": "Approve this loan application?", "success_message": "Loan application approved successfully.", "hide_on_values": ["approved", "rejected", "cancelled"]},
            {"action_name": "reject", "title": "Reject Loan", "label": "", "icon_class": "fas fa-times", "class_name": "btn-outline-danger", "confirm_text": "Reject this loan application?", "success_message": "Loan application rejected successfully.", "hide_on_values": ["approved", "rejected", "cancelled"]},
        ],
        datatable_columns=_loan_application_columns,
    )
)


register_entity(
    EntityConfig(
        name="loan_account",
        url_path="loan-accounts",
        verbose_name="Loan Account",
        model=LoanAccount,
        form_class=LoanAccountForm,
        datatable_view=LoanAccountDataTableView,
        fields=[
            {"name": "loan_application", "label": "Loan Application", "type": "select", "required": True, "col": 6, "url_name": "loan_application_select"},
            {"name": "employee", "label": "Employee", "type": "select", "required": True, "col": 6, "url_name": "employee_select"},
            {"name": "loan_type", "label": "Loan Type", "type": "select", "required": True, "col": 6, "url_name": "loan_type_select"},
            {"name": "principal_amount", "label": "Principal", "type": "number", "required": True, "col": 4},
            {"name": "interest_rate", "label": "Interest Rate", "type": "number", "required": True, "col": 4},
            {"name": "interest_type", "label": "Interest Type", "type": "static_select", "required": True, "col": 4, "options": LoanAccount._meta.get_field("interest_type").choices},
            {"name": "tenure_months", "label": "Tenure", "type": "number", "required": True, "col": 4},
            {"name": "emi_amount", "label": "EMI Amount", "type": "number", "required": True, "col": 4},
            {"name": "outstanding_balance", "label": "Outstanding Balance", "type": "number", "required": True, "col": 4},
            {"name": "disbursement_date", "label": "Disbursement Date", "type": "date", "required": False, "col": 4},
            {"name": "start_date", "label": "Start Date", "type": "date", "required": True, "col": 4},
            {"name": "end_date", "label": "End Date", "type": "date", "required": True, "col": 4},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 4, "options": LoanAccount._meta.get_field("status").choices},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=_loan_account_columns,
        show_create=False,
        show_actions=False,
        show_view=True,
    )
)


register_entity(
    EntityConfig(
        name="loan_installment",
        url_path="loan-installments",
        verbose_name="Loan Installment",
        model=LoanInstallment,
        form_class=LoanInstallmentForm,
        datatable_view=LoanInstallmentDataTableView,
        fields=[
            {"name": "loan_account", "label": "Loan Account", "type": "select", "required": True, "col": 6, "url_name": "loan_account_select"},
            {"name": "installment_no", "label": "Installment No", "type": "number", "required": True, "col": 2},
            {"name": "due_date", "label": "Due Date", "type": "date", "required": True, "col": 4},
            {"name": "principal_amount", "label": "Principal", "type": "number", "required": True, "col": 3},
            {"name": "interest_amount", "label": "Interest", "type": "number", "required": True, "col": 3},
            {"name": "total_amount", "label": "Total", "type": "number", "required": True, "col": 3},
            {"name": "paid_amount", "label": "Paid", "type": "number", "required": True, "col": 3},
            {"name": "balance_amount", "label": "Balance", "type": "number", "required": True, "col": 3},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 3, "options": LoanInstallment._meta.get_field("status").choices},
        ],
        datatable_columns=_loan_installment_columns,
        show_create=False,
        show_actions=False,
        show_view=True,
    )
)


register_entity(
    EntityConfig(
        name="loan_disbursement",
        url_path="loan-disbursements",
        verbose_name="Loan Disbursement",
        model=LoanDisbursement,
        form_class=LoanDisbursementForm,
        datatable_view=LoanDisbursementDataTableView,
        fields=[
            {"name": "loan_account", "label": "Loan Account", "type": "select", "required": True, "col": 6, "url_name": "loan_account_select"},
            {"name": "amount", "label": "Amount", "type": "number", "required": True, "col": 3},
            {"name": "disbursed_date", "label": "Disbursed Date", "type": "date", "required": True, "col": 3},
            {"name": "payment_mode", "label": "Payment Mode", "type": "static_select", "required": True, "col": 4, "options": LoanDisbursement._meta.get_field("payment_mode").choices},
            {"name": "reference_no", "label": "Reference No", "type": "text", "required": False, "col": 4},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        post_save=_post_loan_disbursement,
        datatable_columns=_loan_disbursement_columns,
        show_actions=False,
        show_view=True,
    )
)


register_entity(
    EntityConfig(
        name="loan_repayment",
        url_path="loan-repayments",
        verbose_name="Loan Repayment",
        model=LoanRepayment,
        form_class=LoanRepaymentForm,
        datatable_view=LoanRepaymentDataTableView,
        fields=[
            {"name": "loan_installment", "label": "Loan Installment", "type": "select", "required": True, "col": 6, "url_name": "loan_installment_select"},
            {"name": "payment_date", "label": "Payment Date", "type": "date", "required": True, "col": 3},
            {"name": "amount_paid", "label": "Amount Paid", "type": "number", "required": True, "col": 3},
            {"name": "payment_mode", "label": "Payment Mode", "type": "static_select", "required": True, "col": 4, "options": LoanRepayment._meta.get_field("payment_mode").choices},
            {"name": "reference_no", "label": "Reference No", "type": "text", "required": False, "col": 4},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        post_save=_post_loan_repayment,
        datatable_columns=_loan_repayment_columns,
        show_actions=False,
        show_view=True,
    )
)


register_entity(
    EntityConfig(
        name="loan_ledger",
        url_path="loan-ledger",
        verbose_name="Loan Ledger",
        model=LoanLedger,
        form_class=LoanLedgerForm,
        datatable_view=LoanLedgerDataTableView,
        fields=[
            {"name": "loan_account", "label": "Loan Account", "type": "select", "required": True, "col": 4, "url_name": "loan_account_select"},
            {"name": "transaction_type", "label": "Transaction Type", "type": "static_select", "required": True, "col": 4, "options": LoanLedger._meta.get_field("transaction_type").choices},
            {"name": "date", "label": "Date", "type": "date", "required": True, "col": 4},
            {"name": "amount", "label": "Amount", "type": "number", "required": True, "col": 4},
            {"name": "balance_after", "label": "Balance After", "type": "number", "required": True, "col": 4},
            {"name": "reference_type", "label": "Reference Type", "type": "text", "required": False, "col": 2},
            {"name": "reference_id", "label": "Reference Id", "type": "number", "required": False, "col": 2},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=_loan_ledger_columns,
        show_create=False,
        show_actions=False,
        show_view=True,
        reset_defaults={"date": timezone.localdate().isoformat()},
    )
)
