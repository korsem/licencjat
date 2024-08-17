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
    WorkoutSession,
    WorkoutStats,
)
from you_train_api.widgets import HMSTimeField


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
        model = Exercise
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
    rest_time = forms.DurationField(label="Rest Time", required=False)
    reps = forms.IntegerField(
        label="Ile razy blok ma być powtórzony", required=True, min_value=1, initial=1
    )

    class Meta:
        model = WorkoutSegment
        fields = ["reps", "rest_time", "notes"]


class ExerciseInSegmentForm(forms.ModelForm):

    duration = forms.DurationField(label="Duration", required=False)
    rest_time = forms.DurationField(label="Rest Time", required=True)

    class Meta:
        model = ExerciseInSegment
        fields = ["exercise", "reps", "duration", "rest_time", "notes"]

    def clean(self):
        cleaned_data = super().clean()
        reps = cleaned_data.get("reps")
        duration = cleaned_data.get("duration")

        if not reps and not duration:
            raise forms.ValidationError("Either reps or duration must be specified.")
        return cleaned_data


class WorkoutSelectionForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label="Search for workouts")


class WorkoutInPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutInPlan
        fields = ["workout", "day_of_week", "date"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        workout_plan = kwargs.pop("workout_plan", None)
        super().__init__(*args, **kwargs)
        if workout_plan and workout_plan.is_cyclic:
            self.fields["date"].widget = forms.HiddenInput()
        elif workout_plan and not workout_plan.is_cyclic:
            self.fields["day_of_week"].widget = forms.HiddenInput()


class WorkoutSessionForm(forms.ModelForm):
    class Meta:
        model = WorkoutSession
        fields = ["description", "is_completed"]

    def __init__(self, *args, **kwargs):
        super(WorkoutSessionForm, self).__init__(*args, **kwargs)
        self.fields["is_completed"].widget = forms.Select(
            choices=[(True, "Tak"), (False, "Nie")]
        )
        self.fields["is_completed"].label = "Trening ukończony"

        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class WorkoutStatsForm(forms.ModelForm):
    duration = HMSTimeField(label="Czas trwania (HH:MM:SS)", required=False)
    distance = forms.FloatField(label="Dystans (km)", required=False, min_value=0)
    satisfaction = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 11)],
        label="Jak w skali 1-10 jesteś zadowolony z treningu",
    )
    well_being = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 11)],
        label="Jak w skali 1-10 się czujesz po treningu",
    )

    class Meta:
        model = WorkoutStats
        fields = [
            "description",
            "distance",
            "duration",
            "avg_heart_rate",
            "max_heart_rate",
            "satisfaction",
            "well_being",
        ]

    def __init__(self, *args, **kwargs):
        super(WorkoutStatsForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
