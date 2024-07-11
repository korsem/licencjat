import calendar

from django.db import models
from django.utils.translation import gettext as _

from you_train_api.choices import MUSCLE_GROUP_CHOICES, EQUIPMENT_CHOICES


class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Equipment(models.Model):
    '''
    ciężar do sprzętu, może po prostu zrobić nazwe choices i dodać do Exercise
    umożliwiłoby to wyszukiwanie treningów i ćwiczeń po sprzęcie i dodawanie sprzętów posiadanych przez użytkownika
    '''
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=300, blank=True)
    resistance = models.FloatField(blank=True, null=True, help_text=_("Resistance in kg"))

    def __str__(self):
        return self.name

class Exercise(models.Model):
    '''
    user musi mięc możliwość dodania własnych ćwiczeń i zarządzania nimi, filtrowania itp
    '''
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True)
    muscle_group = models.CharField(max_length=100, blank=True, choices=MUSCLE_GROUP_CHOICES) # dodać choices
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, related_name='exercises', blank=True, null=True)
    is_cardio = models.BooleanField(default=False, help_text="Czy ćwiczenie jest cardio?") # jeśli tak to nie ma reps, tylko duration oraz muscle_group = cardio
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video_url = models.URLField(blank=True, help_text="Link do filmiku instruktażowego z ćwiczeniem")

    def __str__(self):
        return self.name

class TrainingPlan(models.Model):
    '''
    Plan treningowy ogólnie
    '''
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False) # only one active plan per user
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], condition=models.Q(is_active=True),
                                    name='unique_active_training_plan_per_user')
        ]

class WorkoutPlan(models.Model):
    '''
    Określa czy plan treningowy przebiega cyklicznie, jeśli tak to jak często (cyklicznie - poki co po tygodniu)
    Jeśli nie cyklicznie to dany dzień jest pustą karta i customowo możn sobie ją wypełnić.
    TrainingPlan nie może istnieć bez workoutplan a WorkoutPlan bez training plan, sa OneToOne
    '''
    training_plan = models.OneToOneField(TrainingPlan, related_name='workout_plan', on_delete=models.CASCADE)
    is_cyclic = models.BooleanField(default=False, help_text="Czy powtarza się co tydzień?") # if true cycle_number is required
    cycle_length = models.PositiveIntegerField(default=1, help_text="Ile tygodni ma trwać Plan?") # one cycle - one week

    def __str__(self):
        return f"{self.training_plan.title} (cyclic: {self.is_cyclic})"

class Workout(models.Model):
    '''
    Karta treningowa, z ćwiczeniami, do danego dnia, do danego planu treningowego, jako dict
    '''
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True)
    day_of_week = models.IntegerField(choices=[(i, calendar.day_name[i]) for i in range(7)], blank=True, null=True) # if plan not cyclic then null
    workout_plan = models.ForeignKey(WorkoutPlan, related_name='workouts', on_delete=models.CASCADE) # czy na pewno?

    def __str__(self):
        return self.title

class WorkoutSession(models.Model):
    '''
    "Realny" Trening na dany dzień, do kalendarza, ne istnieje bez WorkoutPlan,
     workout moze miec kilka workout sessions, workoutsessin nie isnieje bez workout, workout moze byc bez workout session
    '''
    description = models.CharField(max_length=300, blank=True)
    date = models.DateField()
    is_completed = models.BooleanField(default=False) # jesli jestesmy w dniu danym lub pózniejszym to dopiero można zmienić na True
    workout_plan = models.ForeignKey(WorkoutPlan, related_name='sessions', on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, related_name='sessions', on_delete=models.CASCADE)
    # goal = models.CharField(max_length=100, blank=True) idk czy potrzebne

    def __str__(self):
        return f"{self.date} - {self.workout.title}"

class WorkoutSegment(models.Model):
    '''
    blok treningowy. Jeden blok, a wiele ćwiczeń - siłownia obwodowa,
    musi być we throoug opisany w jaki sposób odbywają sie ćwizenia tzn czy cwiczenie jest po czasie, po ilości powtórzeń, po dystansie,
    domyslnie jak sa sa opisywanie w workout segment
    '''
    workout = models.ForeignKey(Workout, related_name='seggments', on_delete=models.CASCADE)
    reps = models.IntegerField("Ile razy blok ma być powtórzony")
    rest_time = models.DurationField(help_text="Czas odpoczynku między seriami")
    notes = models.CharField(max_length=300, blank=True)
    excercises = models.ManyToManyField(Exercise, through='ExcerciseInSegment')

    def __str__(self):
        return f"{self.workout.title} - segment {self.id}"

class ExcerciseInSegment(models.Model):
    '''
    ćwiczenie w bloku treningowym, z opisem jak ma być wykonane
    '''
    workout_segment = models.ForeignKey(WorkoutSegment, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    reps = models.IntegerField("Ile powtórzeń", blank=True, default=1)
    duration = models.DurationField("Długość ćwiczenia", null=True, blank=True) # ćwiczenie może być alpo po reps albo po durations
    rest_time = models.DurationField(help_text="Czas odpoczynku między seriami", blank=True, null=True)
    notes = models.CharField(max_length=300, blank=True)

class WorkoutStats(models.Model):
    '''
    Statystyki odbytego, gdy workout session jest completed
    '''
    workout_session = models.OneToOneField(WorkoutSession, on_delete=models.CASCADE) # po ustawieniu workoutsession na clpmeted tworzy się workoutstats
    description = models.CharField(max_length=300, blank=True)
    distance = models.FloatField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True) # moze float?
    avg_heart_rate = models.IntegerField(blank=True, null=True)
    max_heart_rate = models.IntegerField(blank=True, null=True)
    satisfaction = models.IntegerField(blank=True, null=True) # 1-10 może bez null
    well_being = models.IntegerField(blank=True, null=True) # 1-10 może bez null

    def __str__(self):
        return f"{self.workout_session} - stats"
