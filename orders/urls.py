from django.urls import path


from . import views
urlpatterns = [
  
    path('place-order/', views.checkout, name='checkout'),
    path('placed_order/<int:id>/',views.placed_order,name="placed_order"),
    path('payments/',views.payments,name="payments"),

]