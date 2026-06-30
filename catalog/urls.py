from django.urls import path

from catalog import views


app_name = "catalog"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="home"),
    path("contacts/", views.contact, name="contacts"),
    path(
        "my-products/",
        views.MyProductListView.as_view(),
        name="my_products",
    ),
    path(
        "product/add/",
        views.ProductCreateView.as_view(),
        name="product_create",
    ),
    path(
        "product/<int:pk>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),
    path(
        "product/<int:pk>/edit/",
        views.ProductUpdateView.as_view(),
        name="product_update",
    ),
    path(
        "product/<int:pk>/delete/",
        views.ProductDeleteView.as_view(),
        name="product_delete",
    ),
    path(
        "product/<int:pk>/unpublish/",
        views.ProductUnpublishView.as_view(),
        name="product_unpublish",
    ),
    path(
        "categories/<int:category_id>/",
        views.CategoryProductListView.as_view(),
        name="category_products",
    ),
]
