from django.shortcuts import render
from rest_framework.status import *

from authentication.models import User
from .models import Product, Purchases
from .serializers import ProductSerializer, PurchaseSerializer
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import permissions


# Create your views here.

class IsAdminOrMarketPlaceAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin or request.user.is_marketplace_admin


class IsActive(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_active


# adding product to the marketplace

class ProductCreateView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrMarketPlaceAdmin]


# list of available products
class ProductListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = Product.objects.all()
    model = Product
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category']
    ordering_fields = ['price', 'category']


# deleting products for the admin

class ProductDeleteView(GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrMarketPlaceAdmin]

    def delete(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")

        if user.is_admin or user.is_marketplace_admin:
            queryset = Product.objects.filter(pk=self.kwargs['pk']).first()
            if queryset:
                queryset.delete()
                return Response("Success", HTTP_204_NO_CONTENT)
            return Response('No such product', HTTP_400_BAD_REQUEST)
        return Response('You are not allowed to do this.', HTTP_400_BAD_REQUEST)



# updating product information for the admin
class ProductUpdateView(GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrMarketPlaceAdmin]

    def put(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        requested_product = Product.objects.filter(pk=pk).first()
        if requested_product:
            serializer = self.serializer_class(requested_product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, HTTP_200_OK)
            return Response(serializer.errors, HTTP_400_BAD_REQUEST)
        return Response('Requested product does not exist', HTTP_400_BAD_REQUEST)


# needs to be updated using cart
class MakePurchaseView(GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer, PurchaseSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def post(self, request,*args, **kwargs ):
        user = request.user
        pk = kwargs.get("pk")
        requested_user = User.objects.filter(pk=pk).first()
        if requested_user:
            if user == requested_user or user.is_admin or user.is_marketplace_admin:
                products_in_cart = Purchases.objects.filter(user=requested_user, purchase_status='In Cart')
                print(products_in_cart)
                cost = 0
                for product in products_in_cart:
                    cost += product.product.price * product.quantity

                if user.account_bonus >= cost:
                    user.account_bonus -= cost
                    user.save()

                    #need to see this
                    Purchases.objects.filter(user=requested_user, purchase_status='In Cart').update(purchase_status='Complete')
                    # data = products_in_cart.update(purchase_status='Complete')

                    return Response("success", HTTP_200_OK)
                return Response("Not enough bonus points: you have " + str(user.account_bonus) + " bonuses and you need " + str(cost) + " bonuses" , HTTP_400_BAD_REQUEST)
            return Response("No Product pk", HTTP_400_BAD_REQUEST)


# past Purchases for the user
class UserPurchasesView(GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer, PurchaseSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def get(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")
        requested_user = User.objects.filter(pk=pk).first()
        if requested_user:
            if user == requested_user or user.is_admin or user.is_marketplace_admin:
                purchases = Purchases.objects.filter(user=requested_user)
                purchases_data = PurchaseSerializer(purchases, many=True).data
                return Response(purchases_data, HTTP_200_OK)
            return Response('You are not allowed to do this.', HTTP_400_BAD_REQUEST)
        return Response('User does not exist', HTTP_400_BAD_REQUEST)


# add to cart only available if the user logged in is requesting to add to their own cart

class AddToCart(GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer, PurchaseSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def post(self, request, *args, **kwargs):
        user = request.user
        product_pk = request.data.get('product_pk')
        size = request.data.get('chosen_size')
        quantity = request.data.get('quantity')
        #user pk
        pk = kwargs.get("pk")
        requested_user = User.objects.filter(pk=pk).first()
        if requested_user:
            if user == requested_user or user.is_admin or user.is_marketplace_admin:
                #test this
                if product_pk:
                    product = Product.objects.get(pk=product_pk)
                    purchase_list = Purchases.objects.filter(product = product,purchase_status='In Cart', user=user, chosen_size = size ).filter()
                    if purchase_list:
                        purchase = purchase_list.first()
                        purchase.quantity += quantity
                        purchase.save()
                        return Response(data=PurchaseSerializer(purchase).data, status=HTTP_200_OK)
                    else:
                        data = Purchases.objects.create(user=user, product=product, chosen_size=size, quantity=quantity,
                                                        purchase_status='In Cart')
                        serializer = PurchaseSerializer(data)
                    return Response(serializer.data, HTTP_200_OK)
                return Response("No product pk", HTTP_400_BAD_REQUEST)
            return Response("You are not allowed", HTTP_400_BAD_REQUEST)
        return Response("No requested user", HTTP_400_BAD_REQUEST)

    # view cart


class ViewCart(GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer, PurchaseSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def get(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")
        requested_user = User.objects.filter(pk=pk).first()
        if requested_user:
            if user == requested_user or user.is_admin or user.is_marketplace_admin:
                purchases = Purchases.objects.filter(user=requested_user, purchase_status='In Cart')
                purchases_data = PurchaseSerializer(purchases, many=True).data
                return Response(purchases_data, HTTP_200_OK)
            return Response('You are not allowed to do this.', HTTP_400_BAD_REQUEST)
        return Response('User does not exist', HTTP_400_BAD_REQUEST)


    # delete from cart all the products
class DeleteFromCart(GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer, PurchaseSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def delete(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")
        requested_user = User.objects.filter(pk=pk).first()
        product_pk = request.data.get('product_pk')

        if requested_user:
            if user == requested_user or user.is_admin or user.is_marketplace_admin:
                purchases = Purchases.objects.filter(user=requested_user, purchase_status='In Cart', product = product_pk)
                if purchases:
                    purchases.delete()
                    return Response("Success", HTTP_200_OK)
                return Response('Given product is not in your cart', HTTP_400_BAD_REQUEST)
            return Response('You are not allowed to do this.', HTTP_400_BAD_REQUEST)
        return Response('User does not exist', HTTP_400_BAD_REQUEST)


    #change quantity in cart

class UpdateQuanityOfProductsInCart(GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer, PurchaseSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def post(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")
        requested_user = User.objects.filter(pk=pk).first()
        product_pk = request.data.get("product_pk")
        quantity = request.data.get("quantity")

        if requested_user:
            if user == requested_user or user.is_admin or user.is_marketplace_admin:
                purchase = Purchases.objects.filter(user=user, purchase_status='In Cart', product=product_pk).first()
                if purchase:
                    purchase.quantity = quantity
                    purchase.save()
                    return Response(data=PurchaseSerializer(purchase).data, status=HTTP_200_OK)
                return Response('Cannot change the quantity of non-existing product', HTTP_400_BAD_REQUEST)
            return Response('You are not allowed to do this.', HTTP_400_BAD_REQUEST)
        return Response('User does not exist', HTTP_400_BAD_REQUEST)

    # show all purchases for the admin
class ViewAllPurchasesAdmin(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrMarketPlaceAdmin, IsActive]
    queryset = Purchases.objects.all()
    model = Purchases
    serializer_class = PurchaseSerializer