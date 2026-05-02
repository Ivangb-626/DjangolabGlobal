
from django.contrib.auth import login as auth_login
from django.shortcuts import redirect, render

from .forms import RegisterForm


def index(request):
    return render(request, 'polls/index.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('polls:login')
    else:
        form = RegisterForm()

    return render(request, 'polls/register.html', {'form': form})


def login(request):
    return render(request, 'polls/login.html')


def films(request):
    return render(request, 'polls/films.html')


def usuario(request):
    return render(request, 'polls/usuario.html')


def votar(request):
    return render(request, 'polls/votar.html')


def ver(request):
    return render(request, 'polls/ver.html')
