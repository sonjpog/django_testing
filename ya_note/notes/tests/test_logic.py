from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'text': 'Текст',
            'title': 'Заголовок'
        }
        cls.expected_text = cls.form_data['text']
        cls.expected_title = cls.form_data['title']
        cls.expected_slug = 'zagolovok'

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        initial_notes_count = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, initial_notes_count)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        initial_notes_count = Note.objects.count()
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, initial_notes_count + 1)
        note = Note.objects.latest('id')
        self.assertEqual(note.text, self.expected_text)
        self.assertEqual(note.title, self.expected_title)
        self.assertEqual(note.author, self.user)

    def test_two_identical_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        initial_notes_count = Note.objects.count()
        self.auth_client.post(self.url, data=self.form_data)
        notes_count_first_attempt = Note.objects.count()
        self.assertEqual(notes_count_first_attempt,
                         initial_notes_count + 1)
        self.auth_client.post(self.url, data=self.form_data)
        notes_count_second_attempt = Note.objects.count()
        self.assertEqual(notes_count_second_attempt,
                         initial_notes_count + 1)

    def test_automatic_creation_slug(self):
        """При создании заметки, если не заполнен slug,"""
        """он формируется автоматически."""
        self.auth_client.post(self.url, data=self.form_data)
        note = Note.objects.latest('id')
        self.assertEqual(note.slug, self.expected_slug)


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )
        cls.note_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'text': 'Текст',
            'title': 'Заголовок'
        }
        cls.expected_text = cls.form_data['text']
        cls.expected_title = cls.form_data['title']

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        initial_notes_count = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.note_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, initial_notes_count - 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить заметку другого пользователя."""
        initial_notes_count = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, initial_notes_count)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.note_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.expected_text)
        self.assertEqual(self.note.title, self.expected_title)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать заметку другого пользователя."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.expected_text)
        self.assertEqual(self.note.title, self.expected_title)
