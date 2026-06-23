from django.contrib import admin

from catalog.models import Category, Producta, Contact

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category')
    list_filter = ('category', )
    search_filter = ('name', 'description')
    readonly_fields = ('create_at',)
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "phone", "email", "address", "working_hours")
    search_fields = ("phone", "email", "address")
