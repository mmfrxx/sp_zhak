from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase
import io
from PIL import Image
from authentication.models import User
from marketplace.models import Product, Purchases
from django.urls import include, path, reverse
from requests.auth import HTTPBasicAuth
from django.conf import settings


class ProjectTests(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('marketplace/', include('marketplace.urls')),
    ]

    def setUp(self):
        new_user1_data = {
            "username": "pet",
            "first_name": "a",
            "last_name": "pet",
            "password": "randompassword",
            "email": "test@test.com",
        }

        self.new_user1 = User.objects.create(
            username=new_user1_data["username"],
            first_name=new_user1_data["first_name"],
            last_name=new_user1_data["last_name"],
            email=new_user1_data["email"],
            password=new_user1_data["password"],
            is_active=True,
            is_marketplace_admin=True
        )

        self.client.session.auth = HTTPBasicAuth('user', 'pass')
        self.token = self.new_user1.tokens()['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        Product.objects.create(
            name="Cap24",
            description="Pink",
            sizes_available="l",
            category="Hoodie",
            price=100,

        )
        Product.objects.create(
            name="Cap25",
            description="Pink",
            sizes_available="l",
            category="Hoodie",
            price=100,

        )
    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_AddProduct(self):
        create_url = reverse('create_product')
        photo_file = self.generate_photo_file()
        data = {
            "name": "Cap22",
            "description": "Pink",
            "sizes_available": "l",
            "category": "Hoodie",
            "price": 100,
            "photo": photo_file
        }
        response = self.client.post(create_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)

    def test_GetProduct(self):
        create_url = reverse('getProducts')
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_UpdateProduct(self):
        product = Product.objects.filter(name='Cap24').first()
        update_url = reverse('updateProduct', kwargs={"pk": product.pk})
        name = "new name"
        data = {
            "name": name,
            "price": "200"
        }

        response = self.client.put(update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.filter(name=name).exists(), True)

    def test_makePurchase(self):
        product = Product.objects.filter(name='Cap25').first()
        addToCart_url = reverse('addToCart', kwargs={"pk": self.new_user1.pk})
        data = {
            "product_pk": product.pk,
            "chosen_size": "l",
            "quantity": 3
            }
        response = self.client.post(addToCart_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Purchases.objects.count(), 1)
        self.assertEqual(Purchases.objects.filter(product=product.pk).exists(), True)

    def test_DeleteProduct(self):
        product = Product.objects.filter(name='Cap24').first()
        delete_url = reverse('deleteProduct', kwargs={"pk": product.pk})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 1)
