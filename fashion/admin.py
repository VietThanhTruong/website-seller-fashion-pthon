from django.contrib import admin
from .models import Product, Category, CartItem
from user_sessions.models import Session

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(CartItem)

class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'user', 'ip', 'user_agent', 'last_activity', 'expire_date')
    search_fields = ('user__username', 'ip', 'user_agent')
    list_filter = ('expire_date',)

admin.site.unregister(Session)
admin.site.register(Session, SessionAdmin)