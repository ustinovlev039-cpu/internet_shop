from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from catalog.forms import ProductForm
from catalog.models import Category, Product
from catalog.services.products import (
    get_products_by_category,
    get_published_products,
)


class ProductListView(LoginRequiredMixin, ListView):
    template_name = "catalog/home.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        return get_published_products()


class CategoryProductListView(LoginRequiredMixin, ListView):
    template_name = "catalog/category_products.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            pk=self.kwargs["category_id"],
        )

        return get_products_by_category(self.category.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category

        return context


@method_decorator(
    cache_page(60 * 5, key_prefix="catalog_product_detail"),
    name="dispatch",
)
@method_decorator(vary_on_cookie, name="dispatch")
class ProductDetailView(LoginRequiredMixin, DetailView):
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


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = Product.PublicationStatus.PENDING

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "catalog:product_detail",
            kwargs={"pk": self.object.pk},
        )


class ProductUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView,
):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def test_func(self):
        product = self.get_object()

        return (
            product.owner_id == self.request.user.id
            or self.request.user.has_perm(
                "catalog.can_unpublish_product"
            )
        )

    def handle_no_permission(self):
        messages.error(
            self.request,
            "Редактировать товар может только его владелец или модератор.",
        )
        return redirect("catalog:home")

    def form_valid(self, form):
        form.instance.status = Product.PublicationStatus.PENDING

        return super().form_valid(form)

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
    template_name = "catalog/product_confirm_delete.html"
    context_object_name = "product"
    success_url = reverse_lazy("catalog:home")

    def test_func(self):
        product = self.get_object()

        return (
            product.owner_id == self.request.user.id
            or self.request.user.has_perm("catalog.delete_product")
        )

    def handle_no_permission(self):
        messages.error(
            self.request,
            "Удалить товар может только его владелец или модератор.",
        )
        return redirect("catalog:home")


class ProductUnpublishView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    View,
):
    permission_required = "catalog.can_unpublish_product"
    raise_exception = True

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied

        return redirect_to_login(
            self.request.get_full_path(),
            self.get_login_url(),
            self.get_redirect_field_name(),
        )

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.status = Product.PublicationStatus.UNPUBLISHED
        product.save(update_fields=["status"])

        messages.success(request, "Товар снят с публикации.")

        return redirect("catalog:product_detail", pk=product.pk)


@login_required
def contact(request):
    success_message = None

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if name and email and message:
            success_message = (
                "Спасибо! Ваше сообщение успешно отправлено."
            )

    return render(
        request,
        "catalog/contacts.html",
        {
            "success_message": success_message,
        },
    )
