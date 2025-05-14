from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from fuzzywuzzy import process
from .models import Product, CartItem
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

@login_required
def cart_item_count(request):
    if not request.session.session_key:
        request.session.save() 
    session_key = request.session.session_key
    cart_items = CartItem.objects.filter(session_key=session_key)
        
    return cart_items.count()

@login_required
def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products, 'cart_item_count': cart_item_count(request)})

@login_required
def user_profile(request):
    # Logic xử lý thông tin người dùng
    return render(request, 'store/user_profile.html', {'cart_item_count': cart_item_count(request)})

@login_required
def edit_profile(request):
    # Logic chỉnh sửa profile
    return render(request, 'store/edit_profile.html')

@login_required
def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()  
    results = []

    for product in products:
        similarity = process.extractOne(query, [product.name])[1]
        if similarity > 80:  
            results.append(product)
    
    return render(request, 'store/search_results.html', {
        'query': query,
        'results': results,
        'cart_item_count': cart_item_count(request)
    })

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'store/product_detail.html', {'product': product, 'cart_item_count': cart_item_count(request)})

@permission_required('fashion.change_product')
@csrf_protect
@require_POST
def add_to_cart(request, product_id):
    session_key = request.session.session_key or request.session.save()
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))
    item, created = CartItem.objects.get_or_create(
        product=product,
        session_key=session_key,
        defaults={'quantity': quantity}
    )
    if not created:
        item.quantity += quantity
    item.save()
    return redirect('cart')

@require_POST
@login_required
def update_cart_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    if item.user != request.user and item.session_key != request.session.session_key:
        return redirect('cart')  # Ngăn không cho người lạ sửa cart của người khác

    action = request.POST.get('action')
    if action == 'increase':
        item.quantity += 1
    elif action == 'decrease' and item.quantity > 1:
        item.quantity -= 1
    item.save()
    return redirect('cart')

@login_required
def cart(request):
    session_key = request.session.session_key
    items = CartItem.objects.filter(session_key=session_key)

    total = sum(item.total_price() for item in items)
    return render(request, 'store/cart.html', {'items': items, 'total': total, 'cart_item_count': cart_item_count(request)})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
