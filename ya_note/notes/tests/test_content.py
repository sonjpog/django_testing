from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class TestNotesPage(TestCase):

    NOTES_URL = reverse('notes:list')
    NOTE_COUNT = 10

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор записи')
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        all_notes = [
            Note(
                title=f'Новость{index}',
                text='Текст',
                author=cls.author,
                slug=f'note-{index}'
            )
            for index in range(cls.NOTE_COUNT)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_list_view_for_author(self):
        """Автор видит свои заметки на странице списка."""
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        first_note = object_list[0]
        self.assertIn(first_note, object_list)

    def test_notes_list_view_for_reader(self):
        """Читатель не видит заметок на странице списка."""
        self.client.force_login(self.reader)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        notes_count = len(object_list)
        self.assertEqual(notes_count, 0)

    def test_notes_count_for_author(self):
        """Количество заметок для автора равно NOTE_COUNT."""
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        notes_count = len(object_list)
        self.assertEqual(notes_count, self.NOTE_COUNT)


class TestAddAndEditPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор записи')
        cls.notes = Note.objects.create(
            title='Новость',
            text='Текст',
            author=cls.author
        )

    def test_add_and_edit_form(self):
        """На страницах добавления и редактирования есть форма."""
        self.client.force_login(self.author)
        urls = (
            ('notes:edit', (self.notes.slug,)),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
