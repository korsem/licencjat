from django.urls import include, path
from .views import home, sign_up, exercise_list, equipment_list, equipment_exercises

urlpatterns = [
    path('home', home, name='home'),
    path('sign-up', sign_up, name='sign_up'),
    path('exercises/', exercise_list, name='exercise_list'),
    path('equipments/', equipment_list, name='equipment_list'),
    path('equipment/<int:equipment_id>/exercises/', equipment_exercises, name='equipment_exercises'),
]
