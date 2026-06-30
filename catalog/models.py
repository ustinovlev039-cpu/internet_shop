from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Наименование")
    description = models.TextField(blank=True, verbose_name="Описание")
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name
class Product(models.Model):
    class PublicationStatus(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PENDING = "pending", "На модерации"
        PUBLISHED = "published", "Опубликован"
        REJECTED = "rejected", "Отклонён"
        UNPUBLISHED = "unpublished", "Снят с публикации"
    name = models.CharField(max_length=255, db_index=True, verbose_name="Наименование")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to="products/%Y/%m/%d/", blank=True, verbose_name="Изображение")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", verbose_name="Категория")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Цена за покупку",)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    status = models.CharField(max_length=20, choices=PublicationStatus.choices, default=PublicationStatus.PENDING, verbose_name="Статус публикации")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products", verbose_name="Владелец", null=True, blank=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]

        permissions = [("can_unpublish_product", "Может снимать товар с публикации")]

    def __str__(self):
        return self.name
class Contact(models.Model):
    phone = models.CharField("Телефон", max_length=30)
    email = models.EmailField("Email", )
    address = models.CharField("Адрес", max_length=255)
    working_hours = models.CharField("Режим работы", max_length=255)
    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"

    def __str__(self):
        return f"{self.phone} — {self.email}"