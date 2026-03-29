from django.urls import path

from .views.attendance_report import AttendanceHistoryReportView
from .views.leave_balance_report import LeaveBalanceSummaryReportView
from .views.user_select import user_select


urlpatterns = [
    path("select/users/", user_select, name="user_select"),
    path("reports/attendance-history/", AttendanceHistoryReportView.as_view(), name="attendance_history_report"),
    path("reports/leave-balance-summary/", LeaveBalanceSummaryReportView.as_view(), name="leave_balance_summary_report"),
]
