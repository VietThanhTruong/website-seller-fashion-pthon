from django.contrib import admin
from .models import Product, Category, CartItem
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

admin.site.unregister(Session)
admin.site.register(Session, SessionAdmin)
admin.site.register(Category)