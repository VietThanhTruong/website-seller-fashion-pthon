from django.contrib import admin
from .models import Product, Category, CartItem, Order, OrderItem, UserProfile
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from user_sessions.models import Session

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'description', 'category', 'image')  
    search_fields = ('id', 'name', 'description')  
    list_filter = ('category',)  
    ordering = ('-id',) 
    def save_model(self, request, obj, form, change):
        obj._modified_by = request.user 
        super().save_model(request, obj, form, change)

@admin.register(CartItem)
class CartAdmin(admin.ModelAdmin):
    list_display = ('product', 'product_id', 'total_price', 'quantity', 'user')
    search_fields = ('product__name', 'user__username', 'session_key') 
    list_filter = ('user', 'product',)
        
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'user', 'ip', 'user_agent', 'last_activity', 'expire_date')
    search_fields = ('user__username', 'ip', 'user_agent')
    list_filter = ('expire_date',)
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'created_at', 'address', 'contact_phone', 'contact_email',
        'note', 'total_amount', 'user', 'order_key'
    )
    search_fields = ('id', 'contact_phone', 'contact_email', 'order_key', 'user__username')
    list_filter = ('created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'quantity', 'price', 'order', 'product')
    search_fields = ('id', 'order__id', 'product__name')
    list_filter = ('order',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact_email', 'contact_phone', 'address', 'isVerified_email', 'isVerified_phone')
    search_fields = ('user__username', 'contact_email', 'contact_phone', 'address')
    list_filter = ('user', 'isVerified_email', 'isVerified_phone')
    ordering = ('-user',)

class CustomUserAdmin(DefaultUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Thông tin cá nhân', {'fields': ('first_name', 'last_name', 'email')}),
        ('Phân quyền', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Thời gian', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.unregister(Session)
admin.site.register(Session, SessionAdmin)
admin.site.register(Category)
