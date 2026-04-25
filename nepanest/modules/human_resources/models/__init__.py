from .department import Department
from .designation import Designation
from .employee import Employee
from .employee_access import EmployeeAccess
from .employee_address import EmployeeAddress
from .employee_attendance import EmployeeAttendance
from .employee_bank import EmployeeBank
from .employee_contact import EmployeeContact
from .employee_document import EmployeeDocument
from .employee_emergency import EmployeeEmergency
from .employee_exit import EmployeeExit
from .employee_legal import EmployeeLegal
from .employee_payroll import EmployeePayroll
from .employee_profile import EmployeeProfile
from .employee_shift import EmployeeShift
from .employee_work import EmployeeWork
from .employeement_type import EmploymentType
from .shift import Shift
from .team import Team, TeamMember
from .team_role import TeamRole

from nepanest.modules.attendance import models as attendance_models
from nepanest.modules.attendance.models import *  # noqa: F401,F403
from nepanest.modules.leave import models as leave_models
from nepanest.modules.leave.models import *  # noqa: F401,F403
from nepanest.modules.loans import models as loan_models
from nepanest.modules.loans.models import *  # noqa: F401,F403
from nepanest.modules.payroll import models as payroll_models
from nepanest.modules.payroll.models import *  # noqa: F401,F403
from nepanest.modules.policies import models as policy_models
from nepanest.modules.policies.models import *  # noqa: F401,F403
from nepanest.modules.recruitment import models as recruitment_models
from nepanest.modules.recruitment.models import *  # noqa: F401,F403

__all__ = list(
    dict.fromkeys(
        [
            "Department",
            "Designation",
            "Employee",
            "EmployeeAccess",
            "EmployeeAddress",
            "EmployeeAttendance",
            "EmployeeBank",
            "EmployeeContact",
            "EmployeeDocument",
            "EmployeeEmergency",
            "EmployeeExit",
            "EmployeeLegal",
            "EmployeePayroll",
            "EmployeeProfile",
            "EmployeeShift",
            "EmployeeWork",
            "EmploymentType",
            "Shift",
            "Team",
            "TeamMember",
            "TeamRole",
            *recruitment_models.__all__,
            *leave_models.__all__,
            *attendance_models.__all__,
            *payroll_models.__all__,
            *loan_models.__all__,
            *policy_models.__all__,
        ]
    )
)
