from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()  
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)  # Thêm trường user
    session_key = models.CharField(max_length=40, null=True, blank=True)  # Cho trường giỏ hàng không đăng nhập

    session_key = models.CharField(max_length=40)
    class Meta:
        unique_together = (
            ('product', 'user'),
            ('product', 'session_key'),
        )
    def total_price(self):
        return self.quantity * self.product.price
