from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.member_data_table import MEMBER_COLUMNS, MemberDataTableView
from ...forms.member_form import MemberForm
from core.models import PartyIndividualProfile

from ...models import FitnessGoal, Member, MemberProfile


register_entity(
    EntityConfig(
        name="member",
        url_path="members",
        verbose_name="Member",
        model=Member,
        form_class=MemberForm,
        datatable_view=MemberDataTableView,
        fields=[],
        tabs=[
            {
                "key": "party",
                "label": "Party",
                "fields": [
                    {
                        "name": "party_name",
                        "label": "Party Name",
                        "required": True,
                        "col": 6,
                        "type": "text",
                        "placeholder": "Member full name",
                    },
                    {
                        "name": "party_display_name",
                        "label": "Display Name",
                        "type": "text",
                        "required": False,
                        "col": 6,
                        "placeholder": "Optional display name",
                    },
                    {
                        "name": "party_type",
                        "label": "Party Type",
                        "type": "select",
                        "required": True,
                        "col": 4,
                        "url_name": "party_type_select",
                    },
                   
                    {
                        "name": "party_is_active",
                        "label": "Party Active",
                        "type": "checkbox",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "party_remarks",
                        "label": "Party Notes",
                        "type": "textarea",
                        "required": False,
                        "col": 12,
                        "placeholder": "Notes saved to Party master",
                    },
                ],
            },
            {
                "key": "membership",
                "label": "Membership",
                "requires_id": True,
                "fields": [
                    {
                        "name": "member_code",
                        "label": "Member Code",
                        "type": "text",
                        "required": False,
                        "col": 6,
                        "placeholder": "Auto-generated if left blank",
                    },
                    {
                        "name": "join_date",
                        "label": "Join Date",
                        "type": "date",
                        "required": True,
                        "col": 4,
                        "calendar_switchable": False,
                        "calendar_mode": "ad",
                    },
                    {
                        "name": "status",
                        "label": "Status",
                        "type": "select",
                        "required": True,
                        "col": 4,
                        "url_name": "member_status_select",
                    },
                    {
                        "name": "branch",
                        "label": "Branch",
                        "type": "select",
                        "required": True,
                        "col": 4,
                        "url_name": "branch_select",
                    },
                    {
                        "name": "emergency_contact_name",
                        "label": "Emergency Contact Name",
                        "type": "text",
                        "required": False,
                        "col": 6,
                    },
                    {
                        "name": "emergency_contact_phone",
                        "label": "Emergency Contact Phone",
                        "type": "text",
                        "required": False,
                        "col": 6,
                    },
                    {
                        "name": "remarks",
                        "label": "Notes",
                        "type": "textarea",
                        "required": False,
                        "col": 12,
                        "placeholder": "Notes saved to Member record",
                    },
                ],
            },
            {
                "key": "profile",
                "label": "Profile",
                "requires_id": True,
                "fields": [
                    {
                        "name": "date_of_birth",
                        "label": "Date of Birth",
                        "type": "date",
                        "required": False,
                        "col": 4,
                        "calendar_switchable": False,
                        "calendar_mode": "ad",
                    },
                    {
                        "name": "gender",
                        "label": "Gender",
                        "type": "static_select",
                        "required": False,
                        "col": 4,
                        "options": [("", "Select Gender"), *PartyIndividualProfile.GENDER_CHOICES],
                    },
                    {
                        "name": "fitness_goals",
                        "label": "Fitness Goals",
                        "type": "checkbox_table",
                        "required": False,
                        "col": 12,
                        "options": lambda _request=None: [
                            {
                                "value": goal.pk,
                                "label": goal.name,
                                "code": goal.code,
                                "remarks": goal.remarks,
                            }
                            for goal in FitnessGoal.objects.order_by("name")
                        ],
                    },
                    {
                        "name": "activity_level",
                        "label": "Activity Level",
                        "type": "select",
                        "required": False,
                        "col": 4,
                        "url_name": "activity_level_select",
                    },
                    {
                        "name": "height",
                        "label": "Height",
                        "type": "number",
                        "required": False,
                        "col": 3,
                        "step": "0.01",
                        "min": 0,
                    },
                    {
                        "name": "weight",
                        "label": "Weight",
                        "type": "number",
                        "required": False,
                        "col": 3,
                        "step": "0.01",
                        "min": 0,
                    },
                    {
                        "name": "bmi",
                        "label": "BMI",
                        "type": "number",
                        "required": False,
                        "col": 3,
                        "step": "0.01",
                        "min": 0,
                    },
                    {
                        "name": "body_fat_percentage",
                        "label": "Body Fat %",
                        "type": "number",
                        "required": False,
                        "col": 3,
                        "step": "0.01",
                        "min": 0,
                    },
                    {
                        "name": "photo",
                        "label": "Photo",
                        "type": "file",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "medical_conditions",
                        "label": "Medical Conditions",
                        "type": "textarea",
                        "required": False,
                        "col": 6,
                    },
                    {
                        "name": "injuries",
                        "label": "Injuries",
                        "type": "textarea",
                        "required": False,
                        "col": 6,
                    },
                ],
            },
        ],
        datatable_columns=[
            {
                "name": key,
                "title": key.replace("_", " ").title() if key != "party" else "Party",
            }
            for key, _accessor in MEMBER_COLUMNS
            if key != "id"
        ],
        reset_defaults={"party_is_active": True},
        select_search_fields=["member_code", "party__name", "party__display_name", "branch__name"],
        select_label_func=lambda obj: f"{obj.member_code} - {obj.party.display_name or obj.party.name}",
    )
)
