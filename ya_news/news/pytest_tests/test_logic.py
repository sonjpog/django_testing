from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import WARNING


def test_user_can_create_comment(author_client, author, news, comment_text):
    """Авторизованный пользователь может отправить комментарий."""
    comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, {'text': comment_text})
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == comments_count + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == comment_text
    assert new_comment.author == author
    assert new_comment.news == news


def test_anonymous_user_cant_create_comment(client, news, comment_text):
    """Анонимный пользователь не может отправить комментарий."""
    comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, {'text': comment_text})
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comments_count


def test_user_cant_use_bad_words(author_client, news, bad_comment_text):
    """Комментарий с запрещенными словами не будет опубликован."""
    comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, {'text': bad_comment_text})
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == comments_count


def test_author_can_delete_comment(author_client, news, comment):
    """Авторизованный пользователь может удалить свой комментарий."""
    comments_count = Comment.objects.count()
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == comments_count - 1


def test_author_can_edit_comment(author_client, news,
                                 comment, updated_comment_text):
    """Авторизованный пользователь может редактировать свой комментарий."""
    comments_count = Comment.objects.count()
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, {'text': updated_comment_text})
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == updated_comment_text
    assert Comment.objects.count() == comments_count


def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    """Авторизованный пользователь не может удалить чужой комментарий."""
    comments_count = Comment.objects.count()
    url = reverse('news:delete', args=(comment.id,))
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count


def test_user_cant_edit_comment_of_another_user(reader_client, comment,
                                                new_comment_text):
    """Авторизованный пользователь не может редактировать чужой комментарий."""
    url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(url, {'text': new_comment_text})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != new_comment_text
