from django.shortcuts import render, redirect
from .models import Food, Cart, Order, Category
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import razorpay
from django.conf import settings
from django.http import HttpResponse
from reportlab.pdfgen import canvas

def home(request):

    foods = Food.objects.all()

    categories = Category.objects.all()

    category_id = request.GET.get('category')

    if category_id:

        foods = Food.objects.filter(
            category_id=category_id
        )

    search = request.GET.get('search')

    if search:

        foods = Food.objects.filter(
            name__icontains=search
        )

    return render(request,
                  'home.html',
                  {
                      'foods': foods,
                      'categories': categories
                  })

@login_required
def add_to_cart(request, food_id):

    food = Food.objects.get(id=food_id)

    quantity = 1

    total_price = food.price * quantity

    Cart.objects.create(
        food=food,
        quantity=quantity,
        total_price=total_price
    )

    return redirect('cart')

@login_required
def cart(request):

    cart_items = Cart.objects.all()

    grand_total = 0

    for item in cart_items:
        grand_total += item.total_price

    return render(request,
                  'cart.html',
                  {
                      'cart_items': cart_items,
                      'grand_total': grand_total
                  })

def remove_cart_item(request, cart_id):

    item = Cart.objects.get(id=cart_id)

    item.delete()

    return redirect('cart')

def increase_quantity(request, cart_id):

    item = Cart.objects.get(id=cart_id)

    item.quantity += 1

    item.total_price = item.quantity * item.food.price

    item.save()

    return redirect('cart')

def decrease_quantity(request, cart_id):

    item = Cart.objects.get(id=cart_id)

    if item.quantity > 1:

        item.quantity -= 1

        item.total_price = item.quantity * item.food.price

        item.save()

    return redirect('cart')

@login_required
def checkout(request):

    cart_items = Cart.objects.all()

    grand_total = 0

    for item in cart_items:

        grand_total += item.total_price

    if request.method == "POST":

        customer_name = request.POST.get('customer_name')

        phone = request.POST.get('phone')

        address = request.POST.get('address')

        payment_method = request.POST.get('payment_method')

        # CASH ON DELIVERY

        if payment_method == "COD":

            for item in cart_items:

                Order.objects.create(

                    user=request.user,

                    customer_name=customer_name,

                    phone=phone,

                    address=address,

                    food_name=item.food.name,

                    quantity=item.quantity,

                    total_price=item.total_price,

                    payment_method="Cash On Delivery",

                    payment_status="Pending"
                )

            cart_items.delete()

            return render(request,
                          'success.html')

        # ONLINE PAYMENT

        elif payment_method == "ONLINE":

            client = razorpay.Client(
                auth=(
                    settings.RAZORPAY_KEY_ID,
                    settings.RAZORPAY_KEY_SECRET
                )
            )

            payment = client.order.create({

                "amount": grand_total * 100,

                "currency": "INR",

                "payment_capture": "1"
            })

            request.session['customer_name'] = customer_name
            request.session['phone'] = phone
            request.session['address'] = address

            return render(request,
                          'payment.html',
                          {
                              'payment': payment,
                              'grand_total': grand_total,
                              'razorpay_key': settings.RAZORPAY_KEY_ID
                          })

    return render(request,
                  'checkout.html',
                  {
                      'cart_items': cart_items,
                      'grand_total': grand_total
                  })
@login_required
def payment_success(request):

    cart_items = Cart.objects.all()

    customer_name = request.session.get('customer_name')

    phone = request.session.get('phone')

    address = request.session.get('address')

    for item in cart_items:

        Order.objects.create(

            user=request.user,

            customer_name=customer_name,

            phone=phone,

            address=address,

            food_name=item.food.name,

            quantity=item.quantity,

            total_price=item.total_price,

            payment_method="Razorpay",

            payment_status="Paid"
        )

    cart_items.delete()

    return render(request,
                  'success.html')
@login_required
def download_invoice(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-order_date')

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        'attachment; filename="invoice.pdf"'
    )

    p = canvas.Canvas(response)

    # TITLE

    p.setFont("Helvetica-Bold", 22)

    p.drawString(180, 800, " Speed Food Invoice")

    # CUSTOMER INFO

    y = 760

    if orders.exists():

        first_order = orders.first()

        p.setFont("Helvetica", 12)

        p.drawString(
            50,
            y,
            f"Customer: {first_order.customer_name}"
        )

        y -= 20

        p.drawString(
            50,
            y,
            f"Phone: {first_order.phone}"
        )

        y -= 20

        p.drawString(
            50,
            y,
            f"Address: {first_order.address}"
        )

        y -= 40

        # TABLE HEADER

        p.setFont("Helvetica-Bold", 12)

        p.drawString(50, y, "Food")

        p.drawString(220, y, "Qty")

        p.drawString(300, y, "Price")

        p.drawString(420, y, "Payment")

        y -= 20

        total_amount = 0

        p.setFont("Helvetica", 12)

        for order in orders:

            p.drawString(
                50,
                y,
                order.food_name
            )

            p.drawString(
                220,
                y,
                str(order.quantity)
            )

            p.drawString(
                300,
                y,
                f"Rs. {order.total_price}"
            )

            p.drawString(
                420,
                y,
                order.payment_method
            )

            total_amount += order.total_price

            y -= 20

            # PAGE BREAK

            if y < 100:

                p.showPage()

                y = 800

        # GRAND TOTAL

        y -= 20

        p.setFont("Helvetica-Bold", 14)

        p.drawString(
            50,
            y,
            f"Grand Total: Rs. {total_amount}"
        )

    p.save()

    return response

@login_required
def order_history(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-order_date')

    return render(request,
                  'order_history.html',
                  {
                      'orders': orders
                  })

def register_user(request):

    if request.method == "POST":

        username = request.POST.get('username')

        email = request.POST.get('email')

        password = request.POST.get('password')

        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:

            if User.objects.filter(username=username).exists():

                messages.error(request,
                               "Username already exists")

            else:

                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                messages.success(request,
                                 "Registration Successful")

                return redirect('login')

        else:

            messages.error(request,
                           "Passwords do not match")

    return render(request,
                  'register.html')

def login_user(request):

    if request.method == "POST":

        username = request.POST.get('username')

        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('home')

        else:

            messages.error(request,
                           "Invalid Username or Password")

    return render(request,
                  'login.html')

def logout_user(request):

    logout(request)

    return redirect('login')