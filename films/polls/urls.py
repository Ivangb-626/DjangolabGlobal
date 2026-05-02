from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('films/', views.films, name='films'),
    path('usuario/', views.usuario, name='usuario'),
    path('votar/', views.votar, name='votar'),
    path('ver/', views.ver, name='ver'),
]
