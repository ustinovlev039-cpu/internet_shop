from django.urls import path

from . import views


app_name = "catalog"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="home"),
<<<<<<< HEAD
    path("contacts/", views.ContactView.as_view(), name="contacts"),
    path("product/add/", views.ProductCreateView.as_view(), name="product_create"),
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
]
=======
    path("products/add/", views.ProductCreateView.as_view(), name="product_create"),
    path("my-products/", views.MyProductListView.as_view(), name="my_products"),
    path("products/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
    path("products/<int:pk>/unpublish/", views.ProductUnpublishView.as_view(), name="product_unpublish"),
    path("products/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("contacts/", views.contact, name="contacts")
]
>>>>>>> a4bd209 (Сделанная rbac)
