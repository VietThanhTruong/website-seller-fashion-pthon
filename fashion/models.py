from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
import os

def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'users/{instance.user.id}.{ext}'

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
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        new_image = self.image 
    
        if is_new:
            self.image = None 
            super().save(*args, **kwargs)  
    
        if new_image:
            ext = os.path.splitext(new_image.name)[-1].lower()
            expected_name = f'{self.id}{ext}'
            full_path = os.path.join('products', expected_name)
    
            if default_storage.exists(full_path):
                default_storage.delete(full_path)
    
            new_image.name = expected_name
            self.image = new_image  
    
        super().save(*args, **kwargs)


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'user'], name='unique_user_cartitem', condition=models.Q(user__isnull=False)),
            models.UniqueConstraint(fields=['product', 'session_key'], name='unique_session_cartitem', condition=models.Q(user__isnull=True)),
        ]
          
    def total_price(self):
        return self.quantity * self.product.price
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order_key = models.CharField(max_length=100, unique=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    address = models.TextField(verbose_name="Địa chỉ nhận hàng")
    contact_phone = models.CharField(max_length=20, verbose_name="Số điện thoại liên hệ")
    contact_email = models.EmailField(verbose_name="Email liên hệ", null=True, blank=True)

    note = models.TextField(null=True, blank=True, verbose_name="Nội dung ghi chú")
    total_amount = models.IntegerField(default=0)

    def __str__(self):
        return f"Đơn hàng #{self.id} của {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.IntegerField() 

    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to=user_directory_path, default='users/default.jpg', blank=True, null=True)
    address = models.TextField(null=True, blank=True, verbose_name="Địa chỉ nhận hàng")
    contact_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Số điện thoại liên hệ")
    contact_email = models.EmailField(null=True, blank=True, verbose_name="Email liên hệ")

    def __str__(self):
        return self.user.username
    
class UserContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts")
    address = models.TextField(verbose_name="Địa chỉ nhận hàng")
    contact_phone = models.CharField(max_length=20, verbose_name="Số điện thoại liên hệ")
    contact_email = models.EmailField(verbose_name="Email liên hệ", null=True, blank=True)
    is_default = models.BooleanField(default=False, verbose_name="Địa chỉ mặc định")
    
    def __str__(self):
        return f"{self.address} - {self.contact_phone} ({self.user.username})"