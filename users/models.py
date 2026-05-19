import random
import uuid
from io import BytesIO

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.files import File
from django.db import models
from PIL import Image, ImageDraw, ImageFont

AVATAR_BG_COLORS = [
    "#4A90D9",
    "#7B68EE",
    "#5CB85C",
    "#E8A838",
    "#D9534F",
    "#1ABC9C",
    "#9B59B6",
    "#E67E22",
    "#2ECC71",
    "#3498DB",
]

# Константы длин полей из ТЗ
MAX_LENGTH_NAME = 124
MAX_LENGTH_SURNAME = 124
MAX_LENGTH_PHONE = 12
MAX_LENGTH_ABOUT = 256
MAX_LENGTH_PROJECT_NAME = 200


def _load_avatar_font(size: int):
    font_paths = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:\\Windows\\Fonts\\arial.ttf",
    )
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _render_avatar_png(name: str):
    letter = ((name or "").strip()[:1] or "?").upper()
    img = Image.new("RGB", (200, 200), random.choice(AVATAR_BG_COLORS))
    draw = ImageDraw.Draw(img)
    font = _load_avatar_font(100)
    draw.text((100, 100), letter, fill="#FFFFFF", font=font, anchor="mm")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    filename = f"avatar_{uuid.uuid4()}.png"
    return buffer, filename


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        buffer, filename = _render_avatar_png(name)
        user.avatar.save(filename, File(buffer), save=False)
        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, name, surname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=MAX_LENGTH_NAME)
    surname = models.CharField(max_length=MAX_LENGTH_SURNAME)
    avatar = models.ImageField(upload_to="avatars/")
    phone = models.CharField(max_length=MAX_LENGTH_PHONE, default="")
    github_url = models.URLField(blank=True, default="")
    about = models.TextField(max_length=MAX_LENGTH_ABOUT, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    favorites = models.ManyToManyField(
        "projects.Project",
        blank=True,
        related_name="interested_users",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return f"{self.name} {self.surname}"

    def get_full_name(self):
        return f"{self.name} {self.surname}"
