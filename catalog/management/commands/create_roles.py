from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from catalog.models import Product


class Command(BaseCommand):
    help = "Создаёт группу модераторов продуктов и назначает ей права."

    def handle(self, *args, **options):
        moderator_group, created = Group.objects.get_or_create(
            name="Модератор продуктов",
        )

        product_content_type = ContentType.objects.get_for_model(Product)

        delete_product_permission = Permission.objects.get(
            content_type=product_content_type,
            codename="delete_product",
        )

        unpublish_product_permission = Permission.objects.get(
            content_type=product_content_type,
            codename="can_unpublish_product",
        )

        moderator_group.permissions.set(
            [
                delete_product_permission,
                unpublish_product_permission,
            ],
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "Группа «Модератор продуктов» создана.",
                ),
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Группа «Модератор продуктов» уже существует.",
                ),
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Группе назначены права: delete_product и "
                "can_unpublish_product.",
            ),
        )
