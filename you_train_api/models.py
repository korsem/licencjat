import calendar
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from you_train_api.choices import MUSCLE_GROUP_CHOICES


class Equipment(models.Model):
    """
    Model określa dostępny dla użytkownika sprzęt sportowy,
    który następnie może łączyć ze znanymi ćwiczeniami
    """

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True)
    resistance = models.FloatField(
        blank=True, null=True, help_text=_("Resistance in kg")
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} {self.resistance} kg" if self.resistance else self.name


class Exercise(models.Model):
    """
    Ćwiczenie w bazie - przykładowo pompki lub pływanie
    """

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True)
    muscle_group = models.CharField(
        max_length=100, blank=True, choices=MUSCLE_GROUP_CHOICES
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.SET_NULL,
        related_name="exercises",
        blank=True,
        null=True,
    )
    is_cardio = models.BooleanField(
        default=False, help_text="Czy ćwiczenie jest cardio?"
    )  # jeśli tak to nie ma reps, tylko duration oraz muscle_group = cardio
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video_url = models.URLField(
        blank=True, help_text="Link do filmiku instruktażowego z ćwiczeniem"
    )

    def __str__(self):
        return self.name


class TrainingPlan(models.Model):
    """
    Podsatawowe parametry określające plan treningowy
    """

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True)
    goal = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=False)  # only one active plan per user
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_active=True),
                name="unique_active_training_plan_per_user",
            )
        ]


class WorkoutPlan(models.Model):
    """
    Model określa w jaki sposób ma być wykonywany dany plan treningowy.
    Jest w reklacji OneToOne z planem treningowym.
    """

    training_plan = models.OneToOneField(
        TrainingPlan, related_name="workout_plan", on_delete=models.CASCADE
    )
    start_date = models.DateField(
        default=timezone.now, help_text="Data rozpoczęcia planu"
    )
    end_date = models.DateField(
        null=True, blank=True, help_text="Data zakończenia planu"
    )  # dla cyklicznego nie musi istnieć
    is_cyclic = models.BooleanField(
        default=False, help_text="Czy powtarza się co tydzień?"
    )  # if true cycle_length is required
    cycle_length = models.PositiveIntegerField(
        null=True, blank=True, help_text="Ile tygodni ma trwać Plan?"
    )

    def clean(self):
        if self.is_cyclic:
            if self.end_date:
                raise ValidationError("Cyclic plans should not have an end date.")
            if not self.cycle_length:
                raise ValidationError("Cyclic plans must have a cycle length.")
        else:
            if not self.end_date:
                raise ValidationError("Non-cyclic plans must have an end date.")
            if self.end_date <= self.start_date:
                raise ValidationError("End date must be after the start date.")
            self.cycle_length = None  # Ensure cycle_length is null for non-cyclic plans

    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation is performed
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.training_plan.title} (cyclic: {self.is_cyclic})"


class WorkoutInPlan(models.Model):
    """
    Model "through" dla relacji ManyToMany modeli Workout i WorkoutPlan.
    Określa dzień danego ćwiczenia w planie.
    """

    workout = models.ForeignKey("Workout", on_delete=models.CASCADE)
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(
        choices=[(i, calendar.day_name[i]) for i in range(7)], blank=True, null=True
    )  # if plan not cyclic then null
    date = models.DateField(
        blank=True, null=True
    )  # Only applicable if plan is not cyclic

    def __str__(self):
        return f"{self.workout_plan} - {self.workout} - {self.id}"


class Workout(models.Model):
    """
    Podstawowe parametry Workout
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True)
    workout_plan = models.ManyToManyField(WorkoutPlan, through="WorkoutInPlan")

    def __str__(self):
        return self.title


class WorkoutSession(models.Model):
    """
    "Realny" Trening na dany dzień, do kalendarza, nie istnieje bez WorkoutPlan,
     workout moze miec kilka workout sessions, workoutsessin nie isnieje bez workout, workout moze byc bez workout session
    """

    description = models.CharField(max_length=300, blank=True)
    date = models.DateField()
    is_completed = models.BooleanField(
        default=False
    )  # jesli jestesmy w dniu danym lub pózniejszym to dopiero można zmienić na True
    workout_plan = models.ForeignKey(
        WorkoutPlan, related_name="sessions", on_delete=models.CASCADE
    )
    workout = models.ForeignKey(
        Workout, related_name="sessions", on_delete=models.CASCADE
    )  # zmienić na workout in plan
    # goal = models.CharField(max_length=100, blank=True) idk czy potrzebne

    def __str__(self):
        return f"{self.date} - {self.workout.title}"


class WorkoutSegment(models.Model):
    """
    Model określa blok treningowy. Dany workout składa się z conajmniej jednego bloku treningowego.
    np jeden blok, a wiele ćwiczeń - siłownia obwodowa,
    """

    workout = models.ForeignKey(
        Workout, related_name="segments", on_delete=models.CASCADE
    )
    reps = models.IntegerField("Ile razy blok ma być powtórzony")
    rest_time = models.DurationField(
        help_text="Czas odpoczynku między seriami", null=True, blank=True
    )
    notes = models.CharField(max_length=300, blank=True)
    exercises = models.ManyToManyField(Exercise, through="ExerciseInSegment")

    def __str__(self):
        return f"{self.workout.title} - segment {self.id}"


class ExerciseInSegment(models.Model):
    """
    Model "through" relacji ManyToMany Exercise i WorkoutSegment.
    Określa w jaki sposób ćwiczenie jest wykonywane w danym bloku treningowym.
    """

    workout_segment = models.ForeignKey(WorkoutSegment, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    reps = models.IntegerField("Ile powtórzeń", blank=True, default=1)
    duration = models.DurationField("Długość ćwiczenia", null=True, blank=True)
    rest_time = models.DurationField(
        help_text="Czas odpoczynku między seriami", blank=True, null=True
    )
    notes = models.CharField(max_length=300, blank=True)


class WorkoutStats(models.Model):
    """
    Statystyki odbytego, gdy workout session jest completed
    """

    workout_session = models.OneToOneField(
        WorkoutSession, on_delete=models.CASCADE
    )  # po ustawieniu workoutsession na clpmeted tworzy się workoutstats
    description = models.CharField(max_length=300, blank=True)
    distance = models.FloatField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)  # moze float?
    avg_heart_rate = models.IntegerField(blank=True, null=True)
    max_heart_rate = models.IntegerField(blank=True, null=True)
    satisfaction = models.IntegerField(blank=True, null=True)  # 1-10 może bez null
    well_being = models.IntegerField(blank=True, null=True)  # 1-10 może bez null

    def __str__(self):
        return f"{self.workout_session} - stats"
