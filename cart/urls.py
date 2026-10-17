
from django.urls import path
from .import views


urlpatterns = [
    path('add_cart/<str:product_id>/',views.add_cart,name="add_cart"),
    path('cart/',views.cart,name="cart"),
    path('remove_cart_item/<str:product_id>/<str:cart_item_id>/',views.remove_cart_item,name="remove_cart_item"),
    path('add_cart_item/<str:product_id>/<str:cart_item_id>/',views.add_cart_item,name="add_cart_item"),
    path('remove_button_logic/<str:product_id>/<str:cart_item_id>/',views.remove_button_logic,name="remove_button_logic")

]