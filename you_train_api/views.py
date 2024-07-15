from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from rest_framework import generics

from you_train_api.choices import MUSCLE_GROUP_CHOICES
from you_train_api.forms import RegisterForm, ExerciseForm, EquipmentForm
from you_train_api.models import Exercise, Equipment
from you_train_api.serializers import ExerciseSerializer


@api_view(['GET'])
def home(request):
    return render(request, 'main/home.html')

@login_required(login_url="/login")
def home(request):
    exercises = Exercise.objects.all()
    print(exercises)
    if request.method == "POST":
        exercise_id = request.POST.get("exercise-id")
        user_id = request.POST.get("user-id")

        if exercise_id:
            exercise = Exercise.objects.filter(id=exercise_id).first()
            if exercise and (exercise.author == request.user or request.user.has_perm("main.delete_exercise")):
                exercise.delete()
        elif user_id:
            user = User.objects.filter(id=user_id).first()
            if user and request.user.is_staff:
                try:
                    group = Group.objects.get(name='default')
                    group.user_set.remove(user)
                except:
                    pass

                try:
                    group = Group.objects.get(name='mod')
                    group.user_set.remove(user)
                except:
                    pass

    return render(request, 'main/home.html', {"excercises": "mhm"})


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

@login_required(login_url="/login")
def exercise_list(request):
    exercises = Exercise.objects.filter(user=request.user)
    muscle_groups = request.GET.getlist('muscle_group')
    sort_by = request.GET.get('sort_by')

    if muscle_groups:
        exercises = exercises.filter(muscle_group__in=muscle_groups)

    if sort_by:
        exercises = exercises.order_by(sort_by)

    return render(request, 'you_train_api/exercise_list.html', {
        'exercises': exercises,
        'selected_muscle_groups': muscle_groups,
        'sort_by': sort_by,
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
