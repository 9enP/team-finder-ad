from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from team_finder.querystring import pagination_query_prefix

from .forms import ChangePasswordForm, EditProfileForm, LoginForm, RegisterForm
from .models import User


class RegisterView(View):
    def get(self, request):
        return render(request, "users/register.html", {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.cleaned_data["email"],
                name=form.cleaned_data["name"],
                surname=form.cleaned_data["surname"],
                password=form.cleaned_data["password"],
            )
            login(request, user)
            return redirect("/projects/list/")
        return render(request, "users/register.html", {"form": form})


class LoginView(View):
    def get(self, request):
        return render(request, "users/login.html", {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user is not None and user.is_active:
                login(request, user)
                return redirect("/projects/list/")
            form.add_error(None, "Неверный имейл или пароль")
        return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("/projects/list/")


class UserDetailView(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        return render(request, "users/user-details.html", {"user": user})


class EditProfileView(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def get(self, request, pk):
        if request.user.pk != pk:
            return redirect("users:user_detail", pk=pk)
        form = EditProfileForm(instance=request.user)
        return render(
            request,
            "users/edit_profile.html",
            {"form": form, "user": request.user},
        )

    def post(self, request, pk):
        if request.user.pk != pk:
            return redirect("users:user_detail", pk=pk)
        form = EditProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )
        if form.is_valid():
            form.save()
            return redirect(f"/users/{pk}/")
        return render(
            request,
            "users/edit_profile.html",
            {"form": form, "user": request.user},
        )


class ChangePasswordView(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def get(self, request, pk):
        if request.user.pk != pk:
            return redirect("users:user_detail", pk=pk)
        form = ChangePasswordForm(user=request.user)
        return render(
            request,
            "users/change_password.html",
            {"form": form},
        )

    def post(self, request, pk):
        if request.user.pk != pk:
            return redirect("users:user_detail", pk=pk)
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data["new_password1"])
            request.user.save()
            login(request, request.user)
            return redirect(f"/users/{pk}/")
        return render(request, "users/change_password.html", {"form": form})


class ParticipantsView(View):
    def get(self, request):
        filter_value = ""
        qs = User.objects.filter(is_active=True).order_by("id")
        if request.user.is_authenticated and "filter" in request.GET:
            filter_value = request.GET.get("filter") or ""
            if filter_value == "fav_authors":
                qs = (
                    User.objects.filter(
                        owned_projects__in=request.user.favorites.all()
                    )
                    .filter(is_active=True)
                    .order_by("id")
                    .distinct()
                )
            elif filter_value == "participating":
                qs = (
                    User.objects.filter(
                        owned_projects__participants=request.user
                    )
                    .filter(is_active=True)
                    .order_by("id")
                    .distinct()
                )
            elif filter_value == "fans":
                qs = (
                    User.objects.filter(
                        favorites__in=request.user.owned_projects.all()
                    )
                    .filter(is_active=True)
                    .order_by("id")
                    .distinct()
                )
            elif filter_value == "my_participants":
                qs = (
                    User.objects.filter(
                        participated_projects__in=request.user.owned_projects.all()
                    )
                    .exclude(pk=request.user.pk)
                    .filter(is_active=True)
                    .order_by("id")
                    .distinct()
                )

        paginator = Paginator(qs, 12)
        page_number = request.GET.get("page") or 1
        page_obj = paginator.get_page(page_number)
        return render(
            request,
            "users/participants.html",
            {
                "participants": page_obj,
                "active_filter": filter_value,
                "query_prefix": pagination_query_prefix(request),
            },
        )
