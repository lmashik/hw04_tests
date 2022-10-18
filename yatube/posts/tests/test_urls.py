from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache

from ..models import Post, Group

user = User = get_user_model()


class URLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='Masha')
        cls.not_author = User.objects.create_user(username='NotAuthor')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост о самых разных интересных вещах!',
            author=cls.post_author,
            group=cls.group
        )

    def setUp(self):
        cache.clear()
        # Создаем клиент и авторизуем в нем автора поста
        self.authorized_and_author = Client()
        self.authorized_and_author.force_login(self.post_author)
        # Создаем клиент и авторизуем в нем НЕ автора поста
        self.authorized_not_author = Client()
        self.authorized_not_author.force_login(self.not_author)

    # Проверяем, что для авторизованного автора все страницы доступны и
    # ведут к соответствующим шаблонам
    def test_urls_exist_at_desired_location_and_use_correct_templates(
            self
    ):
        """Страницы по указанным URL доступны авторизованному автору
        и URL-адреса используют соответствующие шаблоны."""
        url_names_templates = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post_author}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in url_names_templates.items():
            with self.subTest(url=url):
                response = self.authorized_and_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    # Проверяем, что открытие несуществующей страницы ведет к 404 ошибке
    def test_unexisting_page_url_exists_at_desired_location(self):
        """Страница /unexisting-page/ не существует."""
        response = self.client.get('/unexisting-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверяем, что неавторизованный пользователь получает редирект
    # на страницах создания и редактирования поста
    def test_create_post_page_url_redirect_anonymous_on_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_edit_post_page_url_redirect_anonymous_on_login(self):
        """Страница по адресу /posts/<post_id>/edit/ перенаправит
        анонимного пользователя на страницу логина.
        """
        response = self.client.get(
            f'/posts/{self.post.id}/edit/',
            follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/')

    # Проверяем, что авторизованный не автор получает редирект на
    # странице редактирования поста
    def test_edit_post_page_url_redirect_not_author_on_post_page(
            self):
        """Страница по адресу /posts/<post_id>/edit/ перенаправит не
        автора на страницу поста."""
        response = self.authorized_not_author.get(
            f'/posts/{self.post.id}/edit/',
            follow=True
        )
        self.assertRedirects(
            response, f'/posts/{self.post.id}/')

    def test_post_detail_comment_page_url_redirect_auth_on_post_detail(
            self
    ):
        """Страница по адресу /posts/<post_id>/comment/ перенаправит
        авторизованного пользователя на страницу поста."""
        response = self.authorized_not_author.get(
            f'/posts/{self.post.id}/comment/',
            follow=True
        )
        self.assertRedirects(
            response,
            f'/posts/{self.post.id}/'
        )

    def test_post_detail_comment_page_url_redirect_anonymous_on_login(
            self
    ):
        """Страница по адресу /posts/<post_id>/comment/ перенаправит
        анонимного пользователя на страницу логина.
        """
        response = self.client.get(
            f'/posts/{self.post.id}/comment/',
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )
