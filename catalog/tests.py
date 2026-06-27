from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from catalog.forms import ProductForm
from catalog.models import Category, Product


class ProductCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Тестовая категория")

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
