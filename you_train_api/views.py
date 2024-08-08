from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from django.http import JsonResponse
import calendar
from django.contrib import messages
from django.utils.translation import gettext as _

from you_train_api.choices import MUSCLE_GROUP_CHOICES
from you_train_api.forms import (
    RegisterForm,
    ExerciseForm,
    EquipmentForm,
    TrainingPlanForm,
    WorkoutPlanForm,
    UserProfileForm,
    UserSettingsForm,
    WorkoutForm,
    ExerciseInSegmentForm,
    WorkoutSegmentForm,
    WorkoutInPlanForm,
)
from you_train_api.models import (
    Exercise,
    Equipment,
    TrainingPlan,
    Workout,
    WorkoutSegment,
    ExerciseInSegment,
    WorkoutSession,
    WorkoutPlan,
    WorkoutInPlan,
)


@login_required(login_url="/login")
def home(request):
    now = timezone.now()
    current_year = now.year
    current_month = now.month

    # Get the month and year from query parameters, defaulting to current month and year
    year = request.GET.get("year", current_year)
    month = request.GET.get("month", current_month)

    try:
        year = int(year)
        month = int(month)
    except ValueError:
        year = current_year
        month = current_month

    # Fetch workout sessions for the selected month
    sessions = WorkoutSession.objects.filter(date__year=year, date__month=month)

    # Create a calendar instance and format the month
    cal = calendar.Calendar(firstweekday=6)  # Week starts on Sunday (default)
    month_days = cal.monthdayscalendar(year, month)

    # Build a dictionary of workout sessions by day
    workout_days = {session.date.day for session in sessions}

    # Generate HTML for the calendar
    html_calendar = '<table class="calendar"><thead><tr>'
    for day_name in calendar.day_name:
        html_calendar += f"<th>{day_name[:2]}</th>"
    html_calendar += "</tr></thead><tbody>"

    for week in month_days:
        html_calendar += "<tr>"
        for i, day in enumerate(week):
            day_class = ""
            if i == 6:  # Sunday
                day_class = "weekend"
            elif i == 5:  # Saturday
                day_class = "weekend"

            if day == 0:
                html_calendar += "<td></td>"
            else:
                label = "trening" if day in workout_days else ""
                html_calendar += f'<td class="{day_class}">{day}<br>{label}</td>'
        html_calendar += "</tr>"

    html_calendar += "</tbody></table>"

    # Determine previous and next month
    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1

    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    context = {
        "calendar": html_calendar,
        "month": calendar.month_name[month],
        "year": year,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
    }

    return render(request, "main/home.html", context)


def sign_up(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/home")
    else:
        form = RegisterForm()

    return render(request, "registration/sign_up.html", {"form": form})


@login_required
def account(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, instance=user)
        settings_form = UserSettingsForm(request.POST)
        password_form = PasswordChangeForm(user, request.POST)

        if "update_profile" in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                return redirect("account", user_id=user_id)
        elif "update_settings" in request.POST:
            if settings_form.is_valid():
                # Update user settings here (e.g., save to user profile model or session)
                request.session["language"] = settings_form.cleaned_data["language"]
                request.session["theme"] = settings_form.cleaned_data["theme"]
                return redirect("account", user_id=user_id)
        elif "change_password" in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important!
                return redirect("account", user_id=user_id)
    else:
        profile_form = UserProfileForm(instance=user)
        settings_form = UserSettingsForm(
            initial={
                "language": request.session.get("language", "en"),
                "theme": request.session.get("theme", "light"),
            }
        )
        password_form = PasswordChangeForm(user)

    return render(
        request,
        "you_train_api/account.html",
        {
            "profile_form": profile_form,
            "settings_form": settings_form,
            "password_form": password_form,
            "member_since": user.date_joined,
        },
    )


@login_required(login_url="/login")
def exercise_list(request):
    exercises = Exercise.objects.filter(user=request.user)
    muscle_groups = request.GET.getlist("muscle_group")
    sort_by = request.GET.get("sort_by")
    search_query = request.GET.get("search", "")
    is_cardio = request.GET.get("is_cardio", "off") == "on"
    selected_equipment = request.GET.getlist("equipment")

    if muscle_groups:
        exercises = exercises.filter(muscle_group__in=muscle_groups)

    if search_query:
        exercises = exercises.filter(name__icontains=search_query)

    if is_cardio:
        exercises = exercises.filter(is_cardio=True)

    if selected_equipment:
        exercises = exercises.filter(equipment__name__in=selected_equipment)

    if sort_by:
        exercises = exercises.order_by(sort_by)

    equipment_list = Equipment.objects.all()

    return render(
        request,
        "you_train_api/exercise_list.html",
        {
            "exercises": exercises,
            "selected_muscle_groups": muscle_groups,
            "sort_by": sort_by,
            "search_query": search_query,
            "is_cardio": is_cardio,
            "selected_equipment": selected_equipment,
            "equipment_list": equipment_list,
            "MUSCLE_GROUP_CHOICES": MUSCLE_GROUP_CHOICES,
        },
    )


@login_required(login_url="/login")
def add_exercise(request):
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.user = request.user
            if exercise.is_cardio:
                exercise.muscle_group = "cardio"
            exercise.save()
            return redirect("exercise_list")
    else:
        form = ExerciseForm()

    return render(request, "you_train_api/add_exercise.html", {"form": form})


@login_required(login_url="/login")
def exercise_detail(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)
    return render(request, "you_train_api/exercise_detail.html", {"exercise": exercise})


@login_required(login_url="/login")
def edit_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)

    if request.method == "POST":
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            form.save()
            return redirect("exercise_detail", exercise_id=exercise.id)
    else:
        form = ExerciseForm(instance=exercise)

    return render(
        request,
        "you_train_api/edit_exercise.html",
        {"form": form, "exercise": exercise},
    )


@login_required(login_url="/login")
def delete_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)

    if request.method == "POST":
        exercise.delete()
        return redirect("exercise_list")

    return render(request, "you_train_api/delete_exercise.html", {"exercise": exercise})


@login_required(login_url="/login")
def equipment_list(request):
    if request.method == "POST":
        form = EquipmentForm(request.POST)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.user = request.user
            equipment.save()
            return redirect("equipment_list")
    else:
        form = EquipmentForm()

    equipments = Equipment.objects.filter(user=request.user)
    return render(
        request,
        "you_train_api/equipment_list.html",
        {"equipments": equipments, "form": form},
    )


@login_required
def equipment_exercises(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    exercises = Exercise.objects.filter(equipment=equipment, user=request.user)
    return render(
        request,
        "you_train_api/equipment_exercises.html",
        {"equipment": equipment, "exercises": exercises},
    )


@login_required(login_url="/login")
def training_plan_list(request):
    training_plans = TrainingPlan.objects.filter(
        user=request.user, workout_plan__isnull=False
    )
    active_plan = TrainingPlan.objects.filter(
        user=request.user, workout_plan__isnull=False, is_active=True
    ).first()

    context = {
        "training_plans": training_plans,
        "active_plan": active_plan,
    }
    return render(request, "you_train_api/training_plan_list.html", context)


@login_required(login_url="/login")
def add_training_plan(request):
    print("trainings: ", TrainingPlan.objects.filter(user=request.user))
    if request.method == "POST":
        form = TrainingPlanForm(request.POST)
        if form.is_valid():
            training_plan = form.save(commit=False)
            training_plan.user = request.user
            training_plan.save()
            return redirect("add_workout_plan", training_plan_id=training_plan.id)
    else:
        form = TrainingPlanForm()
    return render(request, "you_train_api/add_training_plan.html", {"form": form})


@login_required(login_url="/login")
def add_workout_plan(request, training_plan_id):
    training_plan = get_object_or_404(
        TrainingPlan, id=training_plan_id, user=request.user
    )
    print("training_plan: ", training_plan)
    print("wortkout plans", WorkoutPlan.objects.all())

    if request.method == "POST":
        form = WorkoutPlanForm(request.POST)
        if form.is_valid():
            workout_plan = form.save(commit=False)
            workout_plan.training_plan = training_plan
            workout_plan.save()
            if request.POST.get("submit_action") == "add_workouts":
                return redirect(
                    "add_workouts_to_plan", training_plan_id=training_plan.id
                )
            return redirect("training_plan_detail", training_plan_id=training_plan.id)
    else:
        form = WorkoutPlanForm()

    return render(
        request,
        "you_train_api/add_workout_plan.html",
        {"form": form, "training_plan": training_plan},
    )


@login_required(login_url="/login")
def workout_search(request):
    query = request.GET.get("query", "")
    workouts = Workout.objects.filter(user=request.user, title__icontains=query)
    workout_list = [{"id": workout.id, "title": workout.title} for workout in workouts]
    return JsonResponse(workout_list, safe=False)


@login_required(login_url="/login")
def training_plan_detail(request, training_plan_id):
    training_plan = get_object_or_404(
        TrainingPlan, id=training_plan_id, user=request.user
    )
    workout_plan = training_plan.workout_plan

    if request.method == "POST":
        if "set_active" in request.POST:
            active_plan = (
                TrainingPlan.objects.filter(user=request.user, is_active=True)
                .exclude(id=training_plan_id)
                .first()
            )

            if active_plan:
                if "confirm" in request.POST:
                    active_plan.is_active = False
                    active_plan.save()

                    training_plan.is_active = True
                    training_plan.save()

                    messages.success(
                        request,
                        f"The plan '{training_plan.title}' is now active. '{active_plan.title}' has been deactivated.",
                    )
                    return redirect(
                        "training_plan_detail", training_plan_id=training_plan_id
                    )
                else:
                    return redirect(f"{request.path}?confirm=true")
            else:
                training_plan.is_active = True
                training_plan.save()
                messages.success(
                    request, f"The plan '{training_plan.title}' is now active."
                )
                return redirect(
                    "training_plan_detail", training_plan_id=training_plan_id
                )

        elif "deactivate" in request.POST:
            training_plan.is_active = False
            training_plan.save()
            messages.success(
                request, f"The plan '{training_plan.title}' has been deactivated."
            )
            return redirect("training_plan_detail", training_plan_id=training_plan_id)

    existing_workouts_in_plan = WorkoutInPlan.objects.filter(workout_plan=workout_plan)
    week_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    return render(
        request,
        "you_train_api/training_plan_detail.html",
        {
            "training_plan": training_plan,
            "workout_plan": workout_plan,
            "existing_workouts_in_plan": existing_workouts_in_plan,
            "week_days": week_days,
            "confirm": "confirm" in request.GET,
        },
    )


def workout_list(request):
    workouts = Workout.objects.filter(user=request.user)
    print(WorkoutSegment.objects.all())
    return render(request, "you_train_api/workout_list.html", {"workouts": workouts})


def workout_detail(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id)
    print(WorkoutSegment.objects.filter(workout=workout))
    return render(request, "you_train_api/workout_detail.html", {"workout": workout})


@login_required(login_url="/login")
def add_workout(request):
    WorkoutSegmentFormSet = inlineformset_factory(
        Workout, WorkoutSegment, form=WorkoutSegmentForm, extra=1, can_delete=True
    )
    ExerciseInSegmentFormSet = inlineformset_factory(
        WorkoutSegment,
        ExerciseInSegment,
        form=ExerciseInSegmentForm,
        extra=1,
        can_delete=True,
    )

    if request.method == "POST":
        workout_form = WorkoutForm(request.POST)
        segment_formset = WorkoutSegmentFormSet(request.POST, prefix="segments")

        if workout_form.is_valid() and segment_formset.is_valid():
            workout = workout_form.save(commit=False)
            workout.user = request.user
            workout.save()

            segments = segment_formset.save(commit=False)
            print("aaaaaaaaa", segments)
            # segmentów nie zapisuje a workout bez ssgtmentu nioe ma prawa bycia
            for segment in segments:
                print(segment)
                segment.workout = workout
                segment.save()

                exercise_formset = ExerciseInSegmentFormSet(
                    request.POST,
                    instance=segment,
                    prefix=f"segment_{segment.pk}_exercises",
                )
                if exercise_formset.is_valid():
                    exercise_formset.save()

            messages.success(request, f'Training "{workout.title}" has been saved!')
            return redirect("workout_list")
    else:
        workout_form = WorkoutForm()
        segment_formset = WorkoutSegmentFormSet(prefix="segments")
        exercise_formsets = [
            ExerciseInSegmentFormSet(
                instance=form.instance, prefix=f"segment_{i}_exercises"
            )
            for i, form in enumerate(segment_formset.forms)
        ]

    return render(
        request,
        "you_train_api/add_workout.html",
        {
            "workout_form": workout_form,
            "segment_formset": segment_formset,
            "exercise_formsets": exercise_formsets,
        },
    )


@login_required(login_url="/login")
def exercise_search(request):
    query = request.GET.get("query", "")
    exercises = Exercise.objects.filter(user=request.user, name__icontains=query)
    exercise_list = [
        {"id": exercise.id, "name": exercise.name} for exercise in exercises
    ]
    return JsonResponse(exercise_list, safe=False)


@login_required(login_url="/login")
def add_workouts_to_plan(request, training_plan_id):
    training_plan = get_object_or_404(
        TrainingPlan, id=training_plan_id, user=request.user
    )
    workout_plan = training_plan.workout_plan

    if request.method == "POST":
        form = WorkoutInPlanForm(request.POST, workout_plan=workout_plan)
        if form.is_valid():
            workout_in_plan = form.save(commit=False)
            workout_in_plan.workout_plan = workout_plan
            if not workout_plan.is_cyclic:
                workout_in_plan.day_of_week = None
            workout_in_plan.save()
            messages.success(request, "Workout added to the plan successfully!")
            if "add_another" in request.POST:
                return redirect(
                    "add_workouts_to_plan", training_plan_id=training_plan.id
                )
            return redirect("training_plan_detail", training_plan_id=training_plan.id)
    else:
        form = WorkoutInPlanForm(workout_plan=workout_plan)

    workouts = Workout.objects.filter(user=request.user)
    existing_workouts_in_plan = WorkoutInPlan.objects.filter(workout_plan=workout_plan)
    week_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    return render(
        request,
        "you_train_api/add_workouts_to_plan.html",
        {
            "form": form,
            "workouts": workouts,
            "training_plan": training_plan,
            "workout_plan": workout_plan,
            "existing_workouts_in_plan": existing_workouts_in_plan,
            "week_days": week_days,
        },
    )


@login_required(login_url="/login")
def delete_training_plan(request, training_plan_id):
    training_plan = get_object_or_404(
        TrainingPlan, id=training_plan_id, user=request.user
    )

    if request.method == "POST":
        # Delete the associated WorkoutPlan, if exists
        if hasattr(training_plan, "workout_plan"):
            training_plan.workout_plan.delete()
        # Delete the TrainingPlan itself
        training_plan.delete()
        return redirect("training_plan_list")

    # If not a POST request, redirect back to the detail page
    return redirect("training_plan_detail", training_plan_id=training_plan_id)


@login_required(login_url="/login")
def edit_workout_in_plan(request, training_plan_id, workout_in_plan_id):
    training_plan = get_object_or_404(
        TrainingPlan, id=training_plan_id, user=request.user
    )
    workout_in_plan = get_object_or_404(WorkoutInPlan, id=workout_in_plan_id)

    if request.method == "POST":
        form = WorkoutInPlanForm(request.POST, instance=workout_in_plan)
        if form.is_valid():
            form.save()
            messages.success(request, "Workout updated successfully!")
            return redirect("training_plan_detail", training_plan_id=training_plan.id)
    else:
        form = WorkoutInPlanForm(instance=workout_in_plan)

    return render(
        request,
        "you_train_api/edit_workout_in_plan.html",
        {
            "form": form,
            "training_plan": training_plan,
            "workout_in_plan": workout_in_plan,
        },
    )
