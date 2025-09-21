from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import Cart, CartItem, Product, Category
from rest_framework.response import Response
from .serializers import CartSerializer, CategoryDetailSerializer, ProductListSerializer, ProductDetailSerializer, CategorySerializer

# Create your views here.
@api_view(['GET'])
def product_list(request):
    products = Product.objects.filter(featured=True)
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def product_detial(request, slug):
    products = Product.objects.get(slug=slug)
    serializer = ProductDetailSerializer(products)
    return Response(serializer.data)


@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def category_detail(request, slug):
    categories= Category.objects.get(slug=slug)
    serializer = CategoryDetailSerializer(categories)
    return Response(serializer.data)


@api_view(['POST'])
def add_to_cart(request):
    cart_code = request.data.get('cart_code') or request.GET.get('cart_code')
    product_id = request.data.get('product_id') or request.GET.get('product_id')


    cart, created = Cart.objects.get_or_create(cart_code=cart_code)
    product = Product.objects.get(id=product_id)

    cartitem, created = CartItem.objects.get_or_create(product=product, cart=cart)
    if not created:  # if the item was already in the cart
        cartitem.quantity += 1
    else:
        cartitem.quantity = 1
    cartitem.save()

    serializer = CartSerializer(cart)
    return Response(serializer.data)