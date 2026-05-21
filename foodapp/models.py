from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):

        return self.name
    

class Food(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True
    )

    name = models.CharField(max_length=100)

    price = models.IntegerField()

    description = models.TextField()

    image = models.ImageField(upload_to='foods/')

    def __str__(self):

        return self.name

class Cart(models.Model):

    food = models.ForeignKey(Food, on_delete=models.CASCADE)

    quantity = models.IntegerField(default=1)

    total_price = models.IntegerField()

    def __str__(self):
        return self.food.name
    
class Order(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )

    customer_name = models.CharField(max_length=100)

    phone = models.CharField(max_length=15)

    address = models.TextField()

    food_name = models.CharField(max_length=100)

    quantity = models.IntegerField()

    total_price = models.IntegerField()

    payment_method = models.CharField(
        max_length=50,
        null=True
    )

    payment_status = models.CharField(
        max_length=50,
        default='Pending'
    )

    order_status = models.CharField(
    max_length=50,
    default='Pending'
    )
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return self.customer_name