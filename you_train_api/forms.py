from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from you_train_api.models import Exercise, Equipment, TrainingPlan, WorkoutPlan


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': _('Username'),
            'email': _('Email'),
        }

class UserSettingsForm(forms.Form):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('pl', 'Polish'),
    ]
    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
    ]
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, label=_('Language'))
    theme = forms.ChoiceField(choices=THEME_CHOICES, label=_('Theme'), required=False)

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'description', 'muscle_group', 'equipment', 'is_cardio', 'video_url']

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'description', 'resistance']


class TrainingPlanForm(forms.ModelForm):
    class Meta:
        model = TrainingPlan
        fields = ['title', 'description', 'goal', 'is_active']
        widgets = {
            'goal': forms.TextInput(attrs={'placeholder': 'Enter your goal here'}),
        }


class WorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = ['start_date', 'end_date', 'is_cyclic', 'cycle_length']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_cyclic = cleaned_data.get("is_cyclic")
        end_date = cleaned_data.get("end_date")
        cycle_length = cleaned_data.get("cycle_length")

        if is_cyclic:
            if end_date:
                raise forms.ValidationError('Cyclic plans should not have an end date.')
            if not cycle_length:
                raise forms.ValidationError('Cyclic plans must have a cycle length.')
        else:
            if not end_date:
                raise forms.ValidationError('Non-cyclic plans must have an end date.')
            if end_date <= cleaned_data.get("start_date"):
                raise forms.ValidationError('End date must be after the start date.')
            cleaned_data['cycle_length'] = None  # Ensure cycle_length is null for non-cyclic plans

        return cleaned_data