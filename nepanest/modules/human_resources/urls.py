from django.urls import path

from nepanest.modules.attendance.views import AttendanceHistoryReportView
from nepanest.modules.leave.views import (
    HolidayCalendarDatesView,
    HolidayCalendarView,
    LeaveBalanceSummaryReportView,
)

from .views.user_select import user_select


urlpatterns = [
    path("select/users/", user_select, name="user_select"),
    path("calendar/holidays/", HolidayCalendarDatesView.as_view(), name="calendar_holiday_dates"),
    path("holiday-calendar/", HolidayCalendarView.as_view(), name="holiday_calendar_view"),
    path("reports/attendance-history/", AttendanceHistoryReportView.as_view(), name="attendance_history_report"),
    path("reports/leave-balance-summary/", LeaveBalanceSummaryReportView.as_view(), name="leave_balance_summary_report"),
]
