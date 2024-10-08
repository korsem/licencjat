from datetime import datetime, timedelta

from django.contrib.auth.models import User
from you_train_api.models import WorkoutSession, WorkoutInPlan, TrainingPlan


def get_polish_day_of_week(day: int) -> str:
    """
    Args:
        day: int (0-6)
    Returns the name of the day of the week in Polish.
    """
    days = {
        0: "poniedziałek",
        1: "wtorek",
        2: "środa",
        3: "czwartek",
        4: "piątek",
        5: "sobota",
        6: "niedziela",
    }
    return days[day]


def get_active_workout_plan_for_user(user: User):
    """
    Args:
        user: User
    Returns the active TrainingPlan for a given user.
    """
    if not TrainingPlan.objects.filter(user=user, is_active=True).exists():
        return None
    return TrainingPlan.objects.get(user=user, is_active=True).workout_plan


def get_first_workout_day(start_date, week_day) -> datetime.date:
    """
    Args:
        start_date: datetime.date
        week_day: int (0-6)
    Returns the date of the first occurrence of a given week day after a given date.
    """
    days_ahead = week_day - start_date.weekday()
    if days_ahead <= 0:  # Target day already happened this week or today.
        days_ahead += 7
    return start_date + timedelta(days=days_ahead)


def get_monday_date(date: datetime.date) -> datetime.date:
    """
    Args:
        date: datetime.date
    Returns the date of the Monday of the week in which the given date is.
    """
    return date - timedelta(days=date.weekday())


def create_workout_sessions(workout_in_plan: WorkoutInPlan) -> None:
    """ "
    Args:
        workout_in_plan: WorkoutInPlan

    Funkcja tworząca sesje treningowe na podstawie modelu WorkoutInPlan.
    Powinna być wywoływana przy tworzeniu lub aktualizacji danego WorkoutInPlan.
    Przy aktualizacji, usuwa wszystkie WorkoutSession związane z danym WorkoutInPlan,
    od dnia aktualnego, minione WorkoutSessions pozostają nienaruszone.
    """

    if workout_in_plan.workout_plan.is_cyclic:
        workout_first_day = get_first_workout_day(
            workout_in_plan.workout_plan.start_date, workout_in_plan.day_of_week
        )

        for i in range(0, workout_in_plan.workout_plan.cycle_length):
            WorkoutSession.objects.create(  # można bulkowo
                date=workout_first_day + timedelta(weeks=i),
                workout_plan=workout_in_plan.workout_plan,
                is_completed=False,
                workout=workout_in_plan.workout,
            )
    else:
        WorkoutSession.objects.create(
            date=workout_in_plan.date,
            workout_plan=workout_in_plan.workout_plan,
            is_completed=False,
            workout=workout_in_plan.workout,
        )
