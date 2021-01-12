from django.db import models
from authentication.models import User


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.CharField(max_length=255, db_index=True)
    size = models.CharField(max_length=255)
    category = models.CharField(max_length=255)

    photo = models.ImageField(
                              null=True,
                              blank=True,
                              help_text="Upload your photo for Product"
                              )
    price = models.IntegerField(default=0)


class Purchases(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
