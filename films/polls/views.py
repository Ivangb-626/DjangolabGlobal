
from django.shortcuts import render


def index(request):
    return render(request, 'polls/index.html')

def register(request):
    return render(request, 'polls/register.html')

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