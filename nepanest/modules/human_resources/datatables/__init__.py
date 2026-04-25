from nepanest.modules.leave import datatables as leave_datatables
from nepanest.modules.leave.datatables import *  # noqa: F401,F403
from nepanest.modules.loans import datatables as loan_datatables
from nepanest.modules.loans.datatables import *  # noqa: F401,F403
from nepanest.modules.payroll import datatables as payroll_datatables
from nepanest.modules.payroll.datatables import *  # noqa: F401,F403
from nepanest.modules.policies import datatables as policy_datatables
from nepanest.modules.policies.datatables import *  # noqa: F401,F403
from nepanest.modules.recruitment import datatables as recruitment_datatables
from nepanest.modules.recruitment.datatables import *  # noqa: F401,F403

from .attendance_adjustment_data_table import ATTENDANCE_ADJUSTMENT_COLUMNS, AttendanceAdjustmentDataTableView
from .attendance_data_table import ATTENDANCE_COLUMNS, AttendanceDataTableView
from .department_data_table import DEPARTMENT_COLUMNS, DepartmentDataTableView
from .designation_data_table import DESIGNATION_COLUMNS, DesignationDataTableView
from .employee_data_table import EMPLOYEE_COLUMNS, EmployeeDataTableView
from .employee_shift_data_table import EMPLOYEE_SHIFT_COLUMNS, EmployeeShiftDataTableView
from .employeement_type_data_table import EMPLOYEEMENT_TYPE_COLUMNS, EmploymentTypeDataTableView
from .overtime_record_data_table import OVERTIME_RECORD_COLUMNS, OvertimeRecordDataTableView
from .overtime_request_data_table import OVERTIME_REQUEST_COLUMNS, OvertimeRequestDataTableView
from .shift_data_table import SHIFT_COLUMNS, ShiftDataTableView
from .team_data_table import TEAM_COLUMNS, TeamDataTableView
from .team_role_data_table import TEAM_ROLE_COLUMNS, TeamRoleDataTableView

__all__ = list(
    dict.fromkeys(
        [
            "ATTENDANCE_ADJUSTMENT_COLUMNS",
            "ATTENDANCE_COLUMNS",
            "AttendanceAdjustmentDataTableView",
            "AttendanceDataTableView",
            "DEPARTMENT_COLUMNS",
            "DESIGNATION_COLUMNS",
            "DepartmentDataTableView",
            "DesignationDataTableView",
            "EMPLOYEE_COLUMNS",
            "EMPLOYEE_SHIFT_COLUMNS",
            "EMPLOYEEMENT_TYPE_COLUMNS",
            "EmployeeDataTableView",
            "EmployeeShiftDataTableView",
            "EmploymentTypeDataTableView",
            "OVERTIME_RECORD_COLUMNS",
            "OVERTIME_REQUEST_COLUMNS",
            "OvertimeRecordDataTableView",
            "OvertimeRequestDataTableView",
            "SHIFT_COLUMNS",
            "ShiftDataTableView",
            "TEAM_COLUMNS",
            "TEAM_ROLE_COLUMNS",
            "TeamDataTableView",
            "TeamRoleDataTableView",
            *recruitment_datatables.__all__,
            *leave_datatables.__all__,
            *payroll_datatables.__all__,
            *loan_datatables.__all__,
            *policy_datatables.__all__,
        ]
    )
)
