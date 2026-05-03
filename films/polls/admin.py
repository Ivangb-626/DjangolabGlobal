from django.contrib import admin

from .models import Filma, Votante


@admin.register(Filma)
class FilmaAdmin(admin.ModelAdmin):
    list_display = ('id', 'izenburua', 'zuzendaria', 'urtea', 'generoa', 'bozkak')
    search_fields = ('izenburua', 'zuzendaria', 'generoa')


@admin.register(Votante)
class VotanteAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'peliculas_votadas')
    search_fields = ('usuario__username', 'peliculas__izenburua')

    def peliculas_votadas(self, obj):
        return ', '.join(obj.peliculas.values_list('izenburua', flat=True)) or '-'

    peliculas_votadas.short_description = 'Peliculas votadas'
