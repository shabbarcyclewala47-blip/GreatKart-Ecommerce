from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from category import views as category_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Index homepage from the category app
    path('', category_views.index, name='home'),

    # Separate Store page
    path('store/', include('store.urls')),

    path('category/', include('category.urls')),
    path('cart/', include('cart.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )