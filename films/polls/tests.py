from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Filma, Votante


User = get_user_model()


class ModelosVotacionTests(TestCase):
    def test_crear_usuario_no_crea_votante_automaticamente(self):
        usuario = User.objects.create_user(username='ana', password='ClaveSegura123')

        self.assertFalse(Votante.objects.filter(usuario=usuario).exists())

    def test_un_votante_puede_votar_varias_peliculas(self):
        usuario = User.objects.create_user(username='luis', password='ClaveSegura123')
        votante = Votante.objects.create(usuario=usuario)
        f1 = Filma.objects.create(
            izenburua='Earthlings',
            zuzendaria='Shaun Monson',
            urtea='2005',
            generoa='DO',
            sinopsia=(
                'Using hidden cameras and never-before-seen footage, Earthlings chronicles '
                'the day-to-day practices of the largest industries in the world, all of '
                'which rely entirely on animals for profit.'
            ),
            bozkak='0',
        )
        f2 = Filma.objects.create(
            izenburua='Koyaanisqatsi',
            zuzendaria='Godfrey Reggio',
            urtea=1982,
            generoa='DC',
            sinopsia='A visual tone poem about modern life and imbalance.',
        )

        votante.peliculas.add(f1, f2)

        self.assertEqual(votante.peliculas.count(), 2)
        self.assertEqual(list(votante.peliculas.order_by('izenburua')), [f1, f2])

    def test_bozkak_no_se_actualiza_automaticamente(self):
        usuario = User.objects.create_user(username='maria', password='ClaveSegura123')
        votante = Votante.objects.create(usuario=usuario)
        filma = Filma.objects.create(
            izenburua='Baraka',
            zuzendaria='Ron Fricke',
            urtea=1992,
            generoa='DC',
            sinopsia='A non-narrative documentary with striking global imagery.',
        )

        votante.peliculas.add(filma)

        filma.refresh_from_db()
        self.assertEqual(filma.bozkak, 0)

    def test_borrar_votante_no_borra_usuario(self):
        usuario = User.objects.create_user(username='nora', password='ClaveSegura123')
        votante = Votante.objects.create(usuario=usuario)
        usuario_id = usuario.id

        votante.delete()

        self.assertTrue(User.objects.filter(id=usuario_id).exists())
