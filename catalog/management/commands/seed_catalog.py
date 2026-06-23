from django.core.management import BaseCommand, call_command
from django.db import transaction

from catalog.models import Category, Product


class Command(BaseCommand):
    help = "Удаляет старые категории и товары, затем загружает тестовые данные"

    @transaction.atomic
    def handle(self, *args, **options):
        products_count = Product.objects.count()
        categories_count = Category.objects.count()

        Product.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write(
            f"Удалено товаров: {products_count}; "
            f"категорий: {categories_count}."
        )
        
        call_command(
            "loaddata",
            "catalog_data",
            verbosity=options["verbosity"],
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Тестовые данные успешно загружены. "
                f"Категорий: {Category.objects.count()}; "
                f"товаров: {Product.objects.count()}."
            )
        )