from django.shortcuts import render

from django.shortcuts import render\

def home(request):
    return render(request, "catalog/home.html")

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