from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("list/", views.ParticipantsView.as_view(), name="participants"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    path("<int:pk>/edit/", views.EditProfileView.as_view(), name="edit_profile"),
    path(
        "<int:pk>/change-password/",
        views.ChangePasswordView.as_view(),
        name="change_password",
    ),
]
