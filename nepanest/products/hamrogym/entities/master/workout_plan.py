from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.workout_plan_data_table import WorkoutPlanDataTableView, WORKOUT_PLAN_COLUMNS
from ...forms.workout_plan_form import WorkoutPlanForm
from ...models import WorkoutPlan


register_entity(
    EntityConfig(
        name="workout_plan",
        url_path="workout-plans",
        verbose_name="Workout Plan",
        model=WorkoutPlan,
        form_class=WorkoutPlanForm,
        datatable_view=WorkoutPlanDataTableView,
        template_name="hamrogym/workout_plans/index.html",
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "fitness_goal", "label": "Fitness Goal", "type": "select", "required": False, "col": 6, "url_name": "fitness_goal_select"},
            {"name": "difficulty_level", "label": "Difficulty Level", "type": "static_select", "required": False, "col": 4, "options": WorkoutPlan._meta.get_field("difficulty_level").choices},
            {"name": "duration_week", "label": "Duration (Weeks)", "type": "number", "required": False, "col": 4},
            {"name": "days_per_week", "label": "Days Per Week", "type": "number", "required": False, "col": 4},
        ],
        datatable_columns=(
            [
                {"name": key, "title": key.replace("_", " ").title()}
                for key, _accessor in WORKOUT_PLAN_COLUMNS
                if key != "id"
            ]
            + [
                {
                    "name": "id",
                    "title": "Actions",
                    "orderable": False,
                    "searchable": False,
                    "render": (
                        "function(data,type,row){return renderActionButtons((row && row.id) || data, {"
                        "view: false, "
                        "extra_actions: [{"
                        "label: 'Overview', "
                        "title: 'Open Overview', "
                        "icon_class: 'fas fa-eye', "
                        "class_name: 'btn-outline-dark', "
                        "href_url: '/workout-plans/{id}/'"
                        "}, {"
                        "label: 'Structure', "
                        "title: 'Open Structure Builder', "
                        "icon_class: 'fas fa-sitemap', "
                        "class_name: 'btn-outline-warning', "
                        "href_url: '/workout-plans/{id}/structure/'"
                        "}, {"
                        "label: 'Assign', "
                        "title: 'Assign Plan', "
                        "icon_class: 'fas fa-user-plus', "
                        "class_name: 'btn-outline-success', "
                        "href_url: '/workout-assignments/create/?workout_plan={id}'"
                        "}, {"
                        "label: 'Edit', "
                        "title: 'Edit Plan', "
                        "icon_class: 'fas fa-edit', "
                        "class_name: 'btn-primary', "
                        "href_url: '/workout-plans/{id}/edit/'"
                        "}]"
                        "}, row || {});}"
                    ),
                }
            ]
        ),
        reset_defaults={},
        show_actions=False,
        show_create=False,
        show_view=False,
    )
)
