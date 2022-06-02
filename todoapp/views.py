import django
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login as lin
from django.contrib.auth import logout as lout
from django.contrib.auth import authenticate
from django.db import IntegrityError
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

def login(request):
    
    if request.method == 'GET':
        return render(request, 'login.html', {'form':AuthenticationForm(), "error":''})

    else:
        #Login user
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'login.html', {'form':AuthenticationForm(), "error":"Such user doesn't exist"})
        else:
            lin(request, user)
            return redirect('currenttodos')
@login_required
def logout(request):
    if request.method == 'POST':
        lout(request)
        return redirect('home')



def signup(request):

    if request.method == 'GET':
        return render(request, 'signupuser.html', {'form':UserCreationForm(), "error":''})

    else:
        #Creation of new user
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                lin(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                 return render(request, 'signupuser.html', {'form':UserCreationForm(), 'error': "This name has been taken"})

        else:
            return render(request, 'signupuser.html', {'form':UserCreationForm(), 'error': "Passwords didn't match"})
@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'createtodo.html', {'form':TodoForm(), "error":""})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'createtodo.html', {'form':TodoForm(), "error":"Bad data passed in"})
@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'current.html', {'todos':todos})
@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'completed.html', {'todos':todos})
@login_required
def viewtodo(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST,instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'viewtodo.html', {'todo': todo, 'form': form,"error":"Bad data passed in"})
@login_required
def completetodo(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')
@login_required
def deletetodo(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')