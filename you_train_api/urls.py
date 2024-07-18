from django.urls import include, path
from .views import home, sign_up, exercise_list, equipment_list, equipment_exercises, exercise_detail, add_exercise, \
    edit_exercise, delete_exercise, add_training_plan, training_plan_detail, training_plan_list, add_workout_plan, \
    account, workout_list, workout_detail, add_workout, exercise_search

exercise_patterns = [
    path('', exercise_list, name='exercise_list'),
    path('<int:exercise_id>/', exercise_detail, name='exercise_detail'),
    path('<int:exercise_id>/edit/', edit_exercise, name='edit_exercise'),
    path('<int:exercise_id>/delete/', delete_exercise, name='delete_exercise'),
    path('add/', add_exercise, name='add_exercise'),
]

equipment_patterns = [
    path('', equipment_list, name='equipment_list'),
    path('<int:equipment_id>/exercises/', equipment_exercises, name='equipment_exercises'),
]

training_plan_patterns = [
    path('', training_plan_list, name='training_plan_list'),
    path('add/', add_training_plan, name='add_training_plan'),
    path('<int:training_plan_id>/add_workout_plan/', add_workout_plan, name='add_workout_plan'),
    path('<int:training_plan_id>/', training_plan_detail, name='training_plan_detail'),
]

urlpatterns = [
    path('', home, name='home'),
    path('sign-up/', sign_up, name='sign_up'),
    path('account/<int:user_id>/', account, name='account'),
    path('exercises/', include(exercise_patterns)),
    path('equipments/', include(equipment_patterns)),
    path('training_plans/', include(training_plan_patterns)),
    path('workouts/', workout_list, name='workout_list'),
    path('workouts/<int:workout_id>/', workout_detail, name='workout_detail'),
    path('workouts/add/', add_workout, name='add_workout'),
    path('exercise_search/', exercise_search, name='exercise_search'),
]