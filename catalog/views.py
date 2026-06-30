<<<<<<< HEAD
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from catalog.forms import ProductForm
from catalog.models import Product

class ProductListView(LoginRequiredMixin, ListView):
=======
from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .models import Product


class ProductListView(ListView):
>>>>>>> a4bd209 (Сделанная rbac)
    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        return (
            Product.objects
            .select_related("category", "owner")
            .filter(
                status=Product.PublicationStatus.PUBLISHED,
            )
            .order_by("-created_at")
        )


class MyProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "catalog/my_products.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        return (
            Product.objects
            .select_related("category")
            .filter(owner=self.request.user)
            .order_by("-created_at")
        )


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.select_related(
            "category",
            "owner",
        )

    def get_object(self, queryset=None):
        product = super().get_object(queryset)

        is_owner = (
            self.request.user.is_authenticated
            and product.owner_id == self.request.user.id
        )

        can_moderate = (
            self.request.user.is_authenticated
            and (
                self.request.user.has_perm(
                    "catalog.can_unpublish_product",
                )
                or self.request.user.has_perm(
                    "catalog.delete_product",
                )
            )
        )

        if (
            product.status != Product.PublicationStatus.PUBLISHED
            and not is_owner
            and not can_moderate
        ):
            raise Http404("Товар не найден.")

        return product


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
<<<<<<< HEAD
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def get_success_url(self):
        return reverse("catalog:product_detail", kwargs={"pk": self.object.pk})


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
=======
    template_name = "catalog/create.html"
    fields = [
        "name",
        "description",
        "image",
        "category",
        "price",
    ]
>>>>>>> a4bd209 (Сделанная rbac)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = Product.PublicationStatus.PENDING

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "catalog:product_detail",
            kwargs={"pk": self.object.pk},
        )


<<<<<<< HEAD
    def get(self, request):
        return render(request, self.template_name, {"success_message": None})

    def post(self, request):
=======
class ProductUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView,
):
    model = Product
    template_name = "catalog/update.html"
    fields = [
        "name",
        "description",
        "image",
        "category",
        "price",
    ]

    def test_func(self):
        product = self.get_object()

        is_owner = product.owner_id == self.request.user.id
        is_moderator = self.request.user.has_perm(
            "catalog.can_unpublish_product",
        )

        return is_owner or is_moderator

    def handle_no_permission(self):
        messages.error(
            self.request,
            "Редактировать товар может только его владелец или модератор.",
        )
        return redirect("catalog:home")

    def get_success_url(self):
        return reverse(
            "catalog:product_detail",
            kwargs={"pk": self.object.pk},
        )


class ProductDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView,
):
    model = Product
    template_name = "catalog/confirm_delete.html"
    context_object_name = "product"

    def test_func(self):
        product = self.get_object()

        is_owner = product.owner_id == self.request.user.id
        is_moderator = self.request.user.has_perm(
            "catalog.delete_product",
        )

        return is_owner or is_moderator

    def handle_no_permission(self):
        messages.error(
            self.request,
            "Удалить товар может только владелец или модератор.",
        )
        return redirect("catalog:home")

    def get_success_url(self):
        product = self.object

        if product.owner_id == self.request.user.id:
            return reverse_lazy("catalog:my_products")

        return reverse_lazy("catalog:home")


class ProductUnpublishView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    View,
):
    permission_required = "catalog.can_unpublish_product"
    raise_exception = True

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        product.status = Product.PublicationStatus.UNPUBLISHED
        product.save(update_fields=["status"])

        messages.success(
            request,
            "Товар снят с публикации.",
        )

        return redirect(
            "catalog:product_detail",
            pk=product.pk,
        )


def contact(request):
    success_message = None

    if request.method == "POST":
>>>>>>> a4bd209 (Сделанная rbac)
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

<<<<<<< HEAD
        success_message = None

        if name and email and message:
            success_message = "Спасибо! Ваше сообщение успешно отправлено. )"
=======
        if name and email and message:
            success_message = (
                "Спасибо! Ваше сообщение успешно отправлено."
            )
>>>>>>> a4bd209 (Сделанная rbac)

    return render(
        request,
        "catalog/contacts.html",
        {
            "success_message": success_message,
        },
    )
