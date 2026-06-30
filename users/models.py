from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Для пользователя необходимо указать email.")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields,)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Для суперпользователя is_staff должен быть True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Для суперпользователя is_superuser должен быть True.")

        return self.create_user(
            email=email,
            password=password,
            **extra_fields,
        )


class CustomUser(AbstractUser):
    username = None

    email = models.EmailField(unique=True, verbose_name="электронная почта")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="аватар")
    phone = models.CharField(max_length=30, blank=True, verbose_name="номер телефона")
    country = models.CharField(max_length=100, blank=True, verbose_name="страна")

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.email