from django.contrib import admin

# Register your models here.
from .models import Product,Variation
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':['product_name',]}
    list_display=['product_name','description','price','stock','is_available']

class VariationAdmin(admin.ModelAdmin):
    list_display=['product','variation_category','variation_value','created_date']
admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)