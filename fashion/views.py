from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .forms import EditProfileForm, UserProfileForm
from django.contrib.auth.forms import UserCreationForm
from fuzzywuzzy import process
from django.urls import reverse
from django.contrib import messages
from .models import Product, CartItem, UserProfile, UserContact, Order, OrderItem
import logging
import urllib.parse

logger = logging.getLogger(__name__)


def _cart_items(request):
    if request.user.is_authenticated:
        return CartItem.objects.filter(user=request.user)
    if not request.session.session_key:
        request.session.save()
    return CartItem.objects.filter(session_key=request.session.session_key)

def _total_price(items):
    return sum(item.total_price() for item in items)

def _format_vnd(amount):
    return '{:,.0f}'.format(amount).replace(',', ',')

def generate_vietqr_url(amount, content):
    base_url = "https://img.vietqr.io/image/mbbank-0397644468-print.jpg"
    params = {
        "accountName": "Phạm Lê Xuân Trường",
        "addInfo": content,
        "amount": amount
    }
    query_string = urllib.parse.urlencode(params, safe='')
    full_url = f"{base_url}?{query_string}"
    return full_url

@login_required
def home(request):
    return render(request, 'store/home.html', {
        'products': Product.objects.all(),
        'cart_item_count': _cart_items(request).count()
    })

@login_required
def user_profile(request):
    return render(request, 'store/user_profile.html', {
        'cart_item_count': _cart_items(request).count()
    })

@login_required
def edit_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = EditProfileForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_profile')  
    else:
        user_form = EditProfileForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'cart_item_count': _cart_items(request).count()
    }
    return render(request, 'store/edit_profile.html', context)

@login_required
def search(request):
    q = request.GET.get('q', '')
    results = [p for p in Product.objects.all() if process.extractOne(q, [p.name])[1] > 80]
    return render(request, 'store/search_results.html', {
        'query': q, 'results': results,
        'cart_item_count': _cart_items(request).count()
    })

@login_required
def product_detail(request, product_id):
    return render(request, 'store/product_detail.html', {
        'product': get_object_or_404(Product, pk=product_id),
        'cart_item_count': _cart_items(request).count()
    })

@permission_required('fashion.add_cartitem')
@csrf_protect
@require_POST
def add_to_cart(request, product_id):
    try:
        product = get_object_or_404(Product, pk=product_id)
        quantity = int(request.POST.get('quantity', 1) or 1)

        if not request.session.session_key:
            request.session.save()

        if request.user.is_authenticated:
            filters = {'product': product, 'user': request.user}
        else:
            filters = {
                'product': product,
                'user': None,
                'session_key': request.session.session_key
            }

        item, created = CartItem.objects.get_or_create(defaults={'quantity': quantity}, **filters)

        if not created:
            item.quantity += quantity
        item.save()

        return JsonResponse({'success': True})
    
    except Exception as e:
        logger.error(f"Lỗi khi thêm vào giỏ hàng: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

    
@permission_required('fashion.delete_cartitem')
@require_POST
def delete_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    if request.user.is_authenticated:
        if item.user != request.user:
            return JsonResponse({'success': False, 'error': 'Bạn không có quyền xóa mục này.'}, status=403)
    else:
        if item.session_key != request.session.session_key:
            return JsonResponse({'success': False, 'error': 'Bạn không có quyền xóa mục này.'}, status=403)

    item.delete()
    return JsonResponse({'success': True, 'message': 'Đã xóa sản phẩm khỏi giỏ hàng.'})

@permission_required('fashion.change_cartitem')
@require_POST
@login_required
def update_cart_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    if item.user != request.user and item.session_key != request.session.session_key:
        return JsonResponse({'success': False, 'error': 'Không được phép'}, status=403)

    action = request.POST.get('action')
    item.quantity += 1 if action == 'increase' else -1 if item.quantity > 1 else 0
    item.save()

    items = _cart_items(request)
    return JsonResponse({
        'success': True,
        'quantity': item.quantity,
        'item_total': _format_vnd(item.total_price()),
        'cart_total': _format_vnd(_total_price(items)),
    })

@login_required
def cart(request):
    keys_to_clear = ['selected_items', 'total_price', 'oderKey', 'selected_contact_id', 'voucher_code', 'items']
    for key in keys_to_clear:
        if key in request.session:
            del request.session[key]
            
    items = _cart_items(request)
    return render(request, 'store/cart.html', {
        'items': items,
        'total': _total_price(items),
        'cart_item_count': items.count()
    })
    
@login_required
def checkout_address_view(request):
    user = request.user
    items = _cart_items(request)

    if not items.exists():
        return redirect('cart')

    contacts = UserContact.objects.filter(user=user)

    item_ids_str = request.GET.get("selected_items") or request.session.get("selected_items", "")
    item_ids = item_ids_str.split(",") if item_ids_str else []

    selected_items = items.filter(id__in=item_ids)
    total_price = sum(item.total_price() for item in selected_items)

    request.session['selected_items'] = ",".join(item_ids)
    request.session['total_price'] = int(total_price)  
    request.session['items_ids_only'] = item_ids

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_address':
            if contacts.count() >= 4:
                messages.warning(request, "Bạn chỉ có thể lưu tối đa 4 địa chỉ.")
            else:
                address = request.POST.get('new_address')
                phone = request.POST.get('new_phone')
                email = request.POST.get('new_email', '')

                if address and phone:
                    UserContact.objects.create(user=user, address=address, contact_phone=phone, contact_email=email)
                    messages.success(request, "Thêm địa chỉ thành công.")
                else:
                    messages.error(request, "Vui lòng điền đầy đủ thông tin.")

            return redirect("checkout_address")

        elif action == 'delete_contact':
            contact_id = request.POST.get('contact_id')
            contact = get_object_or_404(UserContact, id=contact_id, user=user)
            contact.delete()
            messages.success(request, "Đã xóa địa chỉ thành công.")
            return redirect("checkout_address")

        elif action == 'checkout':
            selected_contact_id = request.POST.get("selected_contact")
            if not selected_contact_id:
                messages.error(request, "Vui lòng chọn địa chỉ giao hàng.")
            else:
                request.session['selected_contact_id'] = selected_contact_id
                request.session['order_note'] = request.POST.get("note", "")
                return redirect("checkout")

    return render(request, 'store/checkout_address.html', {
        'contacts': contacts,
        'items': selected_items,
        'itemIds': item_ids_str,
    })

@login_required
def checkout_view(request):
    user = request.user
    items = _cart_items(request)

    contact_id = request.session.get('selected_contact_id')
    item_ids_str = request.session.get('selected_items', '')
    total_price = request.session.get('total_price')
    note = request.session.get('order_note', '')
    oder_key = request.session.get('oderKey')

    if not all([contact_id, item_ids_str, total_price]):
        return redirect("checkout_address")

    contact = get_object_or_404(UserContact, id=contact_id, user=user)

    order, created = Order.objects.get_or_create(
        order_key=oder_key,
        defaults={
            'user': user,
            'address': contact.address,
            'contact_phone': contact.contact_phone,
            'contact_email': contact.contact_email,
            'note': note,
            'total_amount': total_price
        }
    )

    item_ids = item_ids_str.split(",") if item_ids_str else []
    selected_items = items.filter(id__in=item_ids)
    if created:
        for item in selected_items:
            product = item.product
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price
            )

    return render(request, "store/checkout.html", {
        'cart_item_count': items.count(),
        'data': {
            "amount": total_price,
            "transactionContent": user.username,
            "bankName": "MB Bank",
            "stk": "0397644468",
            "name": "Phạm Lê Xuân Trường",
            "icon": "https://img.bankhub.dev/rounded/mbbank.png",
            "description": "Ngân hàng TMCP Quân đội",
            "qrCode": generate_vietqr_url(total_price, user.username),
            "status_text": "pending",
            "oderKey": oder_key
        }
    })

def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'register.html', {'form': form})
