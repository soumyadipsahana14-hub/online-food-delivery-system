from django.contrib import admin
from .models import Food, Cart, Order, Category


class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'customer_name',
        'food_name',
        'quantity',
        'total_price',
        'payment_method',
        'payment_status',
        'order_status',
        'order_date'
    )


admin.site.register(Food)
admin.site.register(Cart)
admin.site.register(Category)

admin.site.register(Order, OrderAdmin)