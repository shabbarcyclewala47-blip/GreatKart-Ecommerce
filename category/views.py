from django.shortcuts import render
from django.http import HttpResponse
from store .models import Product
import random 


from django.shortcuts import render
from django.http import HttpResponse
from store.models import Product
import random

def index(request):
    products = Product.objects.all()
    random_prod = random.sample(list(Product.objects.all()), k=4)
    context = {
        "random_prod": random_prod,
    }
    return render(request, "index.html", context)