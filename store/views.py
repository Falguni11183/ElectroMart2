from django.db.models import Q
from django.shortcuts import render, redirect
from .models import Product
from .models import Product, Customer, Order, OrderItem
from .models import Customer
from .models import Wishlist
from .models import Customer, Product, Order, Review
import csv
from django.http import HttpResponse
from .models import Order
import re
from django.contrib import messages
import threading
import time
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProductSerializer

def home(request):
    products = Product.objects.all()[:3]   

    return render(request, "index.html", {
        "products": products
    })

def login_page(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            customer = Customer.objects.get(
                email=email,
                password=password
            )

            request.session["customer_id"] = customer.id
            request.session["customer_name"] = customer.fullname

            return redirect("products")

        except Customer.DoesNotExist:
            return render(request, "login.html", {
                "error": "Invalid Email or Password"
            })

    return render(request, "login.html")


def register_page(request):

    if request.method == "POST":

        print(request.POST)

        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        name_pattern = r'^[A-Za-z ]{3,50}$'
        if not re.match(name_pattern, fullname):
            messages.error(request, "Enter a valid full name.")
            return redirect("register")

        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(email_pattern, email):
            messages.error(request, "Invalid Email Address.")
            return redirect("register")

        phone_pattern = r'^[6-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            messages.error(request, "Invalid Mobile Number.")
            return redirect("register")

        
        password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+=!]).{8,}$'
        if not re.match(password_pattern, password):
            messages.error(
                request,
                "Password must contain at least 8 characters, one uppercase, one lowercase, one number and one special character."
            )
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if Customer.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        if Customer.objects.filter(phone=phone).exists():
            messages.error(request, "Mobile number already registered.")
            return redirect("register")

        
        Customer.objects.create(
            fullname=fullname,
            email=email,
            phone=phone,
            password=password
        )

        print("Customer Saved Successfully")

        messages.success(request, "Registration Successful. Please Login.")
        return redirect("login")

    return render(request, "register.html")



def products(request):

    search = request.GET.get("search")
    category = request.GET.get("category")

    products = Product.objects.all()

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    if category:
        products = products.filter(category=category)

    categories = Product.objects.values_list(
        "category",
        flat=True
    ).distinct()

    wishlist_product_ids = []

    if "customer_id" in request.session:

        wishlist_product_ids = Wishlist.objects.filter(
            customer_id=request.session["customer_id"]
        ).values_list("product_id", flat=True)

    return render(request, "products.html", {

        "products": products,

        "categories": categories,

        "wishlist_product_ids": wishlist_product_ids

    })


def cart(request):

    cart = request.session.get("cart", [])

    products = Product.objects.filter(id__in=cart)

    grand_total = 0

    for product in products:
        grand_total += product.price

    return render(request, "cart.html", {
        "products": products,
        "grand_total": grand_total
    })
def send_order_notification(customer_name):
    time.sleep(3)   

    print("===================================")
    print("ORDER CONFIRMATION")
    print(f"Notification sent to {customer_name}")
    print("===================================")

def checkout(request):

    if "customer_id" not in request.session:
        return redirect("login")

    if request.method == "POST":

        customer = Customer.objects.get(
            id=request.session["customer_id"]
        )

        cart = request.session.get("cart", [])

        products = Product.objects.filter(id__in=cart)

        total = sum(product.price for product in products)

        address = request.POST.get("address")
        phone = request.POST.get("phone")
        pincode = request.POST.get("pincode")
        payment = request.POST.get("payment")

        
        
        if len(address.strip()) < 10:
            messages.error(request, "Please enter a valid address.")
            return redirect("checkout")

        phone_pattern = r'^[6-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            messages.error(request, "Invalid Mobile Number.")
            return redirect("checkout")

        
        pincode_pattern = r'^[1-9][0-9]{5}$'
        if not re.match(pincode_pattern, pincode):
            messages.error(request, "Invalid Pincode.")
            return redirect("checkout")

        
        order = Order.objects.create(
            customer=customer,
            total_amount=total,
            payment_method=payment,
            address=address,
            phone=phone,
            pincode=pincode
        )

        
        notification_thread = threading.Thread(
            target=send_order_notification,
            args=(customer.fullname,)
        )
        notification_thread.start()

        
        for product in products:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                price=product.price
            )

       
        request.session["cart"] = []

        messages.success(request, "Order Placed Successfully.")
        return redirect("orders")

    return render(request, "checkout.html")
def orders(request):

    if "customer_id" not in request.session:
        return redirect("login")

    customer = Customer.objects.get(
        id=request.session["customer_id"]
    )

    orders = Order.objects.filter(customer=customer).order_by("-order_date")

    return render(request, "orders.html", {
        "orders": orders
    })
from .models import Review

def review(request, id):

    if "customer_id" not in request.session:
        return redirect("login")

    product = Product.objects.get(id=id)

    if request.method == "POST":

        rating = int(request.POST.get("rating"))
        review_text = request.POST.get("review")

        
        sentiment = analyze_sentiment(review_text)

        customer = Customer.objects.get(
            id=request.session["customer_id"]
        )

        Review.objects.create(
            customer=customer,
            product=product,
            rating=rating,
            review=review_text,
            sentiment=sentiment
        )

        messages.success(request, "Review submitted successfully!")

        return redirect("products")

    return render(request, "review.html", {
        "product": product
    })




def product_detail(request, id):

    product = Product.objects.get(id=id)

    reviews = Review.objects.filter(product=product).order_by("-review_date")

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "reviews": reviews
        }
    )
def logout_page(request):
    request.session.flush()
    return redirect("login")




def add_to_cart(request, id):

    try:
        product = Product.objects.get(id=id)

        
        if product.stock <= 0:
            raise Exception("Product is Out of Stock")

        if "cart" not in request.session:
            request.session["cart"] = []

        cart = request.session["cart"]

        cart.append(id)

        request.session["cart"] = cart

        messages.success(request, "Product added to cart successfully.")

        return redirect("cart")

    except Exception as e:
        messages.error(request, str(e))
        return redirect("products")
def remove_from_cart(request, id):

    cart = request.session.get("cart", [])

    if id in cart:
        cart.remove(id)

    request.session["cart"] = cart

    return redirect("cart")
def order_details(request, id):

    order = Order.objects.get(id=id)

    items = OrderItem.objects.filter(order=order)

    return render(
        request,
        "order_details.html",
        {
            "order": order,
            "items": items
        }
    )
def add_to_wishlist(request, id):

    if "customer_id" not in request.session:
        return redirect("login")

    customer = Customer.objects.get(
        id=request.session["customer_id"]
    )

    product = Product.objects.get(id=id)

    Wishlist.objects.get_or_create(
        customer=customer,
        product=product
    )

    return redirect("wishlist")
def wishlist(request):

    if "customer_id" not in request.session:
        return redirect("login")

    customer = Customer.objects.get(
        id=request.session["customer_id"]
    )

    wishlist = Wishlist.objects.filter(customer=customer)

    return render(request,
                  "wishlist.html",
                  {"wishlist": wishlist})
def remove_from_wishlist(request, id):

    Wishlist.objects.filter(id=id).delete()

    return redirect("wishlist")
def profile(request):

    if "customer_id" not in request.session:
        return redirect("login")

    customer = Customer.objects.get(
        id=request.session["customer_id"]
    )

    if request.method == "POST":

        customer.fullname = request.POST.get("fullname")
        customer.email = request.POST.get("email")
        customer.phone = request.POST.get("phone")

        customer.save()

        return redirect("profile")

    return render(request, "profile.html", {
        "customer": customer
    })
def dashboard(request):

    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_reviews = Review.objects.count()

    positive = Review.objects.filter(sentiment="Positive").count()
    negative = Review.objects.filter(sentiment="Negative").count()
    neutral = Review.objects.filter(sentiment="Neutral").count()

    return render(request, "dashboard.html", {
        "total_customers": total_customers,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_reviews": total_reviews,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
    })


def admin_products(request):

    products = Product.objects.all()

    return render(request, "admin_products.html", {
        "products": products
    })
def add_product(request):
    return render(request, "add_product.html")


def edit_product(request, id):
    return render(request, "edit_product.html")


def delete_product(request, id):
    return redirect("admin_products")
def add_product(request):

    if request.method == "POST":

        Product.objects.create(

            name=request.POST.get("name"),

            category=request.POST.get("category"),

            price=request.POST.get("price"),

            description=request.POST.get("description"),

            stock=request.POST.get("stock"),

            image=request.POST.get("image")

        )

        return redirect("admin_products")
    
    return render(request, "add_product.html")
def edit_product(request, id):

    product = Product.objects.get(id=id)

    if request.method == "POST":

        product.name = request.POST.get("name")
        product.category = request.POST.get("category")
        product.price = request.POST.get("price")
        product.description = request.POST.get("description")
        product.stock = request.POST.get("stock")
        product.image = request.POST.get("image")

        product.save()

        return redirect("admin_products")

    return render(request, "edit_product.html", {
        "product": product
    })


def delete_product(request, id):

    product = Product.objects.get(id=id)

    product.delete()

    return redirect("admin_products")
def admin_orders(request):

    orders = Order.objects.all().order_by("-order_date")

    return render(request, "admin_orders.html", {
        "orders": orders
    })
def update_order_status(request, id):

    order = Order.objects.get(id=id)

    if request.method == "POST":

        order.status = request.POST.get("status")
        order.save()

    return redirect("admin_orders")
def admin_reviews(request):

    reviews = Review.objects.all().order_by("-review_date")

    return render(request, "admin_reviews.html", {
        "reviews": reviews
    })
def admin_customers(request):

    customers = Customer.objects.all().order_by("-id")

    return render(request, "admin_customers.html", {
        "customers": customers
    })
def export_orders_csv(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Order ID',
        'Customer',
        'Amount',
        'Payment',
        'Status',
        'Order Date'
    ])

    orders = Order.objects.all()

    for order in orders:
        writer.writerow([
            order.id,
            order.customer.fullname,
            order.total_amount,
            order.payment_method,
            order.status,
            order.order_date
        ])

    return response
@api_view(['GET'])
def product_api(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)
def analyze_sentiment(review):
    positive_words = [
        "good", "excellent", "awesome", "best",
        "great", "nice", "love", "amazing"
    ]

    negative_words = [
        "bad", "worst", "poor", "hate",
        "terrible", "slow", "damage", "broken"
    ]

    words = review.lower().split()

    positive_count = sum(
        1 for word in words if word in positive_words
    )

    negative_count = sum(
        1 for word in words if word in negative_words
    )

    if positive_count > negative_count:
        return "Positive"

    elif negative_count > positive_count:
        return "Negative"

    else:
        return "Neutral"
from django.contrib.auth import authenticate, login


def admin_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid Admin Credentials")

    return render(request, "admin_login.html")

