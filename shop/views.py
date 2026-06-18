from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Avg
import json

from .models import Product, Category, Cart, CartItem, Order, OrderItem, Review
from .forms import RegistrationForm, LoginForm, ReviewForm, OrderForm, ProfileForm


def handler404(request, exception):
    return render(request, '404.html', status=404)


def page_not_found(request):
    return render(request, '404.html', status=404)


def index(request):
    popular_products = Product.objects.filter(is_popular=True, is_available=True)[:5]
    new_products = Product.objects.filter(is_new=True, is_available=True)[:8]
    categories = Category.objects.all()

    if popular_products.count() < 5:
        popular_products = Product.objects.filter(is_available=True).order_by('-views_count')[:5]

    context = {
        'popular_products': popular_products,
        'new_products': new_products,
        'categories': categories,
    }
    return render(request, 'shop/index.html', context)


def catalog(request):
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')
    sort_by = request.GET.get('sort', 'default')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__icontains=search_query)
        )

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'popular':
        products = products.order_by('-views_count')
    elif sort_by == 'new':
        products = products.order_by('-created_at')

    context = {
        'products': products,
        'categories': categories,
        'active_category': active_category,
        'search_query': search_query or '',
        'sort_by': sort_by,
        'min_price': min_price or '',
        'max_price': max_price or '',
    }
    return render(request, 'shop/catalog.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product.views_count += 1
    product.save(update_fields=['views_count'])

    reviews = product.reviews.all()
    avg_rating = product.get_avg_rating()
    related_products = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(pk=product.pk)[:4]

    user_review = None
    review_form = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()
        if not user_review:
            review_form = ReviewForm()

    if request.method == 'POST' and request.user.is_authenticated:
        if not user_review:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, 'Ваш отзыв добавлен!')
                return redirect('product_detail', slug=slug)

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'user_review': user_review,
        'related_products': related_products,
    }
    return render(request, 'shop/product_detail.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Cart.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('profile')
    else:
        form = RegistrationForm()

    return render(request, 'shop/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                Cart.objects.get_or_create(user=user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                next_url = request.GET.get('next', 'profile')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()

    return render(request, 'shop/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('index')


@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user)
    cart, created = Cart.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    context = {
        'orders': orders,
        'cart': cart,
        'form': form,
    }
    return render(request, 'shop/profile.html', context)


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()

    context = {
        'cart': cart,
        'items': items,
    }
    return render(request, 'shop/cart.html', context)


@login_required
@require_POST
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
    except (json.JSONDecodeError, TypeError):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

    product = get_object_or_404(Product, pk=product_id, is_available=True)
    cart, created = Cart.objects.get_or_create(user=request.user)

    
    available_quantity = product.stock
    
    
    existing_quantity = 0
    try:
        existing_cart_item = CartItem.objects.get(cart=cart, product=product)
        existing_quantity = existing_cart_item.quantity
    except CartItem.DoesNotExist:
        pass
    
    
    total_quantity = existing_quantity + quantity
    
    
    if total_quantity > available_quantity:
        return JsonResponse({
            'success': False,
            'message': f'Недостаточно товара в наличии. Доступно: {available_quantity} шт., '
                      f'в корзине уже: {existing_quantity} шт.',
            'error_type': 'insufficient_stock',
            'available_quantity': available_quantity,
            'current_in_cart': existing_quantity,
        }, status=400)
    
    
    if quantity <= 0:
        return JsonResponse({
            'success': False,
            'message': 'Количество должно быть больше 0',
            'error_type': 'invalid_quantity',
        }, status=400)

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={'quantity': quantity}
    )

    if not item_created:
        cart_item.quantity += quantity
        cart_item.save()

    return JsonResponse({
        'success': True,
        'message': f'{product.name} добавлен в корзину',
        'cart_count': cart.get_items_count(),
        'cart_total': float(cart.get_total()),
        'available_quantity': available_quantity - total_quantity,  # Оставшееся количество
    })


@login_required
@require_POST
def update_cart(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
    except (json.JSONDecodeError, TypeError):
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))

    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    product = cart_item.product

    
    available_quantity = product.stock
    
    
    if quantity > available_quantity:
        return JsonResponse({
            'success': False,
            'message': f'Недостаточно товара в наличии. Доступно: {available_quantity} шт.',
            'error_type': 'insufficient_stock',
            'available_quantity': available_quantity,
            'max_quantity': available_quantity,
        }, status=400)

    if quantity <= 0:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.save()

    cart = cart_item.cart
    return JsonResponse({
        'success': True,
        'cart_count': cart.get_items_count(),
        'cart_total': float(cart.get_total()),
        'item_total': float(cart_item.get_total()) if quantity > 0 else 0,
        'available_quantity': available_quantity,
    })


@login_required
@require_POST
def remove_from_cart(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
    except (json.JSONDecodeError, TypeError):
        item_id = request.POST.get('item_id')

    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    cart = cart_item.cart
    cart_item.delete()

    return JsonResponse({
        'success': True,
        'message': 'Товар удалён из корзины',
        'cart_count': cart.get_items_count(),
        'cart_total': float(cart.get_total()),
    })


@login_required
def checkout_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()

    if not items:
        messages.warning(request, 'Ваша корзина пуста.')
        return redirect('catalog')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = cart.get_total()
            order.save()

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity,
                )
                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity
                    item.product.save()

            cart.items.all().delete()
            messages.success(request, f'Заказ #{order.pk} успешно оформлен!')
            return redirect('order_success', order_id=order.pk)
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = OrderForm(initial=initial)

    context = {
        'form': form,
        'cart': cart,
        'items': items,
    }
    return render(request, 'shop/checkout.html', context)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'shop/order_success.html', {'order': order})


def about_view(request):
    """Страница 'О нас'"""
    context = {
        'title': 'О нас',
    }
    return render(request, 'shop/about.html', context)


def contacts_view(request):
    """Страница 'Контакты'"""
    context = {
        'title': 'Контакты',
    }
    return render(request, 'shop/contacts.html', context)
