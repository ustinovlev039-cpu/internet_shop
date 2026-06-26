from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView


from catalog.models import Product

class ProductListView(ListView):
    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        return Product.objects.select_related("category").order_by("-created_at")

class ProductDetailView(DetailView):
    model = Product 
    template_name = "catalog/detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.select_related("category")
    
class ProductCreateView(CreateView):
    model = Product
    template_name = "catalog/create.html"
    fields = [
        "name", 
        "description", 
        "image", 
        "category", 
        "price"
    ]

    def get_success_url(self):
        return reverse("catalog:product_detail", kwargs={"pk": self.object.pk})


def contact(request):
    success_message = None

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if name and email and message:
            success_message = "Спасибо! Ваше сообщение успешно отправлено."

    context = {
        "success_message": success_message
    }

    return render(request, "catalog/contacts.html", context)