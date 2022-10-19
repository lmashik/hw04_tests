from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост о самых разных интересных вещах!',
        )

    def test_post_model_str_method(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        text = str(self.post)
        self.assertEqual(
            text,
            'Тестовый пост о',
            'Неправильно работает str в модели Post'
        )

    def test_post_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_post_help_texts(self):
        """help_text в полях совпадает с ожидаемым."""
        post = self.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'pub_date': 'Default value: now',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def test_group_model_str_method(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        title = str(self.group)
        self.assertEqual(
            title, 'Тестовая группа',
            'Неправильно работает str в модели Group'
        )

    def test_group_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = self.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Идентификатор группы',
            'description': 'Описание группы'
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_group_help_texts(self):
        """help_text в полях совпадает с ожидаемым."""
        group = self.group
        field_help_texts = {
            'title': '200 characters max.',
            'slug': 'Enter unique slug, please.',
            'description': 'Enter the group description, please.'
        }

        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text,
                    expected_value
                )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост о самых разных интересных вещах!',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Ава зачет!'
        )

    def test_comment_model_str_method(self):
        """Проверяем, что у модели Comment
        корректно работает __str__."""
        text = str(self.comment)
        self.assertEqual(
            text,
            'Ава зачет!',
            'Неправильно работает str в модели Comment'
        )

    def test_comment_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        comment = self.comment
        field_verboses = {
            'text': 'Комментарий',
            'created': 'Дата комментария',
            'author': 'Автор',
            'post': 'Пост'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_comment_help_texts(self):
        """help_text в полях совпадает с ожидаемым."""
        comment = self.comment
        field_help_texts = {
            'text': 'Оставьте свой комментарий',
            'created': 'Default value: now',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).help_text,
                    expected_value
                )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='Petya')
        cls.user_user = User.objects.create_user(username='Vasya')
        cls.follow = Follow.objects.create(
            user=cls.user_user,
            author=cls.user_author
        )

    def test_comment_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        follow = self.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор постов'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(
                        field).verbose_name,
                    expected_value
                )
