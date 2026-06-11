from django.db import models

class Customer(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=50) # Increased length for emails
    mobile = models.CharField(max_length=10)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class Restaurant(models.Model):
    name = models.CharField(max_length=100) # Increased length for restaurant names
    picture = models.URLField(max_length=500, default='https://designshack.net/wp-content/uploads/Free-Simple-Restaurant-Logo-Template.jpg')
    cuisine = models.CharField(max_length=200)
    rating = models.FloatField()
    
    def __str__(self):
        return self.name

class Item(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    price = models.FloatField()
    # Checked = Veg, Unchecked = Non-Veg
    vegeterian = models.BooleanField(default=False) 
    picture = models.URLField(max_length=500, default='https://www.indiafilings.com/learn/wp-content/uploads/2024/08/How-to-Start-Food-Business.jpg')

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="cart")
    items = models.ManyToManyField("Item", related_name="carts")
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    paid = models.BooleanField(default=False)

    def total_price(self):
        return sum(item.price for item in self.items.all())
    
    def __str__(self):
        return f"Cart {self.id} - {self.customer.username}"