from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("list/", views.ProjectListView.as_view(), name="project_list"),
    path("create-project/", views.CreateProjectView.as_view(), name="create_project"),
    path("favorites/", views.FavoriteProjectsView.as_view(), name="favorites"),
    path("<int:project_pk>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("<int:project_pk>/edit/", views.EditProjectView.as_view(), name="edit_project"),
    path(
        "<int:project_pk>/complete/",
        views.CompleteProjectView.as_view(),
        name="complete_project",
    ),
    path(
        "<int:project_pk>/toggle-favorite/",
        views.ToggleFavoriteView.as_view(),
        name="toggle_favorite",
    ),
    path(
        "<int:project_pk>/toggle-participate/",
        views.ToggleParticipateView.as_view(),
        name="toggle_participate",
    ),
]
