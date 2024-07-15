from django.urls import include, path
from .views import home, sign_up, exercise_list, equipment_list, equipment_exercises, exercise_detail, add_exercise, \
    edit_exercise, delete_exercise

urlpatterns = [
    path('home', home, name='home'),
    path('sign-up', sign_up, name='sign_up'),
    path('exercises/', exercise_list, name='exercise_list'),
    path('exercises/<int:exercise_id>/', exercise_detail, name='exercise_detail'),
   path('exercises/<int:exercise_id>/edit/', edit_exercise, name='edit_exercise'),
    path('exercises/<int:exercise_id>/delete/', delete_exercise, name='delete_exercise'),
    path('exercises/add/', add_exercise, name='add_exercise'),
    path('equipments/', equipment_list, name='equipment_list'),
    path('equipment/<int:equipment_id>/exercises/', equipment_exercises, name='equipment_exercises'),
]
