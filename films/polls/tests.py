from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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


class VerPeliculasViewTests(TestCase):
    def test_ver_muestra_peliculas_en_tabla(self):
        usuario = User.objects.create_user(username='pepe', password='ClaveSegura123')
        Filma.objects.create(
            izenburua='Earthlings',
            zuzendaria='Shaun Monson',
            urtea=2005,
            generoa='DO',
            sinopsia='Documental sobre la explotacion animal.',
            bozkak=7,
        )

        self.client.force_login(usuario)
        response = self.client.get(reverse('polls:ver'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<table', html=False)
        self.assertContains(response, 'Earthlings')
        self.assertContains(response, 'Shaun Monson')
        self.assertContains(response, '7')

    def test_ver_muestra_los_usuarios_que_han_votado(self):
        usuario1 = User.objects.create_user(username='ana', password='ClaveSegura123')
        usuario2 = User.objects.create_user(username='borja', password='ClaveSegura123')
        filma = Filma.objects.create(
            izenburua='Dominion',
            zuzendaria='Chris Delforce',
            urtea=2018,
            generoa='DO',
            sinopsia='Documental sobre la industria animal.',
            bozkak=2,
        )
        votante1 = Votante.objects.create(usuario=usuario1)
        votante2 = Votante.objects.create(usuario=usuario2)
        votante1.peliculas.add(filma)
        votante2.peliculas.add(filma)

        self.client.force_login(usuario1)
        response = self.client.get(reverse('polls:ver'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ana')
        self.assertContains(response, 'borja')


class UsuarioViewTests(TestCase):
    def test_usuario_muestra_los_votantes_por_pelicula(self):
        usuario1 = User.objects.create_user(username='alba', password='ClaveSegura123')
        usuario2 = User.objects.create_user(username='beto', password='ClaveSegura123')
        filma = Filma.objects.create(
            izenburua='Earthlings',
            zuzendaria='Shaun Monson',
            urtea=2005,
            generoa='DO',
            sinopsia='Documental sobre la explotacion animal.',
            bozkak=2,
        )
        Votante.objects.create(usuario=usuario1).peliculas.add(filma)
        Votante.objects.create(usuario=usuario2).peliculas.add(filma)

        self.client.force_login(usuario1)
        response = self.client.get(reverse('polls:usuario'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Earthlings')
        self.assertContains(response, 'alba')
        self.assertContains(response, 'beto')


class VotarPeliculasViewTests(TestCase):
    def test_votar_suma_un_voto_y_lo_registra_en_el_usuario(self):
        usuario = User.objects.create_user(username='lucia', password='ClaveSegura123')
        self.client.force_login(usuario)
        filma = Filma.objects.create(
            izenburua='Earthlings',
            zuzendaria='Shaun Monson',
            urtea=2005,
            generoa='DO',
            sinopsia='Documental sobre la explotacion animal.',
        )

        response = self.client.post(reverse('polls:votar'), {'peliculas': [filma.id]})

        self.assertEqual(response.status_code, 302)
        votante = Votante.objects.get(usuario=usuario)
        self.assertEqual(list(votante.peliculas.values_list('id', flat=True)), [filma.id])
        filma.refresh_from_db()
        self.assertEqual(filma.bozkak, 1)

    def test_votar_la_misma_pelicula_dos_veces_no_incrementa_el_conteo(self):
        usuario = User.objects.create_user(username='elena', password='ClaveSegura123')
        self.client.force_login(usuario)
        filma = Filma.objects.create(
            izenburua='Dominion',
            zuzendaria='Chris Delforce',
            urtea=2018,
            generoa='DO',
            sinopsia='Documental sobre la industria animal.',
        )

        self.client.post(reverse('polls:votar'), {'peliculas': [filma.id]})
        response = self.client.post(reverse('polls:votar'), {'peliculas': [filma.id]})

        self.assertEqual(response.status_code, 200)
        votante = Votante.objects.get(usuario=usuario)
        self.assertEqual(votante.peliculas.count(), 1)
        filma.refresh_from_db()
        self.assertEqual(filma.bozkak, 1)
