from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
# login crea las cookies para que el usuario sea reconocido por el navegador
from django.contrib.auth import login, logout, authenticate
# validar error (usuario existente) dentro de un Except
from django.db import IntegrityError
from .forms import Create_TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                # Register user
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {'form': UserCreationForm(), 'error': 'Username already exists.'})
        else:
            return render(request, 'signup.html', {'form': UserCreationForm(), 'error': 'Password do not match.'})

@login_required
def tasks(request):
    page_name = 'tasks'
    user_ = request.user
    tasks = Task.objects.filter(user=user_, datecompleted__isnull=True).order_by('-datecreated')
    return render(request, 'tasks.html', {'tasks': tasks, 'user':user_, 'page_name':page_name})

@login_required
def tasks_completed(request):
    page_name = 'tasks_completed'
    user_ = request.user
    tasks = Task.objects.filter(user=user_, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {'tasks': tasks, 'user':user_, 'page_name':page_name})

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = Create_TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = Create_TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form,'error':'Error updating task'})
 
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
   
    if request.method=='POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required 
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method=='POST':
        task.delete()
        return redirect('tasks')

@login_required
def create_task(request):
    user_ = request.user
    if request.method == 'GET':
        return render(request, 'create_task.html', {'form': Create_TaskForm,'user':user_})
    else:
        try:
            # Crea un formulario con todos los atributos de Create_TaskForm
            new_data = Create_TaskForm(request.POST)
            # No se quiere guardar un formulario, solo los datos que lo llenan
            new_task = new_data.save(commit=False)
            new_task.user = request.user               # Se le da el atributo user hace falta
            # Guardar datos en la base de datos de tareas
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {'form': Create_TaskForm,'user':user_, 'error': 'Please provide a valid data'})

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {'form': AuthenticationForm, 'error': 'Username or password is incorrect.'})
        else:
            login(request, user)
            return redirect('tasks')
