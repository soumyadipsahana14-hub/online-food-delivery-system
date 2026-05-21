from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('add-to-cart/<int:food_id>/',
         views.add_to_cart,
         name='add_to_cart'),

    path('cart/',
         views.cart,
         name='cart'),

    path('remove-cart-item/<int:cart_id>/',
     views.remove_cart_item,
     name='remove_cart_item'),

    path('increase-quantity/<int:cart_id>/',
     views.increase_quantity,
     name='increase_quantity'),

    path('decrease-quantity/<int:cart_id>/',
     views.decrease_quantity,
     name='decrease_quantity'),

    path('checkout/',
     views.checkout,
     name='checkout'),

    path('register/',
     views.register_user,
     name='register'),

    path('login/',
     views.login_user,
     name='login'),

    path('logout/',
     views.logout_user,
     name='logout'),

    path('order-history/',
     views.order_history,
     name='order_history'),

    path('payment-success/',
     views.payment_success,
     name='payment_success'),

    path('download-invoice/',
     views.download_invoice,
     name='download_invoice'),
]