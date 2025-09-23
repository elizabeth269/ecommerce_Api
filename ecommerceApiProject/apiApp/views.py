from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
import stripe
from .models import Cart, CartItem, Order, OrderItem, Product, Category, Review, Wishlist
from rest_framework.response import Response
from .serializers import CartItemSerializer, CartSerializer, CategoryDetailSerializer, ProductListSerializer, ProductDetailSerializer, CategorySerializer, ReviewSerializer, WishlistSerializer
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
stripe.api_key= settings.STRIPE_SECRET_KEY
endpoint_secret = 'whsec_...'
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


@api_view(['DELETE'])
def delete_cartitem(request, pk):
    try:
        review = CartItem.objects.get(id=pk)
    except CartItem.DoesNotExist:
        return Response({"error": "cartitem not found"}, status=status.HTTP_404_NOT_FOUND)

    review.delete()
    return Response({"message": "cartitem deleted successfully!"}, status=status.HTTP_200_OK)



@api_view(['POST'])
def add_review(request):
    try:
        product_id = request.data.get('product_id') or request.GET.get('product_id')
        email = request.data.get('email') or request.GET.get('email')
        rating = request.data.get('rating') or request.GET.get('rating')
        review_text = request.data.get('review') or request.GET.get('review')

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




@api_view(['PUT'])
def update_review(request, pk):
    try:
        review = Review.objects.get(id=pk)
    except Review.DoesNotExist:
        return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

    rating = request.data.get('rating') or request.GET.get('rating')
    review_text = request.data.get('review') or request.GET.get('review')

    if rating:
        review.rating = rating
    if review_text:
        review.review = review_text

    review.save()

    serializer = ReviewSerializer(review)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_review(request, pk):
    try:
        review = Review.objects.get(id=pk)
    except Review.DoesNotExist:
        return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

    review.delete()
    return Response({"message": "Review deleted successfully!"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_to_wishlist(request):
    email = request.data.get('email') or request.GET.get('email')
    product_id = request.data.get('product_id') or request.GET.get('product_id')
    if not email or not product_id:
        return Response({'error': 'email and product_id are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        product = Product.objects.get(id=product_id)

    except Product.DoesNotExist:
        return Response({'error': "product does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    wishlist = Wishlist.objects.filter(user=user, product=product)
    if wishlist:
        wishlist.delete()
        return Response('wishlist deleted successfull!', status=status.HTTP_200_OK)

    new_wishlist = Wishlist.objects.create(user=user, product=product)
    serializer = WishlistSerializer(new_wishlist)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def product_search(request):
    query = request.query_params.get('query')
    if not query:
        return Response('no query provided', status=status.HTTP_400_BAD_REQUEST)
    
    products = Product.objects.filter(Q(name__icontains=query)|Q(description__icontains=query)|Q(category__name__icontains=query))

    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_checkout_session(request):
    cart_code = request.data.get('cart_code') or request.GET.get('cart_code')
    email = request.data.get('email') or request.GET.get('email')
    if not cart_code or not email:
        return Response({"error": "cart_code and email are required"}, status=400)
    
    try:
        cart = Cart.objects.get(cart_code=cart_code)
        checkout_session = stripe.checkout.Session.create(  
            customer_email=email,
            payment_method_types=["card"],
            mode="payment",  
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                                "name": item.product.name
                            },
                        "unit_amount": int(item.product.price) * 100,  # amount in cents ($20.00)
                        },
                        "quantity": item.quantity,
                    }
                    for item in cart.cartitems.all()
                ],                       
            success_url="https://nextshoppit.vercel.app/success",
            cancel_url="https://nextshoppit.vercel.app/cancel",
            
            )
        return Response({"data": checkout_session})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            



@csrf_exempt
def my_webhook_view(request):
  payload = request.body
  sig_header = request.META['HTTP_STRIPE_SIGNATURE']
  event = None

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, endpoint_secret
    )
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400)
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    return HttpResponse(status=400)

  if (
    event['type'] == 'checkout.session.completed'
    or event['type'] == 'checkout.session.async_payment_succeeded'
  ):
   session = event['data']['object']

  return HttpResponse(status=200)

def fulfill_checkout(session, cart_code):
    order = Order.objects.create(
        stripe_checkout_id=session['id'],
        amount=session['amount_total'] / 100,
        currency=session['currency'],
        status='paid',
    )

    cart = Cart.objects.get(cart_code=cart_code)
    cartitems = cart.cartitems.all()

    for item in cartitems:
        orderitem = OrderItem.objects.create(order=order, product=item.product, qunatity=item.quantity)

        
    cart.delete()