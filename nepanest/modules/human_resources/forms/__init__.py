from nepanest.modules.leave import forms as leave_forms
from nepanest.modules.leave.forms import *  # noqa: F401,F403
from nepanest.modules.loans import forms as loan_forms
from nepanest.modules.loans.forms import *  # noqa: F401,F403
from nepanest.modules.payroll import forms as payroll_forms
from nepanest.modules.payroll.forms import *  # noqa: F401,F403
from nepanest.modules.policies import forms as policy_forms
from nepanest.modules.policies.forms import *  # noqa: F401,F403
from nepanest.modules.recruitment import forms as recruitment_forms
from nepanest.modules.recruitment.forms import *  # noqa: F401,F403

from .attendance_form import AttendanceAdjustmentForm, AttendanceDashboardForm, AttendanceHistoryReportForm
from .department_form import DepartmentForm
from .designation_form import DesignationForm
from .employee_form import EmployeeForm
from .employee_shift_form import EmployeeShiftForm
from .employeement_type_form import EmploymentTypeForm
from .overtime_form import OvertimeRecordForm, OvertimeRequestForm
from .shift_form import ShiftForm
from .team_form import TeamForm
from .team_role_form import TeamRoleForm

__all__ = list(
    dict.fromkeys(
        [
            "AttendanceAdjustmentForm",
            "AttendanceDashboardForm",
            "AttendanceHistoryReportForm",
            "DepartmentForm",
            "DesignationForm",
            "EmployeeForm",
            "EmployeeShiftForm",
            "EmploymentTypeForm",
            "OvertimeRecordForm",
            "OvertimeRequestForm",
            "ShiftForm",
            "TeamForm",
            "TeamRoleForm",
            *recruitment_forms.__all__,
            *leave_forms.__all__,
            *payroll_forms.__all__,
            *loan_forms.__all__,
            *policy_forms.__all__,
        ]
    )
)
