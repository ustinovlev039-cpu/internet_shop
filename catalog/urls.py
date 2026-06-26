from django.urls import path

from catalog import views

app_name = 'catalog'

urlpatterns = [
    path("", views.ProductListView.as_view(), name="home"),
    path("contacts/", views.contact, name="contacts"),
    path("product/add/", views.ProductCreateView.as_view(), name="product_create"),
    path(
        "product/<int:pk>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ) 
]