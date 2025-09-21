from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from ecommerceApiProject.apiApp.models import ProductRating, Review


@receiver(post_save, sender=Review)
def update_product_rating_on_save(sender, instance, **kwargs):
    product = instance.product
    reviews = product.reviews.all()
    total_reviews = reviews.count()

    reviews_average = reviews.aggregate(Avg('reviews'))['rating__avg'] or 0.0 

    product_rating, created = ProductRating.objects.get_or_create(product=product)
    

    
