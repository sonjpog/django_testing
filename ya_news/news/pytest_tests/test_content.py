from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


def test_home_page(client, news_10):
    """На главной странице отображается не более 10 новостей."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_10):
    """
    Новости на главной странице отсортированы
    от самой свежей к самой старой.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_detail_page_contains_form(author_client, news):
    """
    На странице отдельной новости для
    авторизованного пользователя отображается форма для отправки комментария.
    """
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
    form = response.context['form']
    assert isinstance(form, CommentForm)


def test_detail_page_contains_form_for_user(client, news):
    """
    На странице отдельной новости для анонимного пользователя
    не отображается форма для отправки комментария.
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


def test_comments_order(client, news, comments):
    """
    Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке.
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all().order_by('created')
    all_date_created = [comment.created for comment in all_comments]
    sorted_date = sorted(all_date_created)
    assert all_date_created == sorted_date
