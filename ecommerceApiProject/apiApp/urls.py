from django.urls import path
from . import views

urlpatterns = [
    path('product_list', views.product_list, name='product_list'),
    path('product/<slug:slug>', views.product_detial, name='product_detail'),
    path('category_list', views.category_list, name='category_list'),
    path('category/<slug:slug>', views.category_detail, name='category_detial'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
]

