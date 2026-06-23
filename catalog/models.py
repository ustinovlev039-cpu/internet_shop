from django.core.validators import MinValueValidator
from django.db import models


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
    name = models.CharField(max_length=255, db_index=True, verbose_name="Наименование")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to="products/%Y/%m/%d/", blank=True, verbose_name="Изображение")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", verbose_name="Категория")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Цена за покупку",)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]

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