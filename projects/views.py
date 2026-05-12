from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from team_finder.querystring import pagination_query_prefix

from .forms import ProjectForm
from .models import Project


class ProjectListView(View):
    def get(self, request):
        qs = Project.objects.all().order_by("-created_at")
        paginator = Paginator(qs, 12)
        page_number = request.GET.get("page") or 1
        page_obj = paginator.get_page(page_number)
        return render(
            request,
            "projects/project_list.html",
            {
                "projects": page_obj,
                "query_prefix": pagination_query_prefix(request),
            },
        )


class ProjectDetailView(View):
    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        return render(
            request,
            "projects/project-details.html",
            {"project": project},
        )


class CreateProjectView(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def get(self, request):
        return render(
            request,
            "projects/create-project.html",
            {"form": ProjectForm(), "is_edit": False},
        )

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f"/projects/{project.pk}/")
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": False},
        )


class EditProjectView(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if project.owner != request.user:
            return HttpResponseForbidden()
        return render(
            request,
            "projects/create-project.html",
            {
                "form": ProjectForm(instance=project),
                "is_edit": True,
            },
        )

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if project.owner != request.user:
            return HttpResponseForbidden()
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f"/projects/{project.pk}/")
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": True},
        )


class CompleteProjectView(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if request.user != project.owner or project.status != "open":
            return JsonResponse({"status": "error"}, status=403)
        project.status = "closed"
        project.save()
        return JsonResponse({"status": "ok", "project_status": "closed"})


class ToggleFavoriteView(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        user = request.user
        if project in user.favorites.all():
            user.favorites.remove(project)
            favorited = False
        else:
            user.favorites.add(project)
            favorited = True
        return JsonResponse({"status": "ok", "favorited": favorited})


class ToggleParticipateView(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        user = request.user
        if user == project.owner:
            return JsonResponse({"status": "error"}, status=403)
        if user in project.participants.all():
            project.participants.remove(user)
            participating = False
        else:
            project.participants.add(user)
            participating = True
        return JsonResponse({"status": "ok", "participating": participating})


class FavoriteProjectsView(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def get(self, request):
        qs = request.user.favorites.all().order_by("-created_at")
        return render(
            request,
            "projects/favorite_projects.html",
            {"projects": qs},
        )
