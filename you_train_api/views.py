from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.forms import inlineformset_factory
from django.http import JsonResponse
import calendar
from rest_framework import generics

from you_train_api.choices import MUSCLE_GROUP_CHOICES
from you_train_api.forms import RegisterForm, ExerciseForm, EquipmentForm, TrainingPlanForm, WorkoutPlanForm, \
    UserProfileForm, UserSettingsForm, WorkoutForm, ExerciseInSegmentForm, WorkoutSegmentForm
from you_train_api.models import Exercise, Equipment, TrainingPlan, Workout, WorkoutSegment, ExerciseInSegment
from you_train_api.serializers import ExerciseSerializer


@login_required(login_url="/login")
def home(request):
    now = timezone.now()
    current_year = now.year
    current_month = now.month

    cal = calendar.HTMLCalendar().formatmonth(current_year, current_month)

    return render(request, 'main/home.html', {
        'calendar': cal
    })



def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form": form})


@login_required
def account(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=user)
        settings_form = UserSettingsForm(request.POST)
        password_form = PasswordChangeForm(user, request.POST)

        if 'update_profile' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                return redirect('account', user_id=user_id)
        elif 'update_settings' in request.POST:
            if settings_form.is_valid():
                # Update user settings here (e.g., save to user profile model or session)
                request.session['language'] = settings_form.cleaned_data['language']
                request.session['theme'] = settings_form.cleaned_data['theme']
                return redirect('account', user_id=user_id)
        elif 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important!
                return redirect('account', user_id=user_id)
    else:
        profile_form = UserProfileForm(instance=user)
        settings_form = UserSettingsForm(initial={
            'language': request.session.get('language', 'en'),
            'theme': request.session.get('theme', 'light'),
        })
        password_form = PasswordChangeForm(user)

    return render(request, 'you_train_api/account.html', {
        'profile_form': profile_form,
        'settings_form': settings_form,
        'password_form': password_form,
        'member_since': user.date_joined,
    })

@login_required(login_url="/login")
def exercise_list(request):
    exercises = Exercise.objects.filter(user=request.user)
    muscle_groups = request.GET.getlist('muscle_group')
    sort_by = request.GET.get('sort_by')
    search_query = request.GET.get('search', '')
    is_cardio = request.GET.get('is_cardio', 'off') == 'on'
    selected_equipment = request.GET.getlist('equipment')

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

    return render(request, 'you_train_api/exercise_list.html', {
        'exercises': exercises,
        'selected_muscle_groups': muscle_groups,
        'sort_by': sort_by,
        'search_query': search_query,
        'is_cardio': is_cardio,
        'selected_equipment': selected_equipment,
        'equipment_list': equipment_list,
        'MUSCLE_GROUP_CHOICES': MUSCLE_GROUP_CHOICES,
    })

@login_required(login_url="/login")
def add_exercise(request):
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.user = request.user
            if exercise.is_cardio:
                exercise.muscle_group = 'cardio'
            exercise.save()
            return redirect('exercise_list')
    else:
        form = ExerciseForm()

    return render(request, 'you_train_api/add_exercise.html', {'form': form})


@login_required(login_url="/login")
def exercise_detail(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)
    return render(request, 'you_train_api/exercise_detail.html', {'exercise': exercise})


@login_required(login_url="/login")
def edit_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)

    if request.method == 'POST':
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            form.save()
            return redirect('exercise_detail', exercise_id=exercise.id)
    else:
        form = ExerciseForm(instance=exercise)

    return render(request, 'you_train_api/edit_exercise.html', {'form': form, 'exercise': exercise})


@login_required(login_url="/login")
def delete_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)

    if request.method == 'POST':
        exercise.delete()
        return redirect('exercise_list')

    return render(request, 'you_train_api/delete_exercise.html', {'exercise': exercise})

@login_required(login_url="/login")
def equipment_list(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.user = request.user
            equipment.save()
            return redirect('equipment_list')
    else:
        form = EquipmentForm()

    equipments = Equipment.objects.filter(user=request.user)
    return render(request, 'you_train_api/equipment_list.html', {'equipments': equipments, 'form': form})

@login_required
def equipment_exercises(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    exercises = Exercise.objects.filter(equipment=equipment, user=request.user)
    return render(request, 'you_train_api/equipment_exercises.html', {'equipment': equipment, 'exercises': exercises})

#TODO podzielić na mniejsze pliki - ćwiczenia + sprzęt oraz na elementyu planu treingowego

@login_required(login_url="/login")
def training_plan_list(request):
    training_plans = TrainingPlan.objects.filter(user=request.user, workout_plan__isnull=False)
    active_plan = TrainingPlan.objects.filter(user=request.user, workout_plan__isnull=False, is_active=True).first()

    context = {
        'training_plans': training_plans,
        'active_plan': active_plan,
    }
    return render(request, 'you_train_api/training_plan_list.html', context)


@login_required(login_url="/login")
def add_training_plan(request):
    if request.method == "POST":
        form = TrainingPlanForm(request.POST)
        if form.is_valid():
            training_plan = form.save(commit=False)
            training_plan.user = request.user
            training_plan.save()
            return redirect('add_workout_plan', training_plan_id=training_plan.id)
    else:
        form = TrainingPlanForm()
    return render(request, 'you_train_api/add_training_plan.html', {'form': form})

@login_required(login_url="/login")
def add_workout_plan(request, training_plan_id):
    training_plan = get_object_or_404(TrainingPlan, id=training_plan_id, user=request.user)
    if request.method == "POST":
        form = WorkoutPlanForm(request.POST)
        if form.is_valid():
            workout_plan = form.save(commit=False)
            workout_plan.training_plan = training_plan
            workout_plan.save()
            return redirect('training_plan_detail', training_plan_id=training_plan.id)
    else:
        form = WorkoutPlanForm()
    return render(request, 'you_train_api/add_workout_plan.html', {'form': form, 'training_plan': training_plan})

@login_required(login_url="/login")
def training_plan_detail(request, training_plan_id):
    training_plan = get_object_or_404(TrainingPlan, id=training_plan_id, user=request.user)
    workout_plan = training_plan.workout_plan

    if request.method == 'POST':
        # Change the active training plan
        if 'set_active' in request.POST:
            # Deactivate the current active plan, if any
            TrainingPlan.objects.filter(user=request.user, is_active=True).update(is_active=False)
            # Activate the selected plan
            training_plan.is_active = True
            training_plan.save()
            return redirect('training_plan_detail', training_plan_id=training_plan_id)

    return render(request, 'you_train_api/training_plan_detail.html', {
        'training_plan': training_plan,
        'workout_plan': workout_plan,
    })

def workout_list(request):
    workouts = Workout.objects.filter(user=request.user)
    return render(request, 'you_train_api/workout_list.html', {'workouts': workouts})

def workout_detail(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id)
    return render(request, 'you_train_api/workout_detail.html', {'workout': workout})

@login_required(login_url="/login")
def add_workout(request):
    WorkoutSegmentFormSet = inlineformset_factory(Workout, WorkoutSegment, form=WorkoutSegmentForm, extra=1, can_delete=True)
    ExerciseInSegmentFormSet = inlineformset_factory(WorkoutSegment, ExerciseInSegment, form=ExerciseInSegmentForm, extra=1, can_delete=True)

    if request.method == 'POST':
        workout_form = WorkoutForm(request.POST)
        segment_formset = WorkoutSegmentFormSet(request.POST, prefix='segments')

        if workout_form.is_valid() and segment_formset.is_valid():
            workout = workout_form.save()
            segments = segment_formset.save(commit=False)
            for segment in segments:
                segment.workout = workout
                segment.save()

                exercise_formset = ExerciseInSegmentFormSet(request.POST, instance=segment, prefix=f'segment_{segment.pk}_exercises')

                if exercise_formset.is_valid():
                    exercise_formset.save()

            return redirect('workout_list')
    else:
        workout_form = WorkoutForm()
        segment_formset = WorkoutSegmentFormSet(prefix='segments')

    return render(request, 'you_train_api/add_workout.html', {
        'workout_form': workout_form,
        'segment_formset': segment_formset,
    })


@login_required(login_url="/login")
def exercise_search(request):
    query = request.GET.get('query', '')
    exercises = Exercise.objects.filter(user=request.user, name__icontains=query)
    exercise_list = [{'id': exercise.id, 'name': exercise.name} for exercise in exercises]
    return JsonResponse(exercise_list, safe=False)
