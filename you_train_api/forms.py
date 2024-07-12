from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from you_train_api.models import Exercise, Equipment


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'description', 'muscle_group', 'equipment', 'is_cardio', 'video_url']

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'description', 'resistance']