from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Sum, Q
from django.http import HttpResponseNotAllowed
from urllib.parse import urlencode
from .models import Product, ProductCategory, Brand, ReviewLog, StoreInventory, ProductComposition, WishlistItem, Wishlist, Order, OrderItem, OrderStatus, Store
from .forms import CustomUserCreationForm, CustomUserChangeForm, ReviewForm
from django.contrib import messages

def catalog_view(request):
    categories = ProductCategory.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.all()
    
    # Чтение GET-параметров
    category_id = request.GET.get('category')
    brand_id = request.GET.get('brand')
    sort_option = request.GET.get('sort')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    # Собираем параметры в словарь
    get_params = {
        'category': category_id,
        'brand': brand_id,
        'price_min': price_min,
        'price_max': price_max,
        'sort': sort_option,
    }

    # Удаляем пустые значения
    get_params_cleaned = {k: v for k, v in get_params.items() if v}

    # Собираем строку запроса
    query_string = urlencode(get_params_cleaned)

    # Фильтрация по категориям
    if category_id:
        products = products.filter(category_id=category_id)
    if brand_id:
        products = products.filter(brand_id=brand_id)

    # Фильтрация по цене
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    # Сортировка
    if sort_option == 'price_asc':
        products = products.order_by('price')
    elif sort_option == 'price_desc':
        products = products.order_by('-price')


    # Аннотация средней оценки и количества
    products = products.annotate(
        average_rating=Avg('reviews__grade', filter=Q(reviews__viewable=True)),
        total_quantity=Sum('storeinventory__quantity')
    )

    paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'catalog.html', {
        'categories': categories,
        'brands': brands,
        'page_obj': page_obj,
        'query_string': query_string,
    })

def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)

    has_review = ReviewLog.objects.filter(product=product, user=request.user).exists()
    average_rating = ReviewLog.objects.filter(product=product, viewable=True).aggregate(avg=Avg('grade'))['avg'] or 0
    composition = ProductComposition.objects.filter(product=product).select_related('nutrient')
    reviews = ReviewLog.objects.filter(product=product, viewable=True).order_by('-review_date')
    total_quantity = StoreInventory.objects.filter(product=product).aggregate(qty=Sum('quantity'))['qty'] or 0

    # Форма отзыва
    review_form = None
    if request.user.is_authenticated:
        existing_review = ReviewLog.objects.filter(product=product, user=request.user).first()
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                if existing_review:
                    messages.warning(request, "Вы уже оставляли отзыв.")
                else:
                    new_review = form.save(commit=False)
                    new_review.user = request.user
                    new_review.product = product
                    new_review.viewable = False
                    new_review.save()
                    messages.success(request, "Ваш отзыв отправлен на модерацию.")
                    return redirect('product-detail', pk=pk)
        else:
            review_form = ReviewForm()

    return render(request, 'product_detail.html', {
        'product': product,
        'average_rating': average_rating,
        'total_quantity': total_quantity,
        'reviews': reviews,
        'composition': composition,
        'review_form': review_form,
        'has_review': has_review,
    })

def contacts_view(request):
    stores = Store.objects.all()
    return render(request, 'contacts.html', {'stores': stores})

def about_view(request):
    fitness_formula = get_object_or_404(Brand, pk=1)
    just_fit = get_object_or_404(Brand, pk=2)
    maxler = get_object_or_404(Brand, pk=6)

    top_reviews = ReviewLog.objects.filter(
        viewable=True,
        comment__isnull=False
    ).exclude(comment='').order_by('-grade', '-review_date')[:2]

    return render(request, 'about.html', {
        'fitness_formula': fitness_formula,
        'just_fit': just_fit,
        'maxler': maxler,
        'top_reviews': top_reviews,
    })

def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile_view(request):
    wishlist = get_user_wishlist(request.user)
    items = WishlistItem.objects.filter(wishlist=wishlist).select_related('product')[:3]
    orders = Order.objects.filter(user=request.user).exclude(status__name='Черновик').order_by('-order_date')

    return render(request, 'profile.html', {
        'user': request.user,
        'wishlist_items': items,
        'orders' : orders,
    })

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные успешно обновлены.')
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})

def get_user_wishlist(user):
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    return wishlist

@login_required
def add_to_wishlist(request, product_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    wishlist = get_user_wishlist(request.user)
    product = get_object_or_404(Product, pk=product_id)

    item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        item.quantity += 1
        item.save()

    messages.success(request, f'"{product.name}" добавлен в избранное.')

    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))

@login_required
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    item.delete()
    return redirect('wishlist')

@login_required
def wishlist_view(request):
    wishlist = get_user_wishlist(request.user)
    items = WishlistItem.objects.filter(wishlist=wishlist).select_related('product')

    return render(request, 'wishlist.html', {'items': items})

@login_required
def add_to_cart(request, product_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # Получаем статус "Черновик"
    draft_status = OrderStatus.objects.get(name='Черновик')

    # Ищем или создаём черновик заказа
    order, created = Order.objects.get_or_create(
        user=request.user,
        status=draft_status,
        defaults={'comment': '', 'store': None}
    )

    product = get_object_or_404(Product, pk=product_id)

    # Добавляем товар в OrderItem или увеличиваем количество
    item, item_created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={'quantity': 1}
    )

    if not item_created:
        item.quantity += 1
        item.save()

    messages.success(request, f'"{product.name}" добавлен в корзину.')

    return redirect(request.META.get('HTTP_REFERER', 'catalog'))

@login_required
def update_cart(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    draft_status = OrderStatus.objects.get(name='Черновик')
    try:
        order = Order.objects.get(user=request.user, status=draft_status)
    except Order.DoesNotExist:
        return redirect('cart')

    for item in OrderItem.objects.filter(order=order):
        qty_key = f'quantity_{item.id}'
        new_qty = request.POST.get(qty_key)
        if new_qty:
            try:
                qty_int = int(new_qty)
                if qty_int > 0:
                    item.quantity = qty_int
                    item.save()
            except ValueError:
                continue

    messages.success(request, "Корзина обновлена.")
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__status__name='Черновик')
    item.delete()

    messages.success(request, "Товар удалён из корзины.")
    return redirect('cart')

@login_required
def cart_view(request):
    draft_status = OrderStatus.objects.get(name='Черновик')
    try:
        order = Order.objects.get(user=request.user, status=draft_status)
        items = OrderItem.objects.filter(order=order).select_related('product')
    except Order.DoesNotExist:
        order = None
        items = []

    stores = Store.objects.all()
    total_price = sum(item.product.price * item.quantity for item in items)

    return render(request, 'cart.html', {
        'order': order,
        'items': items,
        'stores': stores,
        'total_price': total_price,
        'selected_store_id': order.store.id if order and order.store else None
    })

@login_required
def checkout_view(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    draft_status = OrderStatus.objects.get(name='Черновик')
    processing_status = OrderStatus.objects.get(name='В обработке')

    try:
        order = Order.objects.get(user=request.user, status=draft_status)
        items = OrderItem.objects.filter(order=order)
    except Order.DoesNotExist:
        messages.warning(request, "У вас нет активной корзины.")
        return redirect('cart')

    # Получаем магазин
    store_id = request.POST.get('store_id')
    comment = request.POST.get('comment', '')
    if not store_id:
        messages.error(request, "Выберите магазин.")
        return redirect('cart')

    try:
        store = Store.objects.get(pk=store_id)
    except Store.DoesNotExist:
        messages.error(request, "Выбранный магазин не найден.")
        return redirect('cart')

    # Проверка остатков
    unavailable_items = []
    for item in items:
        stock = StoreInventory.objects.filter(store=store, product=item.product).first()
        if not stock or stock.quantity < item.quantity:
            unavailable_items.append((item.product.name, stock.quantity if stock else 0))

    if unavailable_items:
        msg = "Некоторые товары отсутствуют в выбранном магазине:\n"
        for name, qty in unavailable_items:
            msg += f'• {name} (в наличии: {qty})\n'
        messages.error(request, msg)
        return redirect('cart')

    order.comment = comment
    order.store = store
    order.status = processing_status
    order.save()

    messages.success(request, "Заказ оформлен и передан в обработку.")
    return redirect('profile')

@login_required
def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    items = OrderItem.objects.filter(order=order).select_related('product')
    total_price = sum(item.product.price * item.quantity for item in items)

    return render(request, 'order_detail.html', {
        'order': order,
        'items': items,
        'total_price': total_price
    })

def search_view(request):
    query = request.GET.get('q')
    products = Product.objects.none()

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).annotate(
            average_rating=Avg('reviews__grade', filter=Q(reviews__viewable=True)),
            total_quantity=Sum('storeinventory__quantity')
        )

    paginator = Paginator(products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'search_results.html', {
        'query': query,
        'page_obj': page_obj,
    })