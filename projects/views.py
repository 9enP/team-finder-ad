from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView

from team_finder.querystring import pagination_query_prefix

from .forms import ProjectForm
from .models import Project, PROJECT_STATUS_OPEN, PROJECT_STATUS_CLOSED

PROJECTS_PER_PAGE = 12


def paginate_projects(qs, request, per_page=PROJECTS_PER_PAGE):
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page", 1)
    return paginator.get_page(page_number)


class ProjectListView(View):
    def get(self, request):
        qs = Project.objects.all()
        page_obj = paginate_projects(qs, request)
        return render(
            request,
            "projects/project_list.html",
            {
                "projects": page_obj,
                "query_prefix": pagination_query_prefix(request),
            },
        )


class ProjectDetailView(View):
    pk_url_kwarg = "project_pk"

    def get(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk)
        return render(
            request,
            "projects/project-details.html",
            {"project": project},
        )


class CreateProjectView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"
    pk_url_kwarg = "project_pk"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        self.object.participants.add(self.request.user)
        return response

    def get_success_url(self):
        return reverse_lazy(
            "projects:project_detail",
            kwargs={"project_pk": self.object.pk},
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, is_edit=False)


class EditProjectView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"
    pk_url_kwarg = "project_pk"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner != request.user:
            return HttpResponseForbidden(
                "Редактировать проект может только его автор."
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            "projects:project_detail",
            kwargs={"project_pk": self.object.pk},
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, is_edit=True)


class CompleteProjectView(LoginRequiredMixin, View):
    pk_url_kwarg = "project_pk"

    def post(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk)

        if request.user != project.owner:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Завершить проект может только его автор."
                },
                status=403,
            )
        if project.status != PROJECT_STATUS_OPEN:
            return JsonResponse(
                {"status": "error", "message": "Проект уже завершён."},
                status=403,
            )

        project.status = PROJECT_STATUS_CLOSED
        project.save()
        return JsonResponse({"status": "ok", "project_status": project.status})


class ToggleFavoriteView(LoginRequiredMixin, View):
    pk_url_kwarg = "project_pk"

    def post(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk)
        user = request.user
        is_favorited = user.favorites.filter(pk=project.pk).exists()
        if is_favorited:
            user.favorites.remove(project)
        else:
            user.favorites.add(project)
        return JsonResponse({"status": "ok", "favorited": not is_favorited})


class ToggleParticipateView(LoginRequiredMixin, View):
    pk_url_kwarg = "project_pk"

    def post(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk)
        user = request.user
        if user == project.owner:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Автор проекта не может стать его участником."
                },
                status=403,
            )
        is_participant = project.participants.filter(pk=user.pk).exists()
        if is_participant:
            project.participants.remove(user)
        else:
            project.participants.add(user)
        return JsonResponse({"status": "ok", "participating": not is_participant})


class FavoriteProjectsView(LoginRequiredMixin, View):
    def get(self, request):
        qs = request.user.favorites.all()
        return render(
            request,
            "projects/favorite_projects.html",
            {"projects": qs},
        )
