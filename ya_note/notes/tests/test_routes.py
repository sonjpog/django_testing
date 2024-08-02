from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

        # URLs for testing
        cls.public_urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )

        cls.authorized_urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )

        cls.edit_delete_detail_urls = (
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
            ('notes:detail', (cls.note.slug,)),
        )

        cls.redirect_urls = (
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
            ('notes:detail', (cls.note.slug,)),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )

    def test_pages_availability(self):
        """Доступность общедоступных страниц."""
        for name, args in self.public_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_available_for_authorized_user(self):
        """Доступность страниц для авторизованного пользователя."""
        self.client.force_login(self.author)
        for name, args in self.authorized_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_edit_delete_detail(self):
        """Доступность страниц редактирования, удаления и деталей"""
        """для авторизованных пользователей."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in self.edit_delete_detail_urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Перенаправление анонимного пользователя на страницу входа."""
        login_url = reverse('users:login')
        for name, args in self.redirect_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
