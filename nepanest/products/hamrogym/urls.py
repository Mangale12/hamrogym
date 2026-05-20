from django.urls import path
from django.views.generic import RedirectView

from nepanest.products.hamrogym.views import views

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="dashboard", permanent=False)),
    path("product/hamrogym/dashboard/", views.dashboard, name="dashboard"),
    path("class-schedules/<int:pk>/view/", views.ClassScheduleDetailView.as_view(), name="hamrogym_class_schedule_view"),
    path("workout-plans/", RedirectView.as_view(pattern_name="workout_plan_list", permanent=False), name="hamrogym_workout_plan_list"),
    path("workout-plans/create/", views.WorkoutPlanCreateView.as_view(), name="hamrogym_workout_plan_create"),
    path("workout-plans/<int:pk>/", views.WorkoutPlanDetailView.as_view(), name="hamrogym_workout_plan_detail"),
    path("workout-plans/<int:pk>/edit/", views.WorkoutPlanUpdateView.as_view(), name="hamrogym_workout_plan_edit"),
    path(
        "workout-plans/<int:pk>/structure/",
        views.WorkoutPlanDetailView.as_view(),
        {"tab": "structure"},
        name="hamrogym_workout_plan_structure",
    ),
    path(
        "workout-plans/<int:pk>/structure/weeks/add/",
        views.WorkoutWeekCreateView.as_view(),
        name="hamrogym_workout_week_create",
    ),
    path(
        "workout-plans/<int:pk>/structure/weeks/<int:week_id>/delete/",
        views.WorkoutWeekDeleteView.as_view(),
        name="hamrogym_workout_week_delete",
    ),
    path(
        "workout-plans/<int:pk>/structure/weeks/<int:week_id>/days/add/",
        views.WorkoutDayCreateView.as_view(),
        name="hamrogym_workout_day_create",
    ),
    path(
        "workout-plans/<int:pk>/structure/days/<int:day_id>/delete/",
        views.WorkoutDayDeleteView.as_view(),
        name="hamrogym_workout_day_delete",
    ),
    path(
        "workout-plans/<int:pk>/structure/days/<int:day_id>/exercises/add/",
        views.WorkoutExerciseCreateView.as_view(),
        name="hamrogym_workout_exercise_create",
    ),
    path(
        "workout-plans/<int:pk>/structure/exercises/<int:exercise_id>/delete/",
        views.WorkoutExerciseDeleteView.as_view(),
        name="hamrogym_workout_exercise_delete",
    ),
    path(
        "workout-assignments/create/",
        views.WorkoutAssignmentCreateView.as_view(),
        name="hamrogym_workout_assignment_create",
    ),
    path(
        "workout-logs/create/",
        views.WorkoutLogCreateView.as_view(),
        name="hamrogym_workout_log_create",
    ),
    path(
        "product/hamrogym/members/available-parties/",
        views.member_available_party_select,
        name="member_available_party_select",
    ),
]
