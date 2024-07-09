from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
import json

from .models import User, Post, Follow, Like

def remove_like(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=403)
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    Like.objects.filter(user=user, post=post).delete()
    return JsonResponse({"message": "Like removed!"})

def add_like(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=403)
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    Like.objects.get_or_create(user=user, post=post)
    return JsonResponse({"message": "Like added!"})

def edit(request, post_id):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=403)
        data = json.loads(request.body)
        post = get_object_or_404(Post, pk=post_id)
        post.content = data["content"]
        post.save()
        return JsonResponse({"message": "Change successful", "data": post.content})
    return JsonResponse({"error": "Invalid method"}, status=400)

def index(request):
    all_posts = Post.objects.all().order_by("-id")
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    who_you_liked = []
    if request.user.is_authenticated:
        who_you_liked = list(Like.objects.filter(user=request.user).values_list('post_id', flat=True))

    return render(request, "network/index.html", {
        "posts_of_the_page": posts_of_the_page,
        "whoYouLiked": who_you_liked
    })

def new_post(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=403)
        content = request.POST.get('content')
        user = request.user
        Post.objects.create(content=content, user=user)
        return HttpResponseRedirect(reverse("index"))
    return JsonResponse({"error": "Invalid method"}, status=400)

def profile(request, user_id):
    user_profile = get_object_or_404(User, pk=user_id)
    all_posts = Post.objects.filter(user=user_profile).order_by("-id")

    following = Follow.objects.filter(user=user_profile)
    followers = Follow.objects.filter(user_follower=user_profile)

    is_following = request.user.is_authenticated and followers.filter(user=request.user).exists()

    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "posts_of_the_page": posts_of_the_page,
        "username": user_profile.username,
        "following": following,
        "followers": followers,
        "isFollowing": is_following,
        "user_profile": user_profile
    })

def following(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=403)
    current_user = request.user
    following_people = Follow.objects.filter(user=current_user).values_list('user_follower', flat=True)
    following_posts = Post.objects.filter(user__in=following_people).order_by("-id")

    paginator = Paginator(following_posts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts_of_the_page": posts_of_the_page
    })

def follow(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=403)
        userfollow_username = request.POST.get('userfollow')
        current_user = request.user
        user_to_follow = get_object_or_404(User, username=userfollow_username)
        Follow.objects.get_or_create(user=current_user, user_follower=user_to_follow)
        return HttpResponseRedirect(reverse("profile", kwargs={'user_id': user_to_follow.id}))
    return JsonResponse({"error": "Invalid method"}, status=400)

def unfollow(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=403)
        userfollow_username = request.POST.get('userfollow')
        current_user = request.user
        user_to_unfollow = get_object_or_404(User, username=userfollow_username)
        Follow.objects.filter(user=current_user, user_follower=user_to_unfollow).delete()
        return HttpResponseRedirect(reverse("profile", kwargs={'user_id': user_to_unfollow.id}))
    return JsonResponse({"error": "Invalid method"}, status=400)

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    return render(request, "network/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")

        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "network/register.html")
