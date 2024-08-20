from django.urls import include, path
from .pdf_view import generate_training_plan_pdf
from .views import (
    home,
    sign_up,
    exercise_list,
    equipment_list,
    equipment_exercises,
    exercise_detail,
    add_exercise,
    edit_exercise,
    delete_exercise,
    add_training_plan,
    training_plan_detail,
    training_plan_list,
    add_workout_plan,
    account,
    workout_list,
    workout_detail,
    add_workout,
    exercise_search,
    add_workouts_to_plan,
    delete_training_plan,
    edit_workout_in_plan,
    workout_delete,
    workout_session_detail,
    workout_stats_create,
    workout_stats_detail,
    active_plan_detail,
    workout_stats_summary,
    add_segments_to_workout,
    delete_segment,
    delete_equipment,
)

exercise_patterns = [
    path("", exercise_list, name="exercise_list"),
    path("<int:exercise_id>/", exercise_detail, name="exercise_detail"),
    path("<int:exercise_id>/edit/", edit_exercise, name="edit_exercise"),
    path("<int:exercise_id>/delete/", delete_exercise, name="delete_exercise"),
    path("add/", add_exercise, name="add_exercise"),
]

equipment_patterns = [
    path("", equipment_list, name="equipment_list"),
    path(
        "<int:equipment_id>/exercises/", equipment_exercises, name="equipment_exercises"
    ),
    path(
        "delete/<int:equipment_id>/exercises/",
        delete_equipment,
        name="delete_equipment",
    ),
]

training_plan_patterns = [
    path("", training_plan_list, name="training_plan_list"),
    path("add/", add_training_plan, name="add_training_plan"),
    path(
        "<int:training_plan_id>/add_workout_plan/",
        add_workout_plan,
        name="add_workout_plan",
    ),
    path("<int:training_plan_id>/", training_plan_detail, name="training_plan_detail"),
    path(
        "<int:training_plan_id>/add_workouts/",
        add_workouts_to_plan,
        name="add_workouts_to_plan",
    ),
    path(
        "<int:training_plan_id>/<int:workout_in_plan_id>/",
        edit_workout_in_plan,
        name="edit_workout_in_plan",
    ),
    path(
        "<int:training_plan_id>/delete/",
        delete_training_plan,
        name="delete_training_plan",
    ),
    path(
        "<int:training_plan_id>/generate_pdf/",
        generate_training_plan_pdf,
        name="generate_pdf",
    ),
    path(
        "active_plan/",
        active_plan_detail,
        name="active_plan",
    ),
]

workout_patterns = [
    path("", workout_list, name="workout_list"),
    path("add/", add_workout, name="add_workout"),
    path(
        "add/<int:workout_id>/", add_segments_to_workout, name="add_segments_to_workout"
    ),
    path("<int:workout_id>/", workout_detail, name="workout_detail"),
    path("delete_segment/<int:segment_id>", delete_segment, name="delete_segment"),
    path("<int:workout_id>/delete/", workout_delete, name="delete_workout"),
    path(
        "workout_session/<int:session_id>/",
        workout_session_detail,
        name="workout_session_detail",
    ),
    path(
        "workout_stats/<int:session_id>/create/",
        workout_stats_create,
        name="create_workout_stats",
    ),
    path(
        "workout_stats/<int:session_id>",
        workout_stats_detail,
        name="workout_stats_detail",
    ),
    path(
        "workout_stats/",
        workout_stats_summary,
        name="workout_stats_summary",
    ),
]

urlpatterns = [
    path("", home, name="home"),
    path("sign-up/", sign_up, name="sign_up"),
    path("account/<int:user_id>/", account, name="account"),
    path("exercises/", include(exercise_patterns)),
    path("equipments/", include(equipment_patterns)),
    path("training_plans/", include(training_plan_patterns)),
    path("workouts/", include(workout_patterns)),
    path("exercise_search/", exercise_search, name="exercise_search"),
]
