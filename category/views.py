from django.shortcuts import render
from store.models import Product

def index(request):
    random_prod = Product.objects.order_by('?')[:4]

    context = {
        'random_prod': random_prod,
    }

    return render(request, 'index.html', context)