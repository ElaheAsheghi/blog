from django.shortcuts import render
from django.http import HttpResponse, Http404,HttpResponseRedirect
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect, get_object_or_404
from . forms import *
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank,\
      TrigramSimilarity
from itertools import chain
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views
import random



# Create your views here.
def index(request):
    posts = list(Post.Published.all())
    #many choice
    random_item = random.sample(posts, 1)
    #single choice
    # random_item = random.choice(posts)
    context = {
        'random_item':random_item,
    }
    return render(request, "blog/index.html", context)


def post_list(request, category=None):
    if category is not None:
        posts = Post.Published.filter(category=category)
    else:
        posts = Post.Published.all()
    paginator = Paginator(posts,3)
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = Paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)
    context = {
        'posts':posts,
        'category':category,
    }
    return render(request, "blog/list.html", context)



def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True)
    form = CommentForm()

    context = {
        'post':post,
        'form':form,
        'comments':comments,
    }
    return render(request, "blog/detail.html", context)


def ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket_obj = Ticket.objects.create()
            cd = form.cleaned_data
            ticket_obj.message = cd['message']
            ticket_obj.name = cd['name']
            ticket_obj.email = cd['email']
            ticket_obj.phone = cd['phone']
            ticket_obj.subject = cd['subject']
            ticket_obj.save()
            return redirect("blog:index")
    else:
        form = TicketForm()
    return render(request, "forms/ticket.html", {'form':form})


# @login_required(next='blog:post_detail')
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.name = request.user
        comment.save()
    context = {
        'post':post,
        'form':form,
        'comment':comment,
    }
    return render(request, "forms/comment.html", context)
    

    
# def post(request):
#     if request.method == "POST":
#         form = PostForm(data=request.POST)
#         if form.is_valid():
#             post = form.save()
            
#             return redirect("blog:index")
#     else:
#             form = PostForm()
#     context = {
#         'form': form,
#     }
#     return render(request, "forms/post.html", context)


def post_search(request):
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # results1 = Post.Published.filter(title__icontains=query)
            # results2 = Post.Published.filter(description__icontains=query)
            # results = results1 | results2
            # results = Post.Published.\
            #     filter(Q(title__search=query) | Q(description__search=query))
            # SearchVector
            # results = Post.Published.annotate(search=SearchVector('title', 'description')).\
            # filter(search=query)

            #SearchQuery
            # search_query = SearchQuery(query)
            # results = Post.Published.annotate(search=SearchVector('title', 'description'))\
            #     .filter(search=search_query)

            #SearchRank
            # search_query = SearchQuery(query)
            # search_vector = SearchVector('title', weight='A')\
            #       + SearchVector('description', weight='B')
            # results = Post.Published.annotate(search=search_vector,\
            #                                    rank=SearchRank(search_vector, search_query)).\
            #                                    filter(rank__gt=0.5).order_by('rank')
            
            #TrigramSimilarity
            results1 = Post.Published.annotate(similarity=TrigramSimilarity('title', query))\
            .filter(similarity__gt=0.1)
            results2 = Post.Published.annotate(similarity=TrigramSimilarity('description', query))\
            .filter(similarity__gt=0.1)
            results3 = Image.objects.annotate(similarity=TrigramSimilarity('title', query))\
            .filter(similarity__gt=0.1)
            results4 = Image.objects.annotate(similarity=TrigramSimilarity('description', query))\
            .filter(similarity__gt=0.1)
            posts = (results1 | results2).order_by('similarity')
            images = (results3 | results4).order_by('similarity')
            results = list(chain(posts, images))
            
        context = {
            'query' : query,
            'results' : results,
        }
        return render(request, 'blog/search.html', context)
    

@login_required
def profile(request):
    user = request.user
    posts = Post.Published.filter(author=user)
    paginator = Paginator(posts,5)
    page_number = request.GET.get('page', 1)
    posts = paginator.page(page_number)
    context = {
        'posts' : posts,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def create_post(request):
    if request.method == "POST":
        form = CreatePostForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            img1 = Image.objects.create(image_file=form.cleaned_data['image1'], post=post)
            post.images.add(img1)
            img2 = Image.objects.create(image_file=form.cleaned_data['image2'], post=post)
            post.images.add(img2)
            return redirect('blog:profile')
    else:
        form = CreatePostForm()
    return render(request, 'forms/create_post.html', {'form':form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        post.delete()
        return redirect('blog:profile')
    return render(request, 'forms/delete_post.html', {'post':post})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES, instance=Post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            Image.objects.create(image_file=form.cleaned_data['image1'], post=post)
            Image.objects.create(image_file=form.cleaned_data['image2'], post=post)
            return redirect('blog:profile')
    else:
        form = CreatePostForm(instance=post)
    return render(request, 'forms/create_post.html', {'form':form, 'post':post})


@login_required
def delete_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    image.delete()
    return redirect('blog:profile')
    
    


#view dasti baraye login
# def user_login(request):
#     if request.method == "POST":
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(request, username= cd['username'], password= cd['password'])
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return redirect('blog:profile')
#                 else:
#                     return HttpResponse('your account is disabled!')
#             else:
#                 return HttpResponse('you are not logged in!')
#     else:
#         form = LoginForm()
#     return render(request, 'forms/login.html', {'form':form})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Account.objects.create(user=user)
            return render(request, 'registration/register_done.html', {'user':user})
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form':form})


@login_required
def edit_account(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        account_form = AccountEditForm(request.POST, instance=request.user.account,\
                                       files=request.FILES)
        if account_form.is_valid() and user_form.is_valid():
            account_form.save()
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        account_form = AccountEditForm(instance=request.user.account)
    context = {
        'account_form':account_form,
        'user_form':user_form,
    }
    return render(request, 'registration/edit_account.html', context)


def author_profile(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = post.author
    acc = user.account
    posts = Post.Published.filter(author=user)
    paginator = Paginator(posts,3)
    page_number = request.GET.get('page', 1)
    posts = paginator.page(page_number)
    context = {
        'user':user,
        'post':post,
        'acc':acc,
        'posts':posts,
    }
    return render(request, 'blog/author.html', context)


def show_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments
    context = {
        'comments':comments,
        'post':post,
    }
    return render(request, 'blog/show_comments.html', context)


class UserLoginView(views.LoginView):
    form_class = LoginForm


class UserLogoutView(views.LogoutView):
    form_class = LogoutForm
    




    

