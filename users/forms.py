from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "example@mail.ru",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Придумайте пароль",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Повторите пароль",
            }
        )

        self.fields["email"].label = "Электронная почта"
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Электронная почта",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "example@mail.ru",
                "autofocus": True,
            }
        ),
    )

    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите пароль",
            }
        ),
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "avatar", "phone", "country")

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Имя",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Фамилия",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+7 (900) 000-00-00",
                }
            ),
            "country": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Россия",
                }
            ),
            "avatar": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }

        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "avatar": "Аватар",
            "phone": "Номер телефона",
            "country": "Страна",
        }