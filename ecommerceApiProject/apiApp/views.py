from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import Cart, CartItem, Product, Category, Review
from rest_framework.response import Response
from .serializers import CartItemSerializer, CartSerializer, CategoryDetailSerializer, ProductListSerializer, ProductDetailSerializer, CategorySerializer, ReviewSerializer
from rest_framework import status
from django.contrib.auth import get_user_model

# Create your views here.
User = get_user_model()

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



@api_view(['PUT'])
def update_cartitem_quantity(request):
    cartitem_id = request.data.get('item_id') or request.GET.get('item_id')
    quantity = request.data.get('quantity') or request.GET.get('quantity')

    if cartitem_id is None or quantity is None:
        return Response(
            {
                'error': 'item_id and quantity are required'
            }, status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return Response(
                {"error": "Quantity must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST
            )
    except ValueError:
        return Response(
            {"error": "Quantity must be an integer"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        cartitem = CartItem.objects.get(id=cartitem_id)
    except CartItem.DoesNotExist:
        return Response(
            {"error": "Cart item not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    quantity = int(quantity)

    cartitem = CartItem.objects.get(id=cartitem_id)
    cartitem.quantity = quantity
    cartitem.save()

    serializer = CartItemSerializer(cartitem)
    return Response({'data': serializer.data, 'message': 'cartitem udated successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_review(request):
    try:
        product_id = request.data.get('product_id') or request.GET.get('product_id')
        email = request.data.get('email') or request.GET.get('email')
        rating = request.data.get('rating') or request.GET.get('rating')
        review_text = request.data.get('review') or request.GET.get('reveiw')

        if not all([product_id, email,rating, review_text]):
            return Response({'error': "all fields (product_id, email,rating, review_text) are required"})
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': "product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            return Response({
                'error': 'user not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
        review = Review.objects.create(product=product, user=user, rating=rating, review=review_text)
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
    
    except Exception as e:
        return Response({ 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

