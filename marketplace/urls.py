from django.urls import path, re_path
from .views import *
urlpatterns = [
    path('addProduct', ProductCreateView.as_view(), name='create_product'),
    path('getProducts', ProductListView.as_view()),
    path('deleteProduct/<int:pk>', ProductDeleteView.as_view()),
    path('updateProduct/<int:pk>', ProductUpdateView.as_view()),
    path('makePurchase/<int:pk>', MakePurchaseView.as_view()),
    path('userPurchases/<int:pk>', UserPurchasesView.as_view()),
    path('addToCart/<int:pk>', AddToCart.as_view()),
    path('viewCart/<int:pk>', ViewCart.as_view()),
    path('deleteFromCart/<int:pk>', DeleteFromCart.as_view()),
    path('updateQuanitity/<int:pk>', UpdateQuanityOfProductsInCart.as_view()),
    path('viewAllPurchases', ViewAllPurchasesAdmin.as_view()),

    ]