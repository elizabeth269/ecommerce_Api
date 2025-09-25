from django.urls import path
from . import views

urlpatterns = [
    path('product_list', views.product_list, name='product_list'),
    path('product/<slug:slug>', views.product_detial, name='product_detail'),
    path('category_list', views.category_list, name='category_list'),
    path('category/<slug:slug>', views.category_detail, name='category_detial'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('update_cartitem_quantity/', views.update_cartitem_quantity, name='update_cartitem_quantity'),
    path('delete_cartitem/<str:pk>/', views.delete_cartitem, name='delete_cartitem'),
    path('add_review/', views.add_review, name='add_review'),
    path('delete_review/<str:pk>/', views.delete_review, name='delete_review'),
    path('update_review/<str:pk>/', views.update_review, name='update_review'),
    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('search/', views.product_search, name='search'),
    path('create_checkout_session/', views.create_checkout_session, name='create_checkout_session'),
    path('webhook/', views.my_webhook_view, name='webhook')
]

