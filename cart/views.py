
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from store.models import Product, Variation
from cart.models import Cart, CartItem


# ==========================================================
# GET OR CREATE SESSION CART ID
# ==========================================================

def _cart_id(request):
    cart = request.session.session_key

    if not cart:
        request.session.create()
        cart = request.session.session_key

    return cart


# ==========================================================
# ADD PRODUCT TO CART
# ==========================================================

def add_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':

        rang = request.POST.get('color')
        size = request.POST.get('size')

        # Get or create cart for the current session
        cart, created = Cart.objects.get_or_create(
            cart_id=_cart_id(request)
        )

        # Get selected product variations
        
        # Get selected product variations
        selected_variations = []

        if rang:
            color_variations = Variation.objects.filter(
                product=product,
                variation_category__iexact='color',
                variation_value__iexact=rang
            ).order_by('id')

            if not color_variations.exists():
                return redirect('cart')

            # Use the first matching record to avoid MultipleObjectsReturned.
            color_variation = color_variations.first()
            selected_variations.append(color_variation)

        if size:
            size_variations = Variation.objects.filter(
                product=product,
                variation_category__iexact='size',
                variation_value__iexact=size
            ).order_by('id')

            if not size_variations.exists():
                return redirect('cart')

            # Use the first matching record to avoid MultipleObjectsReturned.
            size_variation = size_variations.first()
            selected_variations.append(size_variation)
            # Get selected variation IDs
        selected_variation_ids = {
         variation.id for variation in selected_variations
        }

        # Find existing items for this user or guest
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user,
                product=product,
                is_active=True
            ).prefetch_related('variations')

        else:
            cart_items = CartItem.objects.filter(
                cart=cart,
                product=product,
                user__isnull=True,
                is_active=True
            ).prefetch_related('variations')

        # Check whether the same product with the same variations exists
        existing_cart_item = None

        for item in cart_items:
            item_variation_ids = set(
                item.variations.values_list('id', flat=True)
            )

            if item_variation_ids == selected_variation_ids:
                existing_cart_item = item
                break

        # Increase quantity if the same item already exists
        if existing_cart_item:
            existing_cart_item.quantity += 1
            existing_cart_item.save(update_fields=['quantity'])

        # Otherwise, create a new cart item
        else:
            if request.user.is_authenticated:
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    user=request.user,
                    quantity=1
                )
            else:
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=1
                )

            # Attach selected color and size
            if selected_variations:
                cart_item.variations.set(selected_variations)

    return redirect('cart')


# ==========================================================
# DISPLAY CART
# ==========================================================

def cart(request):

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(
            user=request.user,
            is_active=True
        ).select_related(
            'product'
        ).prefetch_related(
            'variations'
        )

    else:
        cart_obj, created = Cart.objects.get_or_create(
            cart_id=_cart_id(request)
        )

        cart_items = CartItem.objects.filter(
            cart=cart_obj,
            user__isnull=True,
            is_active=True
        ).select_related(
            'product'
        ).prefetch_related(
            'variations'
        )

    # Calculate subtotal
    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    # Calculate tax at 10%
    tax = total * 0.10

    # Calculate final total
    final_total = total + tax

    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'final_total': final_total,
    }

    return render(request, 'cart.html', context)


# ==========================================================
# DECREASE QUANTITY OR REMOVE ITEM
# ==========================================================

def remove_cart_item(request, product_id, cart_item_id):

    if request.user.is_authenticated:
        cart_item = get_object_or_404(
            CartItem,
            product_id=product_id,
            id=cart_item_id,
            user=request.user
        )

    else:
        cart_item = get_object_or_404(
            CartItem,
            product_id=product_id,
            id=cart_item_id,
            cart__cart_id=_cart_id(request),
            user__isnull=True
        )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save(update_fields=['quantity'])
    else:
        cart_item.delete()

    return redirect('cart')


# ==========================================================
# INCREASE CART ITEM QUANTITY
# ==========================================================

def add_cart_item(request, product_id, cart_item_id):

    if request.user.is_authenticated:
        cart_item = get_object_or_404(
            CartItem,
            product_id=product_id,
            id=cart_item_id,
            user=request.user
        )

    else:
        cart_item = get_object_or_404(
            CartItem,
            product_id=product_id,
            id=cart_item_id,
            cart__cart_id=_cart_id(request),
            user__isnull=True
        )

    cart_item.quantity += 1
    cart_item.save(update_fields=['quantity'])

    return redirect('cart')


# ==========================================================
# REMOVE ITEM COMPLETELY FROM CART
# ==========================================================

def remove_button_logic(request, product_id, cart_item_id):

    if request.user.is_authenticated:
        cart_item = get_object_or_404(
            CartItem,
            product_id=product_id,
            id=cart_item_id,
            user=request.user
        )

    else:
        cart_item = get_object_or_404(
            CartItem,
            product_id=product_id,
            id=cart_item_id,
            cart__cart_id=_cart_id(request),
            user__isnull=True
        )

    cart_item.delete()

    return redirect('cart')
