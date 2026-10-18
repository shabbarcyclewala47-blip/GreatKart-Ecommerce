from django.urls import path
from . import views

urlpatterns = [
    # All products
    path('', views.store, name='store'),

    # Products by category
    path(
        'category/<slug:category_slug>/',
        views.store,
        name='products_by_category'
    ),

    # Product details
    path(
        'category/<slug:category_slug>/<slug:product_slug>/',
        views.product_detail,
        name='product_details'
    ),

    # Search products
    path('search/', views.product_search, name='product_search'),
]