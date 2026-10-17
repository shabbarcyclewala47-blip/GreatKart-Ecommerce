from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
# Create your views here.
from cart.models import Cart,CartItem
from .models import Order,OrderProduct
import random
import json
from orders.models import Payment
from store.models import Product
from django.http import JsonResponse
@login_required(login_url="loggedin")
def checkout(request):

    # Get logged-in user's cart items
    cart_items = CartItem.objects.filter(user=request.user)

    print(f"Saare logged in user ke cartitems aaye: {cart_items}")

    # Calculate total
    total = 0

    for item in cart_items:
        sub_total = item.product.price * item.quantity
        total = total + sub_total

    # Calculate 10% tax
    tax = (total * 10) / 100

    # Final amount
    final_total = total + tax

    # POST request
    if request.method == "POST":

        user = request.user

        first_name = request.POST['fname']
        last_name = request.POST['lname']
        phone_no = request.POST['phone']
        email = request.POST['email']

        country = request.POST['country']
        state = request.POST['state']
        city = request.POST['city']
        pincode = request.POST['pcode']

        add_line_1 = request.POST['add_1']
        add_line_2 = request.POST['add_2']
        order_note = request.POST['o_note']

        # Generate order number
        order_number = random.randint(1000, 999999)

        order_total = final_total
        lagaan = tax

        # Create Order
        order = Order(
            user=user,
            order_number=order_number,
            first_name=first_name,
            last_name=last_name,
            phone_no=phone_no,
            email=email,
            address_line_1=add_line_1,
            address_line_2=add_line_2,
            country=country,
            state=state,
            city=city,
            pincode=pincode,
            order_note=order_note,
            order_total=order_total,
            tax=lagaan,
            status='New',
        )

        order.save()

        print(f"Order ID aa raha hai: {order.id}")

        # Create OrderProduct for every cart item
        

            # Add variations
            # for variation in item.variations.all():
            #     op.variations.add(variation)

        # Context after successful POST
        context = {
            'cart_items': cart_items,
            'total': total,
            'tax': tax,
            'final_total': final_total,
            'order': order,
        }
        return redirect("placed_order",order.id)

     

    # Context for GET request
    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'final_total': final_total,
    }


    return render(
        request,
        'orders/checkout.html',
        context
    )

def placed_order(request,id):
    
    specific_order=Order.objects.get(id=id)
    order_number=specific_order.order_number
    
    email=specific_order.email
    phone_no=request.user.phone_no
    add_line_1=specific_order.address_line_1
    add_line_2=specific_order.address_line_2
    city=specific_order.city
    state=specific_order.state
    pincode=specific_order.pincode
    order_total=specific_order.order_total
    tax=specific_order.tax
    status=specific_order.status
   
   
    context={
        'order_number':order_number,
        'specific_order':specific_order,
    
        'email':email,
        'phone_no':phone_no,
        'add_line_1':add_line_1,
        'add_line_2':add_line_2,
        'city':city,
        'state':state,
        'pincode':pincode,
        'order_total':order_total,
        'tax':tax,
        'status':status,

    }

    return render(request,'orders/placed_order.html',context)


from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from cart.models import CartItem
from orders.models import Order, OrderProduct, Payment
from store.models import Product
import json
import requests


@login_required(login_url="loggedin")
@require_POST
def payments(request):
    # 1. Read payment details from the browser
    try:
        body = json.loads(request.body)
        order_id = body.get("order_id")
        paypal_order_id = body.get("paypal_order_id")

        if not order_id or not paypal_order_id:
            return JsonResponse(
                {"error": "Order ID and PayPal order ID are required."},
                status=400,
            )

    except (json.JSONDecodeError, TypeError):
        return JsonResponse(
            {"error": "Invalid JSON request."},
            status=400,
        )

    # 2. Find this user's pending order
    try:
        order = Order.objects.get(
            id=order_id,
            user=request.user,
            is_ordered=False,
        )
    except Order.DoesNotExist:
        return JsonResponse(
            {"error": "Pending order not found."},
            status=404,
        )

    # 3. Check that Sandbox API credentials are configured
    client_id = getattr(settings, "PAYPAL_CLIENT_ID", "")
    client_secret = getattr(settings, "PAYPAL_CLIENT_SECRET", "")
    base_url = getattr(
        settings,
        "PAYPAL_BASE_URL",
        "https://api-m.sandbox.paypal.com",
    )

    if not client_id or not client_secret:
        return JsonResponse(
            {"error": "PayPal Sandbox credentials are not configured."},
            status=503,
        )

    # 4. Get the cart and check stock before capturing payment
    cart_items = list(
        CartItem.objects.filter(user=request.user).select_related("product")
    )

    if not cart_items:
        return JsonResponse(
            {"error": "Your cart is empty."},
            status=400,
        )

    for item in cart_items:
        if item.quantity <= 0 or item.product.stock < item.quantity:
            return JsonResponse(
                {
                    "error": (
                        f"Insufficient stock for "
                        f"{item.product.product_name}."
                    )
                },
                status=400,
            )

    # 5. Authenticate with PayPal and capture the payment on the server
    try:
        token_response = requests.post(
            f"{base_url}/v1/oauth2/token",
            auth=(client_id, client_secret),
            data={"grant_type": "client_credentials"},
            timeout=20,
        )
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]

        capture_response = requests.post(
            f"{base_url}/v2/checkout/orders/"
            f"{paypal_order_id}/capture",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={},
            timeout=30,
        )

        capture_response.raise_for_status()
        capture_data = capture_response.json()

    except requests.RequestException as exc:
        if exc.response is not None:
            print("PayPal API status:", exc.response.status_code)
            print("PayPal API response:", exc.response.text[:2000])
        else:
            print("PayPal connection error:", str(exc))

        return JsonResponse(
            {
                "error": (
                    "PayPal could not confirm the payment. "
                    "Check the Django terminal for details."
                )
            },
            status=502,
        )
    except (ValueError, KeyError) as exc:
        print("PayPal response parsing error:", str(exc))

        return JsonResponse(
            {"error": "Unable to process PayPal's response."},
            status=502,
        )

    # 6. Verify PayPal's capture status and amount
    if capture_data.get("status") != "COMPLETED":
        return JsonResponse(
            {"error": "PayPal has not confirmed a completed payment."},
            status=400,
        )

    purchase_units = capture_data.get("purchase_units", [])

    captures = [
        capture
        for unit in purchase_units
        for capture in unit.get("payments", {}).get("captures", [])
    ]

    completed_capture = next(
        (capture for capture in captures
         if capture.get("status") == "COMPLETED"),
        None,
    )

    if not completed_capture:
        return JsonResponse(
            {"error": "No completed PayPal capture was found."},
            status=400,
        )

    try:
        paid_amount = Decimal(
            completed_capture["amount"]["value"]
        ).quantize(Decimal("0.01"))

        expected_amount = Decimal(
            str(order.order_total)
        ).quantize(Decimal("0.01"))

    except (KeyError, InvalidOperation, TypeError):
        return JsonResponse(
            {"error": "Unable to verify the payment amount."},
            status=400,
        )

    currency = completed_capture["amount"].get("currency_code")

    if currency != "USD" or paid_amount != expected_amount:
        return JsonResponse(
            {
                "error": (
                    "The payment amount or currency does not match "
                    "your order."
                )
            },
            status=400,
        )

    # 7. Save the verified payment and update the order
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(
                id=order_id,
                user=request.user,
                is_ordered=False,
            )

            # Prevent stock changes or duplicate order processing
            for item in cart_items:
                product = Product.objects.select_for_update().get(
                    id=item.product_id
                )

                if product.stock < item.quantity:
                    raise ValueError(
                        f"Insufficient stock for {product.product_name}."
                    )

            payment = Payment.objects.create(
                user=request.user,
                payment_id=completed_capture["id"],
                payment_method="PayPal",
                amount_paid=paid_amount,
                status="COMPLETED",
            )

            order.payment = payment
            order.is_ordered = True
            order.status = "Completed"
            order.save()

            for item in cart_items:
                product = Product.objects.select_for_update().get(
                    id=item.product_id
                )

                op = OrderProduct.objects.create(
                    order=order,
                    user=request.user,
                    product=product,
                    quantity=item.quantity,
                    price=product.price,
                    payment=payment,
                    ordered=True,
                )

                op.variation.set(item.variations.all())
                op.save()

                product.stock -= item.quantity
                product.save(update_fields=["stock"])

            CartItem.objects.filter(user=request.user).delete()

    except Order.DoesNotExist:
        return JsonResponse(
            {"error": "Order was already processed or not found."},
            status=409,
        )
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse({
        "success": True,
        "order_number": order.order_number,
        "transID": completed_capture["id"],
        "message": "Payment completed successfully.",
    })