from django.urls import path

from .views import (
    BankBookReportView,
    BalanceSheetReportView,
    CashBookReportView,
    CashFlowReportView,
    ChartOfAccountTreeView,
    ChartParentSelectView,
    DayBookReportView,
    DepreciationEffectReportView,
    GeneralLedgerReportView,
    JournalLedgerAccountSelectView,
    JournalRootAccountSelectView,
    LedgerAccountSelectView,
    ProfitLossReportView,
    TrialBalanceReportView,
)


urlpatterns = [
    path("chart-of-accounts/", ChartOfAccountTreeView.as_view(), name="chart_of_account_tree"),
    path("chart-of-accounts/parent-select/", ChartParentSelectView.as_view(), name="chart_of_account_parent_select"),
    path("ledgers/search-select/", LedgerAccountSelectView.as_view(), name="ledger_account_tree_select"),
    path("journal/root-accounts/select/", JournalRootAccountSelectView.as_view(), name="journal_root_account_select"),
    path("journal/ledgers/select/", JournalLedgerAccountSelectView.as_view(), name="journal_ledger_account_select"),
    path("reports/balance-sheet/", BalanceSheetReportView.as_view(), name="balance_sheet_report"),
    path("reports/profit-loss/", ProfitLossReportView.as_view(), name="profit_loss_report"),
    path("reports/trial-balance/", TrialBalanceReportView.as_view(), name="trial_balance_report"),
    path("reports/depreciation-effect/", DepreciationEffectReportView.as_view(), name="depreciation_effect_report"),
    path("reports/cash-flow/", CashFlowReportView.as_view(), name="cash_flow_report"),
    path("reports/general-ledger/", GeneralLedgerReportView.as_view(), name="general_ledger_report"),
    path("reports/day-book/", DayBookReportView.as_view(), name="day_book_report"),
    path("reports/cash-book/", CashBookReportView.as_view(), name="cash_book_report"),
    path("reports/bank-book/", BankBookReportView.as_view(), name="bank_book_report"),
]
