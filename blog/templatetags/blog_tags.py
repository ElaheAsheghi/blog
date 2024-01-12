from django import template
from ..models import Post, Comment
from django.db.models import Count
from markdown import markdown
from django.utils.safestring import mark_safe
from django.template.defaulttags import register
from django.contrib.auth.models import User

register = template.Library()


@register.simple_tag()
def total_posts():
    return Post.Published.count()

@register.simple_tag()
def total_comments():
    return Comment.objects.filter(active=True).count()

@register.inclusion_tag("partials/latest_posts.html")
def latest_posts(count=4):
    l_posts = Post.Published.order_by('-publish')[:count]
    context = {
        'l_posts':l_posts
    }
    return context


@register.simple_tag
def most_popular_posts(count=5):
    return Post.Published.annotate(comments_count=Count('comments')).order_by('-comments_count')[:count]


@register.filter(name='markdown')
def to_markdown(text):
    return mark_safe(markdown(text))


@register.inclusion_tag("partials/max_time.html")
def max_time(count=1):
    max_post = Post.Published.order_by('-reading_time')[:count]
    context = {
        'max_post' : max_post
    }
    return context

@register.inclusion_tag("partials/min_time.html")
def min_time(count=1):
    min_post = Post.Published.order_by("reading_time")[:count]
    context = {
        'min_post' : min_post
    }
    return context

@register.filter(name="sansor")
def to_sansor(text):
    words = ['khar', 'asb', 'اسب', 'گاو', 'زباله']
    # sansored_text = ""
    for word in words:
        if word in text:
            text = text.replace(word, len(word) * "*")
    return text


@register.inclusion_tag("partials/active_user.html")
def active_user(count=2):
    active = User.objects.annotate(post_count=Count('user_posts')).order_by('-post_count')[:count]
    context = {
        'active' : active
    }
    return context


@register.simple_tag()
def total_users():
    return User.objects.count()