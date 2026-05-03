from functools import wraps
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .forms import RegisterForm, VoteForm
from .models import Filma, Votante


def _redirect_if_authenticated(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        return redirect('polls:films') if request.user.is_authenticated else f(request, *args, **kwargs)
    return wrapper


def _logout_if_authenticated(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated: auth_logout(request)
        return f(request, *args, **kwargs)
    return wrapper


def _votante(user): return Votante.objects.get_or_create(usuario=user)[0]


@_logout_if_authenticated
def index(request):
    return render(request, 'polls/index.html')


@_redirect_if_authenticated
def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        auth_login(request, form.save())
        return redirect('polls:films')
    return render(request, 'polls/register.html', {'form': form})


@_redirect_if_authenticated
def login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        auth_login(request, form.get_user())
        return redirect('polls:films')
    return render(request, 'polls/login.html', {'form': form})


@login_required(login_url='polls:login')
def films(request):
    return render(request, 'polls/films.html')


@login_required(login_url='polls:login')
def usuario(request):
    p = Filma.objects.order_by('izenburua')
    return render(request, 'polls/usuario.html', {
        'peliculas': p,
        'pelicula_seleccionada': p.prefetch_related('votantes__usuario').filter(id=request.GET.get('pelicula')).first()
    })


@login_required(login_url='polls:login')
def votar(request):
    form = VoteForm(request.POST or None, queryset=Filma.objects.order_by('izenburua'))
    if request.method == 'POST' and form.is_valid():
        pelicula = form.cleaned_data.get('pelicula')
        if pelicula:
            v = _votante(request.user)
            if not v.peliculas.filter(id=pelicula.id).exists():
                v.peliculas.add(pelicula)
                Filma.objects.filter(id=pelicula.id).update(bozkak=F('bozkak') + 1)
                return redirect('polls:votar')
    return render(request, 'polls/votar.html', {'form': form})


@login_required(login_url='polls:login')
def ver(request):
    peliculas = Filma.objects.order_by('izenburua').prefetch_related('votantes__usuario')
    return render(request, 'polls/ver.html', {'peliculas': peliculas})


@login_required(login_url='polls:login')
def verificar_voto(request):
    return JsonResponse({'votada': _votante(request.user).peliculas.filter(id=request.GET.get('pelicula_id')).exists()})


def logout(request):
    if request.method == 'POST': auth_logout(request)
    return redirect('polls:index')

