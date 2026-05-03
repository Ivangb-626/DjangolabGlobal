from django.conf import settings
from django.db import models


class Filma(models.Model):
    izenburua = models.CharField(max_length=200, unique=True)
    zuzendaria = models.CharField(max_length=200)
    urtea = models.PositiveIntegerField()
    generoa = models.CharField(max_length=50)
    sinopsia = models.TextField()
    bozkak = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.izenburua

    def votantes_nombres(self):
        nombres = self.votantes.order_by('usuario__username').values_list('usuario__username', flat=True)
        return ', '.join(nombres) if nombres else '-'

    votantes_nombres.short_description = 'Votantes'


class Votante(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='votante',
    )
    peliculas = models.ManyToManyField(
        Filma,
        blank=True,
        related_name='votantes',
    )

    def __str__(self):
        return self.usuario.username
