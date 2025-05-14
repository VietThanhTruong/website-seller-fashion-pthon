from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from fuzzywuzzy import process
from .models import Product, CartItem
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def cart_item_count(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        cart_items = CartItem.objects.filter(session_key=session_key)
    return cart_items.count()

def get_total_price(cart_items):
    total = 0
    for item in cart_items:
        total += item.total_price()
    return total


def format_vnd(amount):
    return '{:,.0f}'.format(amount).replace(',', ',')

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
    if request.method == 'POST':
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        print("Session Key: ", session_key)

        product = get_object_or_404(Product, pk=product_id)
        print("Product:", product)

        quantity = request.POST.get('quantity', 1)
        try:
            quantity = int(quantity)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid quantity'}, status=400)

        if request.user.is_authenticated:
            item, created = CartItem.objects.get_or_create(
                product=product,
                user=request.user,
                defaults={'quantity': quantity}
            )
        else:
            item, created = CartItem.objects.get_or_create(
                product=product,
                user=None,
                session_key=session_key,
                defaults={'quantity': quantity}
            )
        

        if not created:
            item.quantity += quantity

        item.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@require_POST
@login_required
def update_cart_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    if item.user != request.user and item.session_key != request.session.session_key:
        return JsonResponse({'success': False, 'error': 'Không được phép'}, status=403)

    action = request.POST.get('action')
    if action == 'increase':
        item.quantity += 1
    elif action == 'decrease' and item.quantity > 1:
        item.quantity -= 1
    item.save()

    item_total = item.total_price()

    if request.user.is_authenticated:
        items = CartItem.objects.filter(user=request.user)
    else:
        items = CartItem.objects.filter(session_key=request.session.session_key)

    cart_total = get_total_price(items)

    return JsonResponse({
        'success': True,
        'quantity': item.quantity,
        'item_total': format_vnd(item_total),
        'cart_total': format_vnd(cart_total),
    })

@login_required
def cart(request):
    session_key = request.session.session_key
    user_is_login =  request.user.is_authenticated
    if user_is_login:
        items = CartItem.objects.filter(user=request.user)
    else:
        if not session_key:
            request.session.save()
        items = CartItem.objects.filter(session_key=session_key)

    total = get_total_price(items)
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
