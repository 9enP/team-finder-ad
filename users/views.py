from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView

from team_finder.querystring import pagination_query_prefix

from .forms import (
    ChangePasswordForm,
    EditProfileForm,
    LoginForm,
    RegisterForm,
)
from .models import User

USERS_PER_PAGE = 12


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("projects:project_list")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.save()
        login(self.request, user)
        return redirect(self.success_url)


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
                return redirect("projects:project_list")
            form.add_error(None, "Неверный имейл или пароль")
        return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:project_list")


class UserDetailView(View):
    def get(self, request, user_pk):
        user = get_object_or_404(User, pk=user_pk)
        return render(request, "users/user-details.html", {"user": user})


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = "users/edit_profile.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return redirect("users:user_detail", user_pk=self.request.user.pk)


class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request, user_pk):
        if request.user.pk != user_pk:
            return redirect("users:user_detail", user_pk=user_pk)
        form = ChangePasswordForm(user=request.user)
        return render(request, "users/change_password.html", {"form": form})

    def post(self, request, user_pk):
        if request.user.pk != user_pk:
            return redirect("users:user_detail", user_pk=user_pk)
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            login(request, request.user)
            return redirect("users:user_detail", user_pk=user_pk)
        return render(request, "users/change_password.html", {"form": form})


class ParticipantsView(View):
    def get(self, request):
        filter_value = request.GET.get("filter", "")
        qs = User.objects.filter(is_active=True)

        if request.user.is_authenticated and filter_value:
            if filter_value == "fav_authors":
                qs = User.objects.filter(
                    owned_projects__in=request.user.favorites.all(),
                    is_active=True,
                ).distinct()
            elif filter_value == "participating":
                qs = User.objects.filter(
                    owned_projects__participants=request.user,
                    is_active=True,
                ).distinct()
            elif filter_value == "fans":
                qs = User.objects.filter(
                    favorites__in=request.user.owned_projects.all(),
                    is_active=True,
                ).distinct()
            elif filter_value == "my_participants":
                qs = (
                    User.objects.filter(
                        participated_projects__in=request.user.owned_projects.all(),
                        is_active=True,
                    )
                    .exclude(pk=request.user.pk)
                    .distinct()
                )

        paginator = Paginator(qs, USERS_PER_PAGE)
        page_number = request.GET.get("page", 1)
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
