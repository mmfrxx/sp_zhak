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


class ProductCreateView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrMarketPlaceAdmin]


class ProductListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = Product.objects.all()
    model = Product
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category']
    ordering_fields = ['price', 'category']


class ProductDeleteView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrMarketPlaceAdmin]

    def get_queryset(self):
        queryset = Product.objects.filter(pk=self.kwargs['pk'])
        return queryset


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


class MakePurchaseView(GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = ProductSerializer, PurchaseSerializer
    permission_classes = [IsAuthenticated, IsActive]

    def post(self, request):
        user = request.user
        product_pk = request.data.get('pk')
        size = request.data.get('selected_size')
        quantity = request.data.get('quantity')
        if product_pk:
            product = Product.objects.get(pk=product_pk)
            if user.account_bonus >= product.price:
                user.account_bonus -= product.price
                user.save()
                data = Purchases.objects.create(user=user, product = product, chosen_size = size, quantity = quantity)
                serializer= PurchaseSerializer(data)
                return Response(serializer.data, HTTP_200_OK)
            return Response("Not enough bonus points", HTTP_400_BAD_REQUEST)
        return Response("No Product pk", HTTP_400_BAD_REQUEST)


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
