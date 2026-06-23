from django.shortcuts import render

from django.shortcuts import render\

from catalog.models import Contact, Product

def home(request):
    latest_products = Product.objects.order_by("-created_at")[:5]

    print("/nПоследние 5 созданий продуктов:")
    for product in latest_products:
        print(
            f"id={product.id}"
            f"name={product.name}"
            f"price={product.price}"
            f"created_at={product.created_at}"
        )
    
    return render(request, "catalog/home.html", {"latest_products": latest_products})

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