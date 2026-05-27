from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator, URLValidator
from django.core.exceptions import ValidationError
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
import random
import os


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, name, surname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    AVATAR_COLORS = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
        "#DDA0DD", "#98D8C8", "#F7B731", "#5D9BEC", "#F47A7A"
    ]

    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=124, verbose_name="Имя")
    surname = models.CharField(max_length=124, verbose_name="Фамилия")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="Аватар")
    phone = models.CharField(
        max_length=12,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^(\+7|8)?\d{10}$",
                message="Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
            )
        ],
        verbose_name="Телефон"
    )
    github_url = models.URLField(blank=True, validators=[URLValidator()], verbose_name="GitHub")
    about = models.TextField(max_length=256, blank=True, verbose_name="О себе")
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
            self.generate_avatar()
        if self.phone:
            if self.phone.startswith("8"):
                self.phone = "+7" + self.phone[1:]
        super().save(*args, **kwargs)

    def generate_avatar(self):
        size = (200, 200)
        color = random.choice(self.AVATAR_COLORS)

        image = Image.new("RGB", size, color)
        draw = ImageDraw.Draw(image)

        letter = self.name[0].upper() if self.name else "?"

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)

        draw.text(position, letter, fill="white", font=font)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        self.avatar.save(f"avatar_{self.email}.png", ContentFile(buffer.read()), save=False)
        buffer.close()

    @property
    def full_name(self):
        return f"{self.name} {self.surname}"
    