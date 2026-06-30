from django.conf import settings
from django.core.mail import send_mail


class WelcomeEmailError(Exception):
    """Raised when a welcome email cannot be sent."""


def send_welcome_email(user):
    try:
        return send_mail(
            subject="Добро пожаловать в интернет-магазин!",
            message=(
                f"Здравствуйте, {user.email}!\n\n"
                "Спасибо за регистрацию в нашем интернет-магазине. "
                "Теперь вы можете войти в аккаунт и пользоваться "
                "доступными функциями сайта."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as error:
        raise WelcomeEmailError(
            "Не удалось отправить приветственное письмо."
        ) from error
