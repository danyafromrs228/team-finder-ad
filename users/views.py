from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
from .forms import UserRegistrationForm, UserLoginForm, UserProfileEditForm, UserChangePasswordForm
from .models import User


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:list")
    else:
        form = UserRegistrationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            return redirect("projects:list")
    else:
        form = UserLoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail_view(request, user_id):
    user = get_object_or_404(User, id=user_id, is_active=True)
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = UserProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = UserProfileEditForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = UserChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = UserChangePasswordForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def users_list_view(request):
    users = User.objects.filter(is_active=True)
    active_filter = request.GET.get("filter")

    if request.user.is_authenticated and active_filter:
        if active_filter == "owners-of-favorite-projects":
            favorite_projects = request.user.favorites.all()
            users = User.objects.filter(owned_projects__in=favorite_projects).distinct()
        elif active_filter == "owners-of-participating-projects":
            participating_projects = request.user.participated_projects.all()
            users = User.objects.filter(owned_projects__in=participating_projects).distinct()
        elif active_filter == "interested-in-my-projects":
            my_projects = request.user.owned_projects.all()
            users = User.objects.filter(favorites__in=my_projects).distinct()
        elif active_filter == "participants-of-my-projects":
            my_projects = request.user.owned_projects.all()
            users = User.objects.filter(participated_projects__in=my_projects).distinct()

    paginator = Paginator(users, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    query_prefix = f"filter={active_filter}&" if active_filter else ""

    return render(request, "users/participants.html", {
        "page_obj": page_obj,
        "active_filter": active_filter,
        "query_prefix": query_prefix,
    })
    