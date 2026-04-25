from nepanest.modules.leave import services as leave_services
from nepanest.modules.leave.services import *  # noqa: F401,F403
from nepanest.modules.loans import services as loan_services
from nepanest.modules.loans.services import *  # noqa: F401,F403
from nepanest.modules.payroll import services as payroll_services
from nepanest.modules.payroll.services import *  # noqa: F401,F403
from nepanest.modules.policies import services as policy_services
from nepanest.modules.policies.services import *  # noqa: F401,F403

from .attendance_report import build_employee_attendance_history_report
from .shift_rotation import current_shift_rotation, resolve_employee_shift

__all__ = list(
    dict.fromkeys(
        [
            "build_employee_attendance_history_report",
            "current_shift_rotation",
            "resolve_employee_shift",
            *leave_services.__all__,
            *payroll_services.__all__,
            *loan_services.__all__,
            *policy_services.__all__,
        ]
    )
)
