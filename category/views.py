from django.shortcuts import render
from django.http import HttpResponse
from store .models import Product
import random 


from django.shortcuts import render
from django.http import HttpResponse
from store.models import Product
import random
from django.shortcuts import render
from store.models import Product

def index(request):
    random_prod = list(Product.objects.order_by('?')[:4])

    context = {
        "random_prod": random_prod,
    }

    return render(request, "index.html", context)