# from core.config import EntityConfig
# from core.registry import register_entity
# from ...datatables.membership_freeze_data_table import MembershipFreezeDataTableView, MEMBERSHIP_FREEZE_COLUMNS
# from ...forms.membership_freeze_form import MembershipFreezeForm
# from ...models import MembershipFreeze


# register_entity(
#     EntityConfig(
#         name="membership_freeze",
#         url_path="membership-freeze",
#         verbose_name="Membership Freeze",
#         model=MembershipFreeze,
#         form_class=MembershipFreezeForm,
#         datatable_view=MembershipFreezeDataTableView,
#         fields=[
#             # TODO: define fields
#             # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
#         ],
#         datatable_columns=[
#             {"name": key, "title": key.replace("_", " ").title()}
#             for key, _accessor in MEMBERSHIP_FREEZE_COLUMNS
#             if key != "id"
#         ],
#         reset_defaults={},
#     )
# )
