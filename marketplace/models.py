from django.db import models
from authentication.models import User
from multiselectfield import MultiSelectField

SIZE_CHOICES = [
    ('xs', 'XS'),
    ('s', 'S'),
    ('m', 'M'),
    ('l', 'L'),
    ('xl', 'XL'),
]

Purchase_status_choices = [
    ('inProgress', 'In progress'),
    ('completed', 'Completed'),
    ('return', 'Applied for return'),
    ('returnCompleted', 'Returned'),
]


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.CharField(max_length=255, db_index=True)
    category = models.CharField(max_length=255)

    photo = models.ImageField(
        null=True,
        blank=True,
        help_text="Upload your photo for Product"
    )
    price = models.IntegerField(default=0)
    sizes_available = MultiSelectField(choices=SIZE_CHOICES,
                                       max_choices=5,
                                       max_length=12,
                                       null=True)


class Purchases(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    chosen_size = models.CharField(max_length=255, null=True)
    quantity = models.IntegerField(default=1)

    purchase_status = models.CharField(
        max_length=16,
        choices=Purchase_status_choices,
        default='In progress',
    )
