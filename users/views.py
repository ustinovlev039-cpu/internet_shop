import logging

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import (
    EmailAuthenticationForm,
    RegisterUserForm,
    UserProfileForm,
)
from users.models import CustomUser
from users.services import WelcomeEmailError, send_welcome_email


logger = logging.getLogger(__name__)


class RegisterView(CreateView):
    model = CustomUser
    form_class = RegisterUserForm
    template_name = "users/register.html"
    success_url = reverse_lazy("catalog:home")

    def form_valid(self, form):
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                send_welcome_email(self.object)
        except WelcomeEmailError:
            logger.exception("Не удалось отправить приветственное письмо.")
            form.add_error(
                None,
                "Не удалось отправить письмо. Попробуйте зарегистрироваться позже.",
            )
            return self.form_invalid(form)

        login(self.request, self.object)

        messages.success(
            self.request,
            "Регистрация успешно завершена. Добро пожаловать!",
        )

        return response


class UserLoginView(auth_views.LoginView):
    template_name = "users/login.html"
    authentication_form = EmailAuthenticationForm

    def form_valid(self, form):
        messages.success(
            self.request,
            "Вы успешно вошли в аккаунт.",
        )
        return super().form_valid(form)


class UserLogoutView(LoginRequiredMixin, auth_views.LogoutView):
    next_page = reverse_lazy("catalog:home")


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(
            self.request,
            "Профиль успешно обновлён.",
        )
        return super().form_valid(form)
