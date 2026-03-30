from django.urls import path

from .views.attendance_report import AttendanceHistoryReportView
from .views.calendar_holidays import HolidayCalendarDatesView
from .views.holiday_calendar_view import HolidayCalendarView
from .views.leave_balance_report import LeaveBalanceSummaryReportView
from .views.user_select import user_select


urlpatterns = [
    path("select/users/", user_select, name="user_select"),
    path("calendar/holidays/", HolidayCalendarDatesView.as_view(), name="calendar_holiday_dates"),
    path("holiday-calendar/", HolidayCalendarView.as_view(), name="holiday_calendar_view"),
    path("reports/attendance-history/", AttendanceHistoryReportView.as_view(), name="attendance_history_report"),
    path("reports/leave-balance-summary/", LeaveBalanceSummaryReportView.as_view(), name="leave_balance_summary_report"),
]
