import json

import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .forms import CheckoutForm, CustomerSignUpForm, ReviewForm
from .models import CartItem, Order, OrderItem, Product, Review

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def splash(request):
    return render(request, 'store/splash.html')


def home(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    products = Product.objects.all().order_by('-created')
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)
    if category:
        products = products.filter(category=category)
    
    from .models import CATEGORY_CHOICES
    categories = [cat[0] for cat in CATEGORY_CHOICES]
    
    return render(request, 'store/home.html', {
        'products': products, 
        'query': query, 
        'current_category': category, 
        'categories': categories
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    review_form = ReviewForm()
    if request.method == 'POST':
        if request.user.is_authenticated:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, 'Your review has been posted.')
                return redirect(product.get_absolute_url())
        else:
            messages.error(request, 'Please log in to post a review.')
            return redirect('login')

    reviews = product.reviews.all()
    return render(
        request,
        'store/product_detail.html',
        {
            'product': product,
            'reviews': reviews,
            'review_form': review_form,
        },
    )


@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    quantity = int(request.POST.get('quantity', 1)) if request.method == 'POST' else 1
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity = min(20, cart_item.quantity + quantity)
    cart_item.save()
    messages.success(request, f'Added {product.name} to your cart.')
    return redirect('cart')


@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})


@login_required
def update_cart(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                item_id = key.split('_', 1)[1]
                try:
                    item = CartItem.objects.get(pk=item_id, user=request.user)
                    quantity = max(1, int(value))
                    item.quantity = quantity
                    item.save()
                except (CartItem.DoesNotExist, ValueError):
                    continue
        remove_id = request.POST.get('remove_id')
        if remove_id:
            CartItem.objects.filter(pk=remove_id, user=request.user).delete()
    return redirect('cart')


@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    if not cart_items.exists():
        messages.info(request, 'Your cart is empty. Add products before checkout.')
        return redirect('home')

    total = sum(item.total_price() for item in cart_items)
    order = None
    payment_ready = False
    razorpay_order_id = None
    form = CheckoutForm(request.POST or None, initial={
        'full_name': request.user.username,
        'email': request.user.email,
    })

    if request.method == 'POST' and form.is_valid():
        order = form.save(commit=False)
        order.user = request.user
        order.amount = total
        order.status = 'pending'
        order.save()
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity,
            )
        razorpay_order = razorpay_client.order.create(
            {'amount': int(total * 100), 'currency': 'INR', 'payment_capture': '1'}
        )
        order.razorpay_order_id = razorpay_order['id']
        order.save()
        payment_ready = True
        razorpay_order_id = razorpay_order['id']

    return render(
        request,
        'store/checkout.html',
        {
            'cart_items': cart_items,
            'total': total,
            'form': form,
            'order': order,
            'payment_ready': payment_ready,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
        },
    )


@csrf_exempt
@login_required
def payment_success(request):
    if request.method != 'POST':
        return redirect('home')

    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_signature = request.POST.get('razorpay_signature')
    order = get_object_or_404(Order, user=request.user, razorpay_order_id=razorpay_order_id)

    try:
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        }
        razorpay_client.utility.verify_payment_signature(params_dict)
        order.razorpay_payment_id = razorpay_payment_id
        order.status = 'paid'
        order.save()
        CartItem.objects.filter(user=request.user).delete()
        return render(request, 'store/order_success.html', {'order': order})
    except razorpay.errors.SignatureVerificationError:
        order.status = 'failed'
        order.save()
        messages.error(request, 'Payment verification failed. Please try again.')
        return redirect('cart')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/order_history.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, 'Welcome back, {}'.format(user.username))
        return redirect('home')

    return render(request, 'store/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = CustomerSignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Account created successfully. Welcome to Oceanix!')
        return redirect('home')

    return render(request, 'store/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def dashboard(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/dashboard.html', {'cart_items': cart_items})


@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    products = Product.objects.count()
    reviews = Review.objects.count()
    return render(request, 'store/admin_dashboard.html', {'products': products, 'reviews': reviews})


def chatbot(request):
    products = Product.objects.all().values('name', 'slug', 'price', 'ai_reference')
    products_list = list(products)
    for p in products_list:
        p['avg_rating'] = Product.objects.get(slug=p['slug']).avg_rating() or 0
        p['price'] = float(p['price'])  # Convert Decimal to float for JSON serialization
    products_json = json.dumps(products_list)
    return render(request, 'store/chatbot.html', {'products_json': products_json})
