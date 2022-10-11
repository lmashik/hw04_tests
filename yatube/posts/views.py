from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .forms import PostForm
from .models import Group, Post, User
from .utils import get_page_obj


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = get_page_obj(request, posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_page_obj(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author')
    page_obj = get_page_obj(request, posts)
    context = {
        'page_obj': page_obj,
        'author': author
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    context = {
        'form': form,
        'is_edit': False
    }
    if form.is_valid():
        real_author = form.save(commit=False)
        real_author.author = request.user
        real_author.save()
        return redirect('posts:profile', request.user.username)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    context = {
        'form': form,
        'is_edit': True
    }
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, template, context)
