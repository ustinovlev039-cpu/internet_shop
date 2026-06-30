from django.core.cache import cache

from catalog.models import Product


PRODUCT_LIST_CACHE_KEY = "catalog:published_products"
PRODUCT_LIST_CACHE_TIMEOUT = 60 * 5
CATEGORY_PRODUCTS_CACHE_KEY_TEMPLATE = "category_{category_id}"
CATEGORY_PRODUCTS_CACHE_TIMEOUT = 60 * 5


def get_category_products_cache_key(category_id: int) -> str:
    return CATEGORY_PRODUCTS_CACHE_KEY_TEMPLATE.format(category_id=category_id)


def get_published_products():
    products = cache.get(PRODUCT_LIST_CACHE_KEY)

    if products is None:
        products = list(
            Product.objects
            .select_related("category", "owner")
            .filter(
                status=Product.PublicationStatus.PUBLISHED,
            )
            .order_by("-created_at")
        )

        cache.set(
            PRODUCT_LIST_CACHE_KEY,
            products,
            timeout=PRODUCT_LIST_CACHE_TIMEOUT,
        )

    return products


def get_products_by_category(category_id: int):
    cache_key = get_category_products_cache_key(category_id)
    products = cache.get(cache_key)

    if products is None:
        products = list(
            Product.objects
            .select_related("category", "owner")
            .filter(
                category_id=category_id,
                status=Product.PublicationStatus.PUBLISHED,
            )
            .order_by("-created_at")
        )

        cache.set(
            cache_key,
            products,
            timeout=CATEGORY_PRODUCTS_CACHE_TIMEOUT,
        )

    return products
