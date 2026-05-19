from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

PROJECT_STATUS_OPEN = "open"
PROJECT_STATUS_CLOSED = "closed"
PROJECT_STATUS_CHOICES = [
    (PROJECT_STATUS_OPEN, _("Открыт")),
    (PROJECT_STATUS_CLOSED, _("Закрыт")),
]

PROJECT_NAME_MAX_LENGTH = 200
PROJECT_STATUS_MAX_LENGTH = max(len(status) for status, _ in PROJECT_STATUS_CHOICES)


class Project(models.Model):
    name = models.CharField(
        max_length=PROJECT_NAME_MAX_LENGTH,
        verbose_name=_("Название"),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Описание"),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name=_("Автор"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания"),
    )
    github_url = models.URLField(
        blank=True,
        default="",
        verbose_name=_("Ссылка на GitHub"),
    )
    status = models.CharField(
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=PROJECT_STATUS_CHOICES,
        default=PROJECT_STATUS_OPEN,
        verbose_name=_("Статус"),
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="participated_projects",
        verbose_name=_("Участники"),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Проект")
        verbose_name_plural = _("Проекты")

    def __str__(self):
        return self.name
