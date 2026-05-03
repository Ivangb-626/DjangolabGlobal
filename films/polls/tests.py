from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthFlowTests(TestCase):
    def test_register_redirects_to_films_and_logs_user_in(self):
        response = self.client.post(
            reverse('polls:register'),
            {
                'username': 'nuevo_usuario',
                'password1': 'ClaveSegura123',
                'password2': 'ClaveSegura123',
            },
        )

        self.assertRedirects(response, reverse('polls:films'))
        self.assertTrue(User.objects.filter(username='nuevo_usuario').exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), User.objects.get(username='nuevo_usuario').pk)

    def test_login_redirects_to_films(self):
        User.objects.create_user(username='ivan', password='ClaveSegura123')

        response = self.client.post(
            reverse('polls:login'),
            {
                'username': 'ivan',
                'password': 'ClaveSegura123',
            },
        )

        self.assertRedirects(response, reverse('polls:films'))
        self.assertEqual(int(self.client.session['_auth_user_id']), User.objects.get(username='ivan').pk)

    def test_logout_redirects_to_index_and_clears_session(self):
        user = User.objects.create_user(username='ivan', password='ClaveSegura123')
        self.client.force_login(user)

        response = self.client.post(reverse('polls:logout'))

        self.assertRedirects(response, reverse('polls:index'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_films_requires_login(self):
        response = self.client.get(reverse('polls:films'))

        self.assertRedirects(response, f"{reverse('polls:login')}?next={reverse('polls:films')}")
