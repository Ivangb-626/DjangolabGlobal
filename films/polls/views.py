from functools import wraps
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .forms import RegisterForm, VoteForm
from .models import Filma, Votante


def _redirect_if_authenticated(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('polls:films')
        return view_func(request, *args, **kwargs)
    return wrapper


def _logout_if_authenticated(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            auth_logout(request)
        return view_func(request, *args, **kwargs)
    return wrapper


def _get_or_create_votante(user):
    return Votante.objects.get_or_create(usuario=user)[0]


def _peliculas_con_votantes():
    return Filma.objects.order_by('izenburua').prefetch_related('votantes__usuario')


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
    pelicula_id = request.GET.get('pelicula')
    peliculas = Filma.objects.order_by('izenburua')
    pelicula_seleccionada = None

    if pelicula_id:
        try:
            pelicula_seleccionada = peliculas.prefetch_related('votantes__usuario').get(id=pelicula_id)
        except Filma.DoesNotExist:
            pass

    return render(
        request,
        'polls/usuario.html',
        {
            'peliculas': peliculas,
            'pelicula_seleccionada': pelicula_seleccionada,
        },
    )


@login_required(login_url='polls:login')
def votar(request):
    votante = _get_or_create_votante(request.user)
    votadas = votante.peliculas.values_list('id', flat=True)
    todas_peliculas = Filma.objects.order_by('izenburua')

    pelicula_votada = False
    pelicula_seleccionada_id = None
    form = VoteForm(request.POST or None, queryset=todas_peliculas)

    if request.method == 'POST' and form.is_valid():
        pelicula = form.cleaned_data.get('pelicula')

        if pelicula:
            pelicula_seleccionada_id = pelicula.id
            # Verificar si ya fue votada
            if pelicula.id in votadas:
                pelicula_votada = True
            else:
                # Agregar voto
                votante.peliculas.add(pelicula)
                Filma.objects.filter(id=pelicula.id).update(bozkak=F('bozkak') + 1)
                return redirect('polls:votar')

    return render(
        request,
        'polls/votar.html',
        {
            'form': form,
            'pelicula_votada': pelicula_votada,
        },
    )


@login_required(login_url='polls:login')
def ver(request):
    peliculas = Filma.objects.order_by('izenburua').prefetch_related('votantes__usuario')

    return render(
        request,
        'polls/ver.html',
        {
            'peliculas': peliculas,
        },
    )


@login_required(login_url='polls:login')
def verificar_voto(request):
    pelicula_id = request.GET.get('pelicula_id')
    if not pelicula_id:
        return JsonResponse({'votada': False})

    votante = _get_or_create_votante(request.user)
    votada = votante.peliculas.filter(id=pelicula_id).exists()

    return JsonResponse({'votada': votada})


def logout(request):
    if request.method == 'POST':
        auth_logout(request)
    return redirect('polls:index')

