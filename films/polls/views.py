
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm


def index(request):
    return render(request, 'polls/index.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('polls:films')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('polls:films')
    else:
        form = RegisterForm()

    return render(request, 'polls/register.html', {'form': form})


def login(request):
    if request.user.is_authenticated:
        return redirect('polls:films')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                auth_login(request, user)
                return redirect('polls:films')
            form.add_error(None, 'Usuario o contrasena incorrectos.')
    else:
        form = LoginForm()

    return render(request, 'polls/login.html', {'form': form})


@login_required(login_url='polls:login')
def films(request):
    return render(request, 'polls/films.html')


@login_required(login_url='polls:login')
def usuario(request):
    return render(request, 'polls/usuario.html')


@login_required(login_url='polls:login')
def votar(request):
    return render(request, 'polls/votar.html')


@login_required(login_url='polls:login')
def ver(request):
    return render(request, 'polls/ver.html')


def logout(request):
    if request.method == 'POST':
        auth_logout(request)
    return redirect('polls:index')
