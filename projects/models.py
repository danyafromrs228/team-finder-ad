from django.db import models
from django.conf import settings


MAX_NAME_LENGTH = 200
MAX_STATUS_LENGTH = 6

STATUS_OPEN = "open"
STATUS_CLOSED = "closed"

STATUS_CHOICES = [
    (STATUS_OPEN, "Открыт"),
    (STATUS_CLOSED, "Закрыт"),
]


class Project(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name="Название"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    github_url = models.URLField(
        blank=True,
        verbose_name="GitHub"
    )
    status = models.CharField(
        max_length=MAX_STATUS_LENGTH,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
        verbose_name="Статус"
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники"
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
    