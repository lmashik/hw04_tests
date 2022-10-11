from ..forms import PostForm
from ..models import Post, Group
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

user = User = get_user_model()


class TestForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='Masha')
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
        # Создаем форму
        cls.form = PostForm()

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(TestForm.post_author)

    def test_create_post(self):
        """Валидная форма создает пост."""
        # Подсчитаем количество постов
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Еще один тестовый текст',
            'group': f'{self.group.id}',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.post_author}'}
            )
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создался пост с указанными текстом и группой
        self.assertTrue(
            Post.objects.filter(
                text='Еще один тестовый текст',
                group=f'{self.group.id}',
                author=f'{self.post_author.id}'
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует пост."""
        # Подсчитаем количество постов
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Теперь тут такой текст',
            'group': f'{self.group.id}',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.post.id}'}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}
            )
        )
        # Проверяем, не изменилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что пост отредактирован
        self.assertTrue(
            Post.objects.filter(
                text='Теперь тут такой текст',
                group=f'{self.group.id}',
                author=f'{self.post_author.id}'
            ).exists()
        )
