from django.shortcuts import render
from django.http import HttpResponse
from .models import Product,Variation
from category.models import Category
from django.db.models import Q
from django.core.paginator import Paginator
# Create your views here.
def store(request,category_slug=None):
    categories=None
    products=None
    if category_slug!=None:#jeans
        categories=Category.objects.get(slug=category_slug)#jeans
        products=Product.objects.filter(category=categories)#jeans ke sare products laa dega
        paginator=Paginator(products,2)#idhar ham specify kar rahe hai ki ek page pe kitne
        # products dikhege
        page=request.GET.get('page')#yaha manlo main page1 me hu to page me jayega page 1
        paged_products=paginator.get_page(page)#to ham kisme the page 1 mw to layega
        # page1 ke products
        prod_count=products.count()
    else:

        products=Product.objects.all()#select * from tablename
        paginator = Paginator(products.order_by('id'), 2)#idhar ham specify kar rahe hai ki ek page pe kitne
        # products dikhege
        page=request.GET.get('page')#yaha manlo main page1 me hu to page me jayega page 1
        paged_products=paginator.get_page(page)#to ham kisme the page 1 mw to layega
        # page1 ke products
        prod_count=products.count()
    context = {
    'all_prod': paged_products,
    'all_prod_count': prod_count,
    'links': Category.objects.all(),
    }
    return render(request,'store/store.html',context)

def product_detail(request,category_slug,product_slug):
    single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)
    print(f'AAraha hai ek product ki detail:{single_product}')
    print(f'aaraha hai kya ek prod ka description:{single_product.description}')
    product_variations=Variation.objects.filter(product=single_product)
    print(f'Product variations are:{product_variations}')
    

    context={
        'single_product':single_product,
        'product_variations':product_variations,
    }


    return render(request,'store/product_detail.html',context)


def product_search(request):
    keyword = request.GET.get('keyword', '').strip()

    searched_products = Product.objects.none()

    if keyword:
        searched_products = Product.objects.filter(
            Q(product_name__icontains=keyword) |
            Q(description__icontains=keyword)
        ).order_by('-created_date')

    context = {
        'all_prod': searched_products,
        'all_prod_count': searched_products.count(),
        'keyword': keyword,
    }

    return render(request, 'store/store.html', context)
