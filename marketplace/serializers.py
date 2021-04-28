from rest_framework import serializers, fields
from .models import Product, Purchases
from .models import SIZE_CHOICES, Purchase_status_choices

class ProductSerializer(serializers.ModelSerializer):
    sizes_available = fields.MultipleChoiceField(choices=SIZE_CHOICES)
    class Meta:
        model = Product
        fields = ['pk', 'name', 'description', 'sizes_available', 'category', 'price', 'photo']


class PurchaseSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_photo = serializers.ImageField(source='product.photo', read_only=True)
    product_price = serializers.CharField(source='product.price', read_only=True)
    product_description = serializers.CharField(source='product.description', read_only=True)
    class Meta:
        model = Purchases
        fields = ['pk', 'user', 'product', 'product_name', 'chosen_size', 'quantity', 'purchase_status', 'product_photo', 'product_price', 'product_description']
