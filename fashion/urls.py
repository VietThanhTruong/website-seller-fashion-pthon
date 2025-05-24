from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('profile/send_code/<str:type>/', views.send_code, name='send_code'),
    path('profile/verify_code/<str:type>/', views.verify_code, name='verify_code'),
    path('product/<int:product_id>', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/delete-cart-item/<int:item_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('cart', views.cart, name='cart'),
    path('order/<str:order_key>/', views.order_detail, name='order_detail'),
    path('my-orders/', views.order_list, name='order_list'),
    path('checkout/address/', views.checkout_address_view, name='checkout_address'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('api/register', views.register, name='register_api'),
    path('api/login/', views.ajax_login, name='login_api'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
]

