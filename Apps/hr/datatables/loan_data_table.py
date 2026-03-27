from core.datatables.views import BaseDataTableView
from core.helpers.helper import encode_date_for_display, encode_datetime_for_display

from ..models import LoanAccount, LoanApplication, LoanDisbursement, LoanInstallment, LoanLedger, LoanRepayment


LOAN_APPLICATION_COLUMNS = [
    ("id", "id"),
    ("employee", lambda obj: str(obj.employee)),
    ("loan_type", lambda obj: str(obj.loan_type)),
    ("requested_amount", "requested_amount"),
    ("requested_tenure", "requested_tenure"),
    ("status", "status"),
    ("applied_date", lambda obj, request: encode_datetime_for_display(obj.applied_date, request)),
    ("approved_date", lambda obj, request: encode_datetime_for_display(obj.approved_date, request)),
]

LOAN_ACCOUNT_COLUMNS = [
    ("id", "id"),
    ("employee", lambda obj: str(obj.employee)),
    ("loan_type", lambda obj: str(obj.loan_type)),
    ("principal_amount", "principal_amount"),
    ("interest_rate", "interest_rate"),
    ("tenure_months", "tenure_months"),
    ("emi_amount", "emi_amount"),
    ("start_date", lambda obj, request: encode_date_for_display(obj.start_date, request)),
    ("end_date", lambda obj, request: encode_date_for_display(obj.end_date, request)),
    ("outstanding_balance", "outstanding_balance"),
    ("status", "status"),
]

LOAN_INSTALLMENT_COLUMNS = [
    ("id", "id"),
    ("loan_account", lambda obj: str(obj.loan_account)),
    ("installment_no", "installment_no"),
    ("due_date", lambda obj, request: encode_date_for_display(obj.due_date, request)),
    ("principal_amount", "principal_amount"),
    ("interest_amount", "interest_amount"),
    ("total_amount", "total_amount"),
    ("paid_amount", "paid_amount"),
    ("balance_amount", "balance_amount"),
    ("status", "status"),
]

LOAN_DISBURSEMENT_COLUMNS = [
    ("id", "id"),
    ("loan_account", lambda obj: str(obj.loan_account)),
    ("amount", "amount"),
    ("disbursed_date", lambda obj, request: encode_date_for_display(obj.disbursed_date, request)),
    ("payment_mode", "payment_mode"),
    ("reference_no", "reference_no"),
]

LOAN_REPAYMENT_COLUMNS = [
    ("id", "id"),
    ("loan_installment", lambda obj: str(obj.loan_installment)),
    ("payment_date", lambda obj, request: encode_date_for_display(obj.payment_date, request)),
    ("amount_paid", "amount_paid"),
    ("payment_mode", "payment_mode"),
    ("reference_no", "reference_no"),
]

LOAN_LEDGER_COLUMNS = [
    ("id", "id"),
    ("loan_account", lambda obj: str(obj.loan_account)),
    ("transaction_type", "transaction_type"),
    ("amount", "amount"),
    ("balance_after", "balance_after"),
    ("reference_type", "reference_type"),
    ("reference_id", "reference_id"),
    ("date", lambda obj, request: encode_date_for_display(obj.date, request)),
]


class LoanApplicationDataTableView(BaseDataTableView):
    model = LoanApplication
    columns = LOAN_APPLICATION_COLUMNS
    searchable_columns = ["employee__employee_id", "employee__user__first_name", "employee__user__last_name", "loan_type__name", "loan_type__code", "status", "reason", "remarks"]
    orderable_columns = ["employee__employee_id", "loan_type__name", "requested_amount", "requested_tenure", "status", "applied_date"]


class LoanAccountDataTableView(BaseDataTableView):
    model = LoanAccount
    columns = LOAN_ACCOUNT_COLUMNS
    searchable_columns = ["employee__employee_id", "employee__user__first_name", "employee__user__last_name", "loan_type__name", "status", "remarks"]
    orderable_columns = ["employee__employee_id", "loan_type__name", "principal_amount", "emi_amount", "start_date", "end_date", "outstanding_balance", "status"]


class LoanInstallmentDataTableView(BaseDataTableView):
    model = LoanInstallment
    columns = LOAN_INSTALLMENT_COLUMNS
    searchable_columns = ["loan_account__employee__employee_id", "loan_account__loan_type__name", "status"]
    orderable_columns = ["loan_account__employee__employee_id", "installment_no", "due_date", "total_amount", "paid_amount", "status"]


class LoanDisbursementDataTableView(BaseDataTableView):
    model = LoanDisbursement
    columns = LOAN_DISBURSEMENT_COLUMNS
    searchable_columns = ["loan_account__employee__employee_id", "loan_account__loan_type__name", "payment_mode", "reference_no", "remarks"]
    orderable_columns = ["loan_account__employee__employee_id", "disbursed_date", "amount", "payment_mode"]


class LoanRepaymentDataTableView(BaseDataTableView):
    model = LoanRepayment
    columns = LOAN_REPAYMENT_COLUMNS
    searchable_columns = ["loan_installment__loan_account__employee__employee_id", "loan_installment__loan_account__loan_type__name", "payment_mode", "reference_no", "remarks"]
    orderable_columns = ["loan_installment__loan_account__employee__employee_id", "payment_date", "amount_paid", "payment_mode"]


class LoanLedgerDataTableView(BaseDataTableView):
    model = LoanLedger
    columns = LOAN_LEDGER_COLUMNS
    searchable_columns = ["loan_account__employee__employee_id", "loan_account__loan_type__name", "transaction_type", "reference_type", "remarks"]
    orderable_columns = ["loan_account__employee__employee_id", "date", "transaction_type", "amount", "balance_after"]
