
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db import models, transaction
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm, VoteForm
from .models import Filma, Votante


def _get_or_create_votante(user):
    votante, _ = Votante.objects.get_or_create(usuario=user)
    return votante


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
    peliculas = Filma.objects.order_by('izenburua').prefetch_related('votantes__usuario')
    return render(request, 'polls/usuario.html', {'peliculas': peliculas})


@login_required(login_url='polls:login')
def votar(request):
    votante = _get_or_create_votante(request.user)
    already_voted = votante.peliculas.all().order_by('izenburua')
    available = Filma.objects.exclude(id__in=already_voted.values('id')).order_by('izenburua')

    if request.method == 'POST':
        form = VoteForm(request.POST, queryset=available)
        if form.is_valid():
            selected = list(form.cleaned_data['peliculas'])
            with transaction.atomic():
                votante = Votante.objects.select_for_update().get(pk=votante.pk)
                current_ids = set(votante.peliculas.values_list('id', flat=True))
                new_films = [filma for filma in selected if filma.id not in current_ids]
                if new_films:
                    votante.peliculas.add(*new_films)
                    Filma.objects.filter(id__in=[filma.id for filma in new_films]).update(bozkak=models.F('bozkak') + 1)
            return redirect('polls:votar')
    else:
        form = VoteForm(queryset=available)

    return render(
        request,
        'polls/votar.html',
        {
            'form': form,
            'votadas': already_voted,
            'disponibles': available,
        },
    )


@login_required(login_url='polls:login')
def ver(request):
    peliculas = Filma.objects.order_by('izenburua').prefetch_related('votantes__usuario')
    return render(request, 'polls/ver.html', {'peliculas': peliculas})


def logout(request):
    if request.method == 'POST':
        auth_logout(request)
    return redirect('polls:index')
