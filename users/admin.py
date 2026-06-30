from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = (
        "email",
        "first_name",
        "last_name",
        "phone",
        "country",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        "country",
    )

    ordering = ("email",)
    
    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone",
        "country",
    )

    fieldsets = (
        (
            "Данные для входа",
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Личная информация",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "avatar",
                    "phone",
                    "country",
                )
            },
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Даты",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            "Создание пользователя",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "avatar",
                    "phone",
                    "country",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )
