from django.db import migrations


def create_product_moderator_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    product_content_type, _ = ContentType.objects.get_or_create(
        app_label="catalog",
        model="product",
    )

    delete_permission, _ = Permission.objects.get_or_create(
        content_type=product_content_type,
        codename="delete_product",
        defaults={"name": "Может удалять товар"},
    )
    unpublish_permission, _ = Permission.objects.get_or_create(
        content_type=product_content_type,
        codename="can_unpublish_product",
        defaults={"name": "Может снимать товар с публикации"},
    )

    moderator_group, _ = Group.objects.get_or_create(
        name="Модератор продуктов",
    )
    moderator_group.permissions.add(
        delete_permission,
        unpublish_permission,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("catalog", "0003_alter_product_options_product_owner_product_status"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(
            create_product_moderator_group,
            migrations.RunPython.noop,
        ),
    ]
