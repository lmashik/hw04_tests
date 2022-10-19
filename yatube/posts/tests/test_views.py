import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group, Comment, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Valera')
        cls.post_author = User.objects.create_user(username='Masha')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        cls.group_without_post = Group.objects.create(
            title='Группа без поста',
            slug='group-without-post',
            description='Посты добавлялись в группу... но не в эту'
        )
        post_image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=post_image,
            content_type='image/gif'
        )
        cls.single_post = Post.objects.create(
            text='Это текст моего поста',
            author=cls.post_author,
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            text='Ава зачет!!!',
            post=cls.single_post,
            author=cls.post_author
        )
        cls.follower = Follow.objects.create(
            user=cls.post_author,
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем авторизованный клиент - автора поста
        cache.clear()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post_author)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.post_author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.single_post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.single_post.id}
            ): 'posts/create_post.html'
        }
        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Функция для сравнения первых элементов списка постов
    # на главной странице, страницах групп и профилей пользователей
    def assert_attr_equation(
            self,
            one_object,
    ):
        post_text_0 = one_object.text
        author_0 = one_object.author.username
        group_0 = one_object.group.title
        image_0 = one_object.image.name
        self.assertEqual(post_text_0, self.single_post.text)
        self.assertEqual(author_0, self.post_author.username)
        self.assertEqual(group_0, self.group.title)
        self.assertIn(self.uploaded.name, image_0)

    # Проверка словаря контекста главной страницы
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом и атрибуты
        первого поста как ожидается."""
        response = self.authorized_author.get(reverse('posts:index'))
        get_object = response.context['page_obj'][0]
        self.assert_attr_equation(get_object)

    # Проверка словаря контекста страницы группы
    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом
        и атрибуты первого поста как ожидается."""
        response = self.authorized_author.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        get_object = response.context['page_obj'][0]
        self.assert_attr_equation(get_object)

    # Проверка словаря контекста страницы профиля
    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом и атрибуты
        первого поста как ожидается."""
        response = self.authorized_author.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.post_author}
            )
        )
        get_object = response.context['page_obj'][0]
        self.assert_attr_equation(get_object)

    # Проверка словаря контекста страницы поста
    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.single_post.id}
            ))
        self.assertEqual(response.context.get('post'),
                         self.single_post)

    # # Проверка словаря контекста страницы создания поста
    def test_post_create_pages_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом
        при создании поста."""
        response = self.authorized_author.get(reverse(
            'posts:post_create'
        ))
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertFalse(response.context['is_edit'])

    # # Проверка словаря контекста страницы редактирования поста
    def test_post_edit_pages_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом
        при редактировании поста."""
        response = self.authorized_author.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.single_post.id}
        ))
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertTrue(response.context['is_edit'])

    def test_created_post_on_correct_pages(self):
        """Созданный пост появляется на главной странице, странице
        группы, странице автора."""
        post = self.single_post
        pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.post_author}
            )
        ]
        for page in pages:
            self.assertIn(
                post,
                self.authorized_author.get(page).context['page_obj']
            )

    def test_created_post_not_on_other_groups_pages(self):
        """Созданный пост не появляется на странице группы, которой он
        не принадлежит."""

        post = self.single_post
        another_group_page = reverse(
            'posts:group_list',
            kwargs={'slug': self.group_without_post.slug}
        )
        response = self.authorized_author.get(another_group_page)
        group_page_posts = response.context['page_obj']
        self.assertNotIn(post, group_page_posts)

    def test_added_comment_on_post_page(self):
        """Созданный комментарий появляется на странице поста."""
        page = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.single_post.id}
        )
        self.assertIn(
            self.comment,
            self.authorized_author.get(page).context['comments']
        )

    def test_added_comment_not_on_another_post_page(self):
        """Созданный комментарий не появляется на странице
        другого поста."""
        another_post = Post.objects.create(
            text='Привет, мир!',
            author=self.post_author,
            group=self.group
        )
        page = reverse(
            'posts:post_detail',
            kwargs={'post_id': another_post.id}
        )
        self.assertNotIn(
            self.comment,
            self.authorized_author.get(page).context['comments']
        )

    def test_cache_on_index_page(self):
        """После удаления поста он находится в кэше
        до принудительной чистки."""
        index_page = reverse('posts:index')
        first_response = self.authorized_author.get(index_page)
        post = Post.objects.create(
            author=self.post_author,
            group=self.group,
            text='Опять нам нужен дополнительный пост'
        )
        post.delete()
        second_response = self.authorized_author.get(index_page)
        self.assertEqual(
            first_response.content,
            second_response.content
        )
        cache.clear()
        third_response = self.authorized_author.get(index_page)
        self.assertEqual(third_response.content, first_response.content)

    def test_auth_user_follow_another(self):
        """Авторизованный пользователь может подписываться
        на другого пользователя."""
        page = reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        )
        response = self.authorized_author.get(page)
        self.assertTrue(response.context['following'])

    def test_auth_user_unfollow_another(self):
        """Авторизованный пользователь может отписаться
        от другого пользователя."""
        self.follower.delete()
        page = reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        )
        response = self.authorized_author.get(page)
        self.assertFalse(response.context['following'])

    def test_follower_sees_post_on_follow_index_page(self):
        """Подписанный пользователь видит пост в избранном."""
        some_post = Post.objects.create(
            text='я, user, тоже пишу посты',
            author=self.user
        )
        page = reverse('posts:follow_index')
        response = self.authorized_author.get(page)
        self.assertIn(some_post, response.context['page_obj'])

    def test_not_follower_doesnt_see_post_on_follow_index_page(self):
        page = reverse('posts:follow_index')
        response = self.authorized_author.get(page)
        self.assertNotIn(self.single_post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='Masha')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        cls.all_posts = int(1.5 * settings.POSTS_PER_PAGE)
        cls.posts_on_second_page = (
            cls.all_posts
            - settings.POSTS_PER_PAGE
        )
        Post.objects.bulk_create(
            Post(
                author=cls.post_author,
                group=cls.group,
                text=f'Тестовый пост №{n} из группы',
            )
            for n in range(cls.all_posts)
        )

    def setUp(self):
        cache.clear()
        # Создаем клиент и авторизуем в нем автора поста
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post_author)

    def test_index_first_page_contains_ten_posts(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']),
            settings.POSTS_PER_PAGE
        )

    def test_index_second_page_contains_three_posts(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            self.posts_on_second_page
        )

    def test_group_first_page_contains_ten_posts(self):
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        ))
        self.assertEqual(
            len(response.context['page_obj']),
            settings.POSTS_PER_PAGE
        )

    def test_group_second_page_contains_three_posts(self):
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}) + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            self.posts_on_second_page
        )

    def test_profile_first_page_contains_ten_posts(self):
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': self.post_author}
        ))
        self.assertEqual(
            len(response.context['page_obj']),
            settings.POSTS_PER_PAGE
        )

    def test_profile_second_page_contains_three_posts(self):
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': self.post_author}) + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            self.posts_on_second_page
        )
