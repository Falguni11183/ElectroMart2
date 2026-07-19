from django.contrib import admin
from .models import Product, Customer, Order, OrderItem, Review, Wishlist

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "total_amount", "status", "order_date")
    list_filter = ("status",)
    search_fields = ("customer__fullname",)

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Wishlist)