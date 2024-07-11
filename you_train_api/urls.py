from django.urls import include, path
from .views import home, sign_up, exercise_list

urlpatterns = [
    path('home', home, name='home'),
    path('sign-up', sign_up, name='sign_up'),
    path('exercises/', exercise_list, name='exercise_list'),
]
