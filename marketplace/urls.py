from django.urls import path, re_path
from .views import *
urlpatterns = [
    path('addProduct', CreateProduct.as_view(), name='create_product'),
    path('getProducts', ProductListView.as_view()),
    path('deleteProduct/<int:pk>', ProductDeleteView.as_view()),
    path('updateProduct/<int:pk>', ProductUpdateView.as_view()),
    ]