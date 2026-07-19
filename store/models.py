from django.db import models



class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)   
    price = models.IntegerField()
    description = models.TextField()
    stock = models.IntegerField()
    image = models.URLField()

    def __str__(self):
        return self.name
class Customer(models.Model):

    fullname = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=10)

    password = models.CharField(max_length=100)

    def __str__(self):
        return self.fullname
STATUS_CHOICES = [
    ("Pending", "Pending"),
    ("Packed", "Packed"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
]
class Order(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    total_amount = models.IntegerField()

    payment_method = models.CharField(max_length=50)

    address = models.TextField()

    phone = models.CharField(max_length=10)

    pincode = models.CharField(max_length=6)

    order_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default="Pending"
)

def __str__(self):
        return f"Order {self.id} - {self.customer.fullname}"
class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.IntegerField(default=1)

    price = models.IntegerField()

    def __str__(self):
        return f"{self.order.id} - {self.product.name}"
class Review(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    rating = models.IntegerField()

    review = models.TextField()

    sentiment = models.CharField(max_length=20)

    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.fullname} - {self.product.name}"
class Wishlist(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.fullname} - {self.product.name}"