from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from mtv.models import User, Owner, Contact, Shop, Category, Product, ProductInfo, Order, OrderItem, Parameter, ProductInfoParameter
from mtv.serializers import OwnerSerializer, UserSerializer, ContactSerializer, ShopSerializer, CategorySerializer, ProductSerializer, ProductInfoParameterSerializer, ProductInfoSerializer, OrderItemSerializer, OrderItemCreateSerializer, OrderSerializer
from mtv.tokens_generator import create_token
import random
# Create your views here.



class RegisterUserAccount(APIView):
    """
    Для регистрации покупателей
    """
    
    def post(self, request, *args, **kwargs):

        try:
            request.data['token'] = create_token()
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': 'User registered', 'data': request.data})
        except Exception as E:
            return JsonResponse({'Status': False, 'Errors': 'AH'})
        

class RegisterOwnerAccount(APIView):
    """
    Для регистрации поставщиков
    """
    
    def post(self, request, *args, **kwargs):

        try:
            request.data['token'] = create_token()
            serializer = OwnerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': 'Owner registered', 'data': request.data})
        except Exception as E:
            return JsonResponse({'Status': False, 'Errors': 'AH'})
        

class ShopRegisterView(APIView):
    """
    Класс для работы с магазинами
    """

    def post(self, request, *args, **kwargs):

        # ow = Owner.objects.get(token=request.data['token'])
        # print(ow)
        if Owner.objects.filter(token=request.data['token']).exists():
                owner_id = Owner.objects.filter(token=request.data['token'])
                print(owner_id)
                request.data['owner'] = owner_id
                del request.data['token']
                print(request.data)
        # try:
        #     if Owner.objects.filter(token=request.data['token']).exists():
        #         owner_id = Owner.objects.filter(token=request.data['token']).select_related('id')
        #         request.data['owner'] = owner_id
        #         del request.data['token']
        #         print(request.data)
        #         serializer = ShopSerializer(data=request.data)
        #         if serializer.is_valid():
        #             serializer.save()
        #             return JsonResponse({'Status': 'Shop created', 'data': request.data})
        # except Exception as E:
        #     return JsonResponse({'Status': False, 'Errors': 'AH'})