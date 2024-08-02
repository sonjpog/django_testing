import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', (1,)),
    ),
)
def test_pages_availability_for_anonymous_user(client, name, args, news):
    """
    Доступность страниц для анонимного пользователя:
    - Главная страница
    - Страница логина
    - Страница логаута
    - Страница регистрации
    - Страница отдельной новости
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_pages_availability_for_author(author_client, name, comment):
    """Доступность страниц редактирования"""
    """и удаления комментария для автора комментария."""
    url = reverse(name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_pages_availability_for_different_users(parametrized_client, name,
                                                comment, expected_status):
    """
    Доступность страниц редактирования и удаления
    комментария для разных пользователей.
    """
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:delete', (1,)),
        ('news:edit', (1,)),
    ),
)
def test_redirects(client, name, args):
    """
    Перенаправление анонимного пользователя на страницу логина
    при попытке доступа к страницам редактирования или удаления комментария.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
