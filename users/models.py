import random
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.validators import RegexValidator, URLValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from PIL import Image, ImageDraw, ImageFont

from .managers import UserManager


MAX_NAME_LENGTH = 124
MAX_PHONE_LENGTH = 12
MAX_ABOUT_LENGTH = 256

AVATAR_SIZE = 200
AVATAR_FONT_SIZE = 100

COLOR_RED = "#FF6B6B"
COLOR_TEAL = "#4ECDC4"
COLOR_BLUE = "#45B7D1"
COLOR_GREEN = "#96CEB4"
COLOR_YELLOW = "#FFEAA7"
COLOR_PURPLE = "#DDA0DD"
COLOR_MINT = "#98D8C8"
COLOR_ORANGE = "#F7B731"
COLOR_SKY_BLUE = "#5D9BEC"
COLOR_PINK = "#F47A7A"

AVATAR_COLORS = [
    COLOR_RED, COLOR_TEAL, COLOR_BLUE, COLOR_GREEN, COLOR_YELLOW,
    COLOR_PURPLE, COLOR_MINT, COLOR_ORANGE, COLOR_SKY_BLUE, COLOR_PINK,
]


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=MAX_NAME_LENGTH, verbose_name="Имя")
    surname = models.CharField(max_length=MAX_NAME_LENGTH, verbose_name="Фамилия")
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар"
    )
    phone = models.CharField(
        max_length=MAX_PHONE_LENGTH,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^(\+7|8)?\d{10}$",
                message="Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
            )
        ],
        verbose_name="Телефон"
    )
    github_url = models.URLField(
        blank=True,
        validators=[URLValidator()],
        verbose_name="GitHub"
    )
    about = models.TextField(
        max_length=MAX_ABOUT_LENGTH,
        blank=True,
        verbose_name="О себе"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name="Избранные проекты"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        creating = not self.pk
        if creating and not self.avatar:
            from .utils import generate_avatar
            generate_avatar(self)
        if self.phone:
            if self.phone.startswith("8"):
                self.phone = "+7" + self.phone[1:]
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.name} {self.surname}"
    