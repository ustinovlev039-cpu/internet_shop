from unittest.mock import patch

from django.core import mail
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from users.models import CustomUser
from users.services import WelcomeEmailError


class AnonymousAccessTests(SimpleTestCase):
    protected_urls = (
        ("catalog:home", None),
        ("catalog:contacts", None),
        ("catalog:product_create", None),
        ("catalog:product_detail", {"pk": 1}),
        ("catalog:category_products", {"category_id": 1}),
        ("catalog:product_unpublish", {"pk": 1}),
        ("blog:post_list", None),
        ("blog:post_detail", {"pk": 1}),
        ("blog:manage_list", None),
        ("blog:manage_create", None),
        ("blog:manage_detail", {"pk": 1}),
        ("blog:manage_update", {"pk": 1}),
        ("blog:manage_delete", {"pk": 1}),
        ("users:logout", None),
        ("users:profile", None),
    )

    def test_protected_endpoints_redirect_to_login(self):
        for url_name, kwargs in self.protected_urls:
            with self.subTest(url_name=url_name):
                url = reverse(url_name, kwargs=kwargs)
                response = self.client.get(url)

                self.assertRedirects(
                    response,
                    f"{reverse('users:login')}?next={url}",
                    fetch_redirect_response=False,
                )

    def test_registration_and_login_are_public(self):
        for url_name in ("users:register", "users:login"):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))

                self.assertEqual(response.status_code, 200)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class RegistrationTests(TestCase):
    registration_data = {
        "email": "customer@example.com",
        "password1": "StrongPassword-2026!",
        "password2": "StrongPassword-2026!",
    }

    def test_registration_creates_and_authenticates_user(self):
        response = self.client.post(
            reverse("users:register"),
            data=self.registration_data,
        )

        user = CustomUser.objects.get(email=self.registration_data["email"])
        self.assertRedirects(response, reverse("catalog:home"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [user.email])

    def test_registration_rolls_back_when_email_sending_fails(self):
        with (
            self.assertLogs("users.views", level="ERROR"),
            patch(
                "users.views.send_welcome_email",
                side_effect=WelcomeEmailError,
            ),
        ):
            response = self.client.post(
                reverse("users:register"),
                data=self.registration_data,
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Не удалось отправить письмо")
        self.assertFalse(
            CustomUser.objects.filter(
                email=self.registration_data["email"],
            ).exists()
        )
        self.assertNotIn("_auth_user_id", self.client.session)


class AuthenticationTests(TestCase):
    email = "customer@example.com"
    password = "StrongPassword-2026!"

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email=self.email,
            password=self.password,
        )

    def test_user_can_log_in_with_email_and_password(self):
        response = self.client.post(
            reverse("users:login"),
            data={"username": self.email, "password": self.password},
        )

        self.assertRedirects(response, reverse("catalog:home"))
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.user.pk,
        )

    def test_invalid_credentials_are_shown_to_user(self):
        response = self.client.post(
            reverse("users:login"),
            data={"username": self.email, "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertNotIn("_auth_user_id", self.client.session)
