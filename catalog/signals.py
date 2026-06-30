from django.core.cache import cache
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from catalog.models import Product
from catalog.services.products import (
    PRODUCT_LIST_CACHE_KEY,
    get_category_products_cache_key,
)


@receiver(pre_save, sender=Product)
def remember_previous_product_category(sender, instance, **kwargs):
    if instance.pk:
        instance._previous_category_id = (
            sender.objects
            .filter(pk=instance.pk)
            .values_list("category_id", flat=True)
            .first()
        )


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def clear_product_list_cache(sender, instance, **kwargs):
    cache_keys = {
        PRODUCT_LIST_CACHE_KEY,
        get_category_products_cache_key(instance.category_id),
    }
    previous_category_id = getattr(instance, "_previous_category_id", None)

    if previous_category_id:
        cache_keys.add(
            get_category_products_cache_key(previous_category_id)
        )

    cache.delete_many(cache_keys)
