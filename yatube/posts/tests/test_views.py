from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

        cls.post = Post.objects.bulk_create(
            Post(
                author=cls.post_author,
                group=cls.group,
                text=f'Тестовый пост №{n} из группы',
            )
            for n in range(30)
        )
        cls.single_post = Post.objects.create(
            text='Это текст моего поста',
            author=cls.post_author,
            group=cls.group
        )

    def setUp(self):
        # Создаем авторизованный клиент - автора поста
        self.authorized_author = Client()
        self.authorized_author.force_login(TestViews.post_author)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "reverse(name): имя_html_шаблона"
        pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{self.group.slug}'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.post_author}'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.single_post.id}'}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.single_post.id}'}
            ): 'posts/create_post.html'
        }
        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Функция для сравнения списков постов и их первых элементов
    # (для главной страницы, страниц групп и профилей пользователей)
    def assertLists(
            self,
            get_page_object_list,
    ):
        expected_page_object_list = list(Post.objects.all()[:10])
        first_object = get_page_object_list[0]
        post_text_0 = first_object.text
        author_0 = first_object.author.username
        group_0 = first_object.group.title
        self.assertListEqual(
            get_page_object_list,
            expected_page_object_list
        )
        self.assertEqual(post_text_0, 'Это текст моего поста')
        self.assertEqual(author_0, f'{self.post_author}')
        self.assertEqual(group_0, f'{self.group}')

    # Проверка словаря контекста главной страницы
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse('posts:index'))
        get_page_object_list = response.context['page_obj'].object_list
        self.assertLists(get_page_object_list)

    # Проверка словаря контекста страницы группы
    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{self.group.slug}'}
            )
        )
        get_page_object_list = response.context['page_obj'].object_list
        self.assertLists(get_page_object_list)

    # Проверка словаря контекста страницы профиля
    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'Masha'}
            )
        )
        get_page_object_list = response.context['page_obj'].object_list
        self.assertLists(get_page_object_list)

    # Проверка словаря контекста страницы поста
    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.single_post.id}'}
            ))
        self.assertEqual(response.context.get('post'),
                         self.single_post)

    # # Проверка словаря контекста страницы создания поста
    # def test_post_create_pages_show_correct_context(self):
    #     response = self.authorized_author.get(reverse(
    #         'posts:post_create'
    #     ))
    #     form_fields = {
    #         'text': forms.fields.CharField,
    #         'group': forms.fields.ModelChoiceField,
    #     }
    #
    #     for value, expected in form_fields.items():
    #         with self.subTest(value=value):
    #             form_field = response.context['form'].fields[value]
    #             self.assertIsInstance(form_field, expected)
    #     self.assertFalse(response.context['is_edit'])
    #
    # # Проверка словаря контекста страницы редактирования поста
    # def test_post_create_pages_show_correct_context(self):
    #     response = self.authorized_author.get(reverse(
    #         'posts:post_create'
    #     ))
    #     form_fields = {
    #         'text': forms.fields.CharField,
    #         'group': forms.fields.ModelChoiceField,
    #     }
    #
    #     for value, expected in form_fields.items():
    #         with self.subTest(value=value):
    #             form_field = response.context['form'].fields[value]
    #             self.assertIsInstance(form_field, expected)
    #     self.assertTrue(response.context['is_edit'])

    def test_created_post_on_correct_pages(self):
        """Созданный пост появляется на главной странице, странице
        группы, странице автора."""

        post = self.single_post
        pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={
                'username': f'{self.post_author}'
            })
        ]
        for page in pages:
            self.assertIn(
                post,
                self.authorized_author.get(page).context['page_obj']
            )

    def test_created_post_not_on_other_groups_pages(self):
        """Созданный пост появляется на главной странице, странице
        группы, странице автора."""

        post = self.single_post
        another_group_page = reverse(
            'posts:group_list',
            kwargs={'slug': f'{self.group_without_post.slug}'}
        )
        response = self.authorized_author.get(another_group_page)
        group_page_posts = response.context['page_obj']
        self.assertNotIn(post, group_page_posts)


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
        Post.objects.bulk_create(
            Post(
                author=cls.post_author,
                group=cls.group,
                text=f'Тестовый пост №{n} из группы',
            )
            for n in range(13)
        )

    def setUp(self):
        # Создаем авторизованный клиент - автора поста
        self.authorized_author = Client()
        self.authorized_author.force_login(
            PaginatorViewsTest.post_author
        )

    def test_index_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_first_page_contains_ten_records(self):
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': f'{self.group.slug}'}
        ))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': f'{self.group.slug}'}
        ) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': 'Masha'}
        ))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': 'Masha'}
        ) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
