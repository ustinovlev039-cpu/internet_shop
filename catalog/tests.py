from decimal import Decimal
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from catalog.forms import ProductForm
from catalog.models import Category, Product
from catalog.services.products import (
    CATEGORY_PRODUCTS_CACHE_TIMEOUT,
    get_category_products_cache_key,
    get_products_by_category,
)
from users.models import CustomUser


TEST_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


@override_settings(CACHES=TEST_CACHES)
class ProductCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Тестовая категория")
        cls.user = CustomUser.objects.create_user(
            email="owner@example.com",
            password="StrongPassword-2026!",
        )

    def setUp(self):
        cache.clear()
        self.client.force_login(self.user)

    def product_data(self, **overrides):
        data = {
            "name": "Тестовый товар",
            "description": "Описание товара",
            "category": self.category.pk,
            "price": "100.00",
        }
        data.update(overrides)
        return data

    def test_product_crud(self):
        create_response = self.client.post(
            reverse("catalog:product_create"),
            self.product_data(),
        )
        product = Product.objects.get(name="Тестовый товар")

        self.assertRedirects(
            create_response,
            reverse("catalog:product_detail", args=[product.pk]),
        )
        self.assertEqual(
            self.client.get(
                reverse("catalog:product_detail", args=[product.pk])
            ).status_code,
            200,
        )

        update_response = self.client.post(
            reverse("catalog:product_update", args=[product.pk]),
            self.product_data(name="Обновлённый товар", price="150.00"),
        )
        product.refresh_from_db()

        self.assertRedirects(
            update_response,
            reverse("catalog:product_detail", args=[product.pk]),
        )
        self.assertEqual(product.name, "Обновлённый товар")
        self.assertEqual(product.price, Decimal("150.00"))

        delete_url = reverse("catalog:product_delete", args=[product.pk])
        self.assertEqual(self.client.get(delete_url).status_code, 200)
        self.assertRedirects(
            self.client.post(delete_url),
            reverse("catalog:home"),
        )
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())

    def test_create_rejects_forbidden_words_regardless_of_case(self):
        response = self.client.post(
            reverse("catalog:product_create"),
            self.product_data(
                name="КАЗИНО",
                description="Совершенно БЕСПЛАТНО",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "запрещённые слова")
        self.assertFalse(Product.objects.exists())

    def test_create_rejects_negative_price_with_clear_error(self):
        response = self.client.post(
            reverse("catalog:product_create"),
            self.product_data(price="-1.00"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Цена не может быть отрицательной. Укажите значение 0 или больше.",
        )
        self.assertFalse(Product.objects.exists())

    def test_existing_image_can_be_kept_and_cleared_during_update(self):
        product = Product.objects.create(
            name="Товар с изображением",
            description="Описание",
            image="products/existing.jpg",
            category=self.category,
            price=Decimal("100.00"),
            owner=self.user,
        )
        update_url = reverse("catalog:product_update", args=[product.pk])

        keep_image_response = self.client.post(
            update_url,
            self.product_data(name=product.name, price="120.00"),
        )
        product.refresh_from_db()

        self.assertRedirects(
            keep_image_response,
            reverse("catalog:product_detail", args=[product.pk]),
        )
        self.assertEqual(product.image.name, "products/existing.jpg")
        self.assertEqual(product.price, Decimal("120.00"))

        clear_image_response = self.client.post(
            update_url,
            self.product_data(
                name=product.name,
                price="120.00",
                **{"image-clear": "on"},
            ),
        )
        product.refresh_from_db()

        self.assertRedirects(
            clear_image_response,
            reverse("catalog:product_detail", args=[product.pk]),
        )
        self.assertFalse(product.image)

    def test_all_widgets_have_bootstrap_styles(self):
        form = ProductForm()

        self.assertIn("form-control", form.fields["name"].widget.attrs["class"])
        self.assertIn(
            "form-control",
            form.fields["description"].widget.attrs["class"],
        )
        self.assertIn("form-control", form.fields["image"].widget.attrs["class"])
        self.assertIn("form-select", form.fields["category"].widget.attrs["class"])
        self.assertIn("form-control", form.fields["price"].widget.attrs["class"])

    def test_image_clear_checkbox_is_styled_as_form_element(self):
        product = Product(
            name="Товар с изображением",
            image="products/existing.jpg",
        )
        image_html = str(ProductForm(instance=product)["image"])

        self.assertIn('type="checkbox"', image_html)
        self.assertIn('class="form-check-input"', image_html)


@override_settings(CACHES=TEST_CACHES)
class CategoryProductCacheTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            email="cache-owner@example.com",
            password="StrongPassword-2026!",
        )
        cls.category = Category.objects.create(name="Кэшируемая категория")
        cls.other_category = Category.objects.create(name="Другая категория")

        cls.product = Product.objects.create(
            name="Опубликованный товар",
            category=cls.category,
            price=Decimal("100.00"),
            owner=cls.user,
            status=Product.PublicationStatus.PUBLISHED,
        )
        Product.objects.create(
            name="Товар на модерации",
            category=cls.category,
            price=Decimal("200.00"),
            owner=cls.user,
            status=Product.PublicationStatus.PENDING,
        )
        Product.objects.create(
            name="Товар другой категории",
            category=cls.other_category,
            price=Decimal("300.00"),
            owner=cls.user,
            status=Product.PublicationStatus.PUBLISHED,
        )

    def setUp(self):
        cache.clear()

    def test_service_uses_category_key_and_timeout(self):
        cache_key = get_category_products_cache_key(self.category.pk)

        with patch(
            "catalog.services.products.cache.set",
            wraps=cache.set,
        ) as cache_set:
            products = get_products_by_category(self.category.pk)

        self.assertEqual([product.pk for product in products], [self.product.pk])
        cache_set.assert_called_once_with(
            cache_key,
            products,
            timeout=CATEGORY_PRODUCTS_CACHE_TIMEOUT,
        )
        self.assertEqual(cache_key, f"category_{self.category.pk}")

        with self.assertNumQueries(0):
            cached_products = get_products_by_category(self.category.pk)

        self.assertEqual(
            [product.pk for product in cached_products],
            [self.product.pk],
        )

    def test_product_save_invalidates_category_cache(self):
        cache_key = get_category_products_cache_key(self.category.pk)
        get_products_by_category(self.category.pk)
        self.assertIsNotNone(cache.get(cache_key))

        self.product.name = "Изменённый товар"
        self.product.save(update_fields=["name"])

        self.assertIsNone(cache.get(cache_key))

    def test_view_uses_service_and_renders_products(self):
        self.client.force_login(self.user)

        with patch(
            "catalog.views.get_products_by_category",
            return_value=[self.product],
        ) as service:
            response = self.client.get(
                reverse(
                    "catalog:category_products",
                    kwargs={"category_id": self.category.pk},
                )
            )

        self.assertEqual(response.status_code, 200)
        service.assert_called_once_with(self.category.pk)
        self.assertContains(response, self.product.name)
