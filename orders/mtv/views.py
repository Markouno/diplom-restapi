from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from mtv.signals import new_user_registered, new_order
from django.http import JsonResponse
from django.db import IntegrityError
from django.db.models import Q, Sum, F
from ujson import loads as load_json
from mtv.models import User, ConfirmEmailToken, Contact, Shop, Category, Product, ProductInfo, Order, OrderItem, Parameter, ProductInfoParameter
from mtv.serializers import UserSerializer, ContactSerializer, ShopSerializer, CategorySerializer, ProductSerializer, ProductInfoParameterSerializer, ProductInfoSerializer, OrderItemSerializer, OrderItemCreateSerializer, OrderSerializer
import random
# Create your views here.



class RegisterAccount(APIView):
    """
    Для регистрации покупателей
    """
    # Регистрация методом POST
    def post(self, request, *args, **kwargs):

        # проверяем обязательные аргументы
        print(request.data)
        if {'first_name', 'last_name', 'email', 'password'}.issubset(request.data):
            errors = {}

            # Валидация пароля
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # Сборщик ошибок
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                # проверяем данные для уникальности имени пользователя
                request.data.update({})
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():

                    # сохраняем пользователя
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    new_user_registered.send(sender=self.__class__, user_id=user.id)
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
    

class LoginAccount(APIView):
    """
    Класс для авторизации пользователей
    """
    # Авторизация методом POST
    def post(self, request, *args, **kwargs):

        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)

                    return JsonResponse({'Status': True, 'Token': token.key})

            return JsonResponse({'Status': False, 'Errors': 'Не удалось авторизовать'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ConfirmAccount(APIView):
    """
    Класс для подтверждения почтового адреса
    """
    # Регистрация методом POST
    def post(self, request, *args, **kwargs):

        # проверяем обязательные аргументы
        if {'email', 'token'}.issubset(request.data):

            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': 'Неправильно указан токен или email'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
    

class CategoryView(ListAPIView):
    """
    Класс для просмотра категорий
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ProductInfoView(APIView):
    """
    Класс для поиска товаров
    """
    def get(self, request, *args, **kwargs):

        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        # Селект из таблицы ProductInfo с приклеиванием ProductInfoParameter
        queryset = ProductInfo.objects.filter(
            query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)


class BasketView(APIView):
    """
    Класс для работы с корзиной пользователя
    """

    # получить корзину
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        basket = Order.objects.filter(
            user_id=request.user.id, status='new').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    # редактировать корзину
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_dict = request.data.get('items')
        print(items_dict)
        print(type(items_dict))
        if items_dict:

            basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='new')
            objects_created = 0
            items_dict.update({'order': basket.id})
            serializer = OrderItemSerializer(data=items_dict)
            if serializer.is_valid():
                try:
                    serializer.save()
                except IntegrityError as error:
                    return JsonResponse({'Status': False, 'Errors': str(error)})
                else:
                    objects_created += 1

            else:

                return JsonResponse({'Status': False, 'Errors': serializer.errors})

            return JsonResponse({'Status': True, 'Objects created': objects_created})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # удалить товары из корзины
    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_dict = request.data.get('items')
        if items_dict:
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='new')
            query = Q()
            objects_deleted = False
            for key, value in items_dict.items():
                query = query | Q(order_id=basket.id, id=value)
                objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # добавить позиции в корзину
    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_dict = request.data.get('items')
        if items_dict:
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='new')
            objects_updated = 0
            objects_updated += OrderItem.objects.filter(order_id=basket.id, id=items_dict['id']).update(
                            quantity=items_dict['quantity'])
            
            return JsonResponse({'Status': True, 'Обновлено объектов': objects_updated})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PartnerState(APIView):
    """
    Класс для работы со статусом поставщика
    """

    # получить текущий статус
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    # изменить текущий статус
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)
        state = request.data.get('state')
        try:
            Shop.objects.filter(user_id=request.user.id).update(state=state)
            return JsonResponse({'Status': True})
        except ValueError as error:
            return JsonResponse({'Status': False, 'Errors': str(error), 'Message': 'Need to send true of false'})

        
class PartnerOrders(APIView):
    """
    Класс для получения заказов поставщиками
    """
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(status='new').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)


class ContactView(APIView):
    """
    Класс для работы с контактами покупателей
    """

    # получить мои контакты
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        contact = Contact.objects.filter(
            user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    # добавить новый контакт
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'city', 'street', 'phone'}.issubset(request.data):
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # удалить контакт
    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            query = Q()
            objects_deleted = False
            for contact_id in items_list:
                if contact_id.isdigit():
                    query = query | Q(user_id=request.user.id, id=contact_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = Contact.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    # редактировать контакт
    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if 'id' in request.data:
            if request.data['id'].isdigit():
                contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()
                print(contact)
                if contact:
                    serializer = ContactSerializer(contact, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse({'Status': True})
                    else:
                        return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


# class ContactUserAccount(APIView):
#     """
#     Для добавления контактов покупателей
#     """
    
#     def post(self, request, *args, **kwargs):

#         try:
#             if User.objects.filter(token=request.data['token']).exists():
#                 user_id = User.objects.get(token=request.data['token'])
#                 request.data['user'] = user_id.id
#                 del request.data['token']
#                 serializer = ContactSerializer(data=request.data)
#                 if serializer.is_valid():
#                     serializer.save()
#                     return JsonResponse({'Status': 'Contact added', 'data': request.data})

#         except Exception as E:
#             return JsonResponse({'Status': False, 'Errors': 'AH'})
        

# class ShopRegisterView(APIView):
#     """
#     Класс для работы с магазинами
#     """

#     def post(self, request, *args, **kwargs):

#         try:
#             if User.objects.filter(token=request.data['token']).exists():
#                     owner_id = Owner.objects.get(token=request.data['token'])
#                     request.data['owner'] = owner_id.id
#                     del request.data['token']
#                     serializer = ShopSerializer(data=request.data)
#                     if serializer.is_valid():
#                         serializer.save()
#                         return JsonResponse({'Status': 'Shop created', 'data': request.data})
#         except Exception as E:
#             return JsonResponse({'Status': False, 'Errors': 'AH'})
#         # try:
#         #     if Owner.objects.filter(token=request.data['token']).exists():
#         #         owner_id = Owner.objects.filter(token=request.data['token']).select_related('id')
#         #         request.data['owner'] = owner_id
#         #         del request.data['token']
#         #         print(request.data)
#         #         serializer = ShopSerializer(data=request.data)
#         #         if serializer.is_valid():
#         #             serializer.save()
#         #             return JsonResponse({'Status': 'Shop created', 'data': request.data})
#         # except Exception as E:
#         #     return JsonResponse({'Status': False, 'Errors': 'AH'})