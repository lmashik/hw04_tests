from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group

user = User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='Masha')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post_author)

    def test_create_post(self):
        """Валидная форма создает пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Еще один тестовый текст',
            'group': self.group.id,
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
                kwargs={'username': self.post_author}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Еще один тестовый текст',
                group=self.group.id,
                author=self.post_author.id
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует пост."""
        self.post = Post.objects.create(
            text='Тестовый пост о самых разных интересных вещах!',
            author=self.post_author,
            group=self.group
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Теперь тут такой текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        # self.assertEqual(Post.objects.last(), self.post)
        last_post = Post.objects.last()
        last_post_text = last_post.text
        last_post_author = last_post.author
        last_post_group = last_post.group.id

        self.assertEqual(last_post_text, form_data['text'])
        self.assertEqual(last_post_group, form_data['group'])
        self.assertEqual(last_post_author, self.post_author)
