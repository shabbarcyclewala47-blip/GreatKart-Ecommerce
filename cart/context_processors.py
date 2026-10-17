
from .models import Cart, CartItem


def cart_counter(request):
    cart_count = 0

    if request.user.is_authenticated:
        cart_count = sum(
            CartItem.objects.filter(
                user=request.user,
                is_active=True
            ).values_list('quantity', flat=True)
        )
    else:
        session_key = request.session.session_key

        if session_key:
            cart = Cart.objects.filter(
                cart_id=session_key
            ).first()

            if cart:
                cart_count = sum(
                    CartItem.objects.filter(
                        cart=cart,
                        user__isnull=True,
                        is_active=True
                    ).values_list('quantity', flat=True)
                )

    return {'cart_count': cart_count}
