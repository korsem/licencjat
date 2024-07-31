from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from you_train_api.models import (
    Exercise,
    Equipment,
    TrainingPlan,
    WorkoutPlan,
    Workout,
    WorkoutSegment,
    ExerciseInSegment,
    WorkoutInPlan,
)
from you_train_api.widgets import HMSTimeField, MSTimeField


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
        labels = {
            "username": _("Username"),
            "email": _("Email"),
        }


class UserSettingsForm(forms.Form):
    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("pl", "Polish"),
    ]
    THEME_CHOICES = [
        ("light", "Light Mode"),
        ("dark", "Dark Mode"),
    ]
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, label=_("Language"))
    theme = forms.ChoiceField(choices=THEME_CHOICES, label=_("Theme"), required=False)


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise  # jeslik is_cardio to muscle group plus duration
        fields = [
            "name",
            "description",
            "muscle_group",
            "equipment",
            "is_cardio",
            "video_url",
        ]


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ["name", "description", "resistance"]


class TrainingPlanForm(forms.ModelForm):
    class Meta:
        model = TrainingPlan
        fields = ["title", "description", "goal", "is_active"]
        widgets = {
            "goal": forms.TextInput(attrs={"placeholder": "Enter your goal here"}),
        }


class WorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = ["start_date", "end_date", "is_cyclic", "cycle_length"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_cyclic = cleaned_data.get("is_cyclic")
        end_date = cleaned_data.get("end_date")
        cycle_length = cleaned_data.get("cycle_length")

        if is_cyclic:
            if end_date:
                raise forms.ValidationError("Cyclic plans should not have an end date.")
            if not cycle_length:
                raise forms.ValidationError("Cyclic plans must have a cycle length.")
        else:
            if not end_date:
                raise forms.ValidationError("Non-cyclic plans must have an end date.")
            if end_date <= cleaned_data.get("start_date"):
                raise forms.ValidationError("End date must be after the start date.")
            cleaned_data["cycle_length"] = (
                None  # Ensure cycle_length is null for non-cyclic plans
            )

        return cleaned_data


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ["title", "description"]


class WorkoutSegmentForm(forms.ModelForm):
    rest_time = MSTimeField(label="Rest Time", required=True)
    reps = forms.IntegerField(
        label="Ile razy blok ma być powtórzony", required=True, min_value=1, initial=1
    )

    class Meta:
        model = WorkoutSegment
        fields = ["reps", "rest_time", "notes"]

    def clean(self):
        cleaned_data = super().clean()
        reps = cleaned_data.get("reps")
        rest_time = cleaned_data.get("rest_time")

        if reps is None or rest_time is None:
            raise forms.ValidationError("Both reps and rest time are required.")


class ExerciseInSegmentForm(forms.ModelForm):

    duration = HMSTimeField(label="Duration", required=False)
    rest_time = MSTimeField(label="Rest Time", required=True)

    class Meta:
        model = ExerciseInSegment
        fields = ["exercise", "reps", "duration", "rest_time", "notes"]

    def clean(self):
        cleaned_data = super().clean()
        reps = cleaned_data.get("reps")
        duration = cleaned_data.get("duration")

        if not reps and not duration:
            raise forms.ValidationError("Either reps or duration must be specified.")


class WorkoutSelectionForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label="Search for workouts")


class WorkoutInPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutInPlan
        fields = ["workout", "day_of_week"]
