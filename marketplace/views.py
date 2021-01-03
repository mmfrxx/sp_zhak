from django.shortcuts import render
from rest_framework.status import *

from authentication.models import User
from .models import Product, Purchases
from .serializers import ProductSerializer
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


class CreateProduct(generics.CreateAPIView):
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
        serializer = self.serializer_class(requested_product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, HTTP_200_OK)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)
