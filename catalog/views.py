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
    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        return Product.objects.select_related("category").order_by("-created_at")

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product 
    template_name = "catalog/detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.select_related("category")
    
class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def get_success_url(self):
        return reverse("catalog:product_detail", kwargs={"pk": self.object.pk})


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def get_success_url(self):
        return reverse("catalog:product_detail", kwargs={"pk": self.object.pk})

class ContactView(LoginRequiredMixin, View):
    template_name = "catalog/contacts.html"

    def get(self, request):
        return render(request, self.template_name, {"success_message": None})

    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        success_message = None

        if name and email and message:
            success_message = "Спасибо! Ваше сообщение успешно отправлено. )"

        return render(request, self.template_name, {"success_message": success_message})
