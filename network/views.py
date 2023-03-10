import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from .models import User, Follow, Post, Like
from .forms import NewPostForm


# Error messages
error_message = {
    "login_to_post": "You must be logged in to post.",
    "login_to_view_profile": "You must be logged in to view user profiles.",
    "login_to_view_following": "You must be logged in to posts made by users you follow.",
}


def index(request):
    # Submit POST 
    if request.method == "POST":
        if request.user.is_authenticated:
            f = NewPostForm(request.POST)
            post = f.save(commit=False)

            post.author = request.user
            post.save()
        else:
            return HttpResponse(error_message["login_to_post"])

        return HttpResponseRedirect(reverse("index"))

    # GET posts
    else:
        # Pagination
        post_list = Post.objects.order_by("-datetime")
        paginator = Paginator(post_list, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, "network/index.html", {
            'form': NewPostForm(),
            'page_obj': page_obj,
        })


def login_view(request):

    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, username):

    # Tell user to login to view profiles
    if not request.user.is_authenticated:
        return HttpResponse(error_message["login_to_view_profile"])

    # Get profile User object
    profile_user_obj = get_object_or_404(User, username=username)

    # Does requester follow this profile
    try: 
        Follow.objects.get(user=request.user, followed=profile_user_obj)
        requester_following = True
    except Follow.DoesNotExist:
        requester_following = False

    profile_user_following = Follow.objects.filter(user=profile_user_obj)
    profile_user_followers = Follow.objects.filter(followed=profile_user_obj)

    # Pagination
    post_list = Post.objects.filter(author=profile_user_obj).order_by("-datetime")
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, f"network/profile.html", {
        "profile_user_following": profile_user_following,
        "profile_user_followers": profile_user_followers,
        "profile_user_obj": profile_user_obj,
        "requester_following": requester_following,
        "page_obj": page_obj,
    })


def following(request):

    # Tell user to login to view followed posts
    if not request.user.is_authenticated:
        return HttpResponse(error_message["login_to_view_following"])

    # Get all follow objects with requester as the user
    follow_objs_qset = request.user.following.all()

    # Get all user objects that requester follows
    followed_user_objs = [obj.followed for obj in follow_objs_qset]

    # Pagination
    post_list = Post.objects.filter(author__in=followed_user_objs).order_by("-datetime")
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page_obj": page_obj,
    })


# APIs
@csrf_exempt
@login_required
def follow(request):

    data = json.loads(request.body)
    action = data.get("action")
    target_username = data.get("target_username")

    if action != "follow" and action != "unfollow":
        return JsonResponse({
            "error": f"Must provide action."
        }, status=400)
    
    if target_username == "":
        return JsonResponse({
            "error": f"Must provide target_username to {action}."
        }, status=400)

    # Get target User object
    try:
        target_user_obj = User.objects.get(username=target_username)
    except User.DoesNotExist:
        return JsonResponse({
            "error": f"Account with username '{target_username}' does not exist."
        }, status=400)
    
    # FOLLOW
    if request.method == "PUT" and action == "follow":

        # Create Follow Relationship
        Follow.objects.create(user=request.user, followed=target_user_obj)

        return JsonResponse({"message": f"Followed '{target_username}' successfully"}, status=201)

    # UNFOLLOW
    elif request.method == "DELETE" and action == "unfollow":

        # Delete Follow Relationship
        Follow.objects.get(user=request.user, followed=target_user_obj).delete()

        return JsonResponse({"message": f"Unfollowed '{target_username}' successfully"}, status=200)

    else:
        return JsonResponse({"error": "Request method must be compatible with 'action'."}, status=400)


@login_required
@csrf_exempt
def like(request):

    data = json.loads(request.body)
    action = data.get("action")
    target_post_id = data.get("target_post_id")

    if action != "like" and action != "unlike":
        return JsonResponse({
            "error": f"Must provide action."
        }, status=400)

    if target_post_id == "":
        return JsonResponse({
            "error": f"Must provide post_id to {action}."
        }, status=400)

    try:
        target_post_obj = Post.objects.get(pk=target_post_id)
    except Post.DoesNotExist:
        return JsonResponse({
            "error": f"Post with id '{target_post_id}' does not exist."
        }, status=400)
    except ValueError:
        return JsonResponse({
            "error": f"Post id invalid"
        }, status=400)

    # LIKE
    if request.method == "PUT" and action == "like":

        # Create Like relationship or error
        try:
            Like.objects.create(user=request.user, post=target_post_obj)
            return JsonResponse({
                "message": f"{action} successfull."
            }, status=201)
        except IntegrityError:
            return JsonResponse({
                "error": f"Unable to {action} post."
            }, status=400)
        

    # UNLIKE
    if request.method == "DELETE" and action == "unlike":

        # Delete Like relationship or error
        try:
            Like.objects.get(user=request.user, post=target_post_obj).delete()
            return JsonResponse({
                "message": f"{action} successfull"
                }, status=200)
        except Like.DoesNotExist:
            return JsonResponse({
                "error": f"Post with id '{target_post_id}' does not exist."
            }, status=400)
        except ValueError:
            return JsonResponse({
                "error": f"Post id invalid."
            }, status=400)


@login_required
@csrf_exempt
def edit_post(request):

    data = json.loads(request.body)
    action, target_post_id, content = data.values()

    if action != "edit":
        return JsonResponse({
            "error": f"Must provide action."
        }, status=400)

    if target_post_id == "":
        return JsonResponse({
            "error": f"Must provide post_id to {action}."
        }, status=400)
    
    try:
        target_post_obj = Post.objects.get(pk=target_post_id)
    except Post.DoesNotExist:
        return JsonResponse({
            "error": f"Post with id '{target_post_id}' does not exist."
        }, status=400)
    except ValueError:
        return JsonResponse({
            "error": f"Post id invalid."
        })

    if request.user != target_post_obj.author:
        return JsonResponse({
            "error": f"Unable to {action} post."
        })
    
    if content == "":
        return JsonResponse({
            "error": f"Must provide content to {action}"
        })
    
    if content == target_post_obj.content:
        return JsonResponse({
            "error": f"New content must not be the same as existing content."
        })
    
    target_post_obj.content = content
    target_post_obj.save()

    return JsonResponse({
        "message": f"{action} successfull"
    }, status=202)