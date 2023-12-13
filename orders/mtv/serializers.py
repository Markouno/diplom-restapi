from rest_framework import serializers
from mtv.models import User, Contact, Shop, Category, Product, ProductInfo, Order, OrderItem, Parameter, ProductInfoParameter



class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'user', 'city', 'street', 'phone',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }
    

class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'type', 'contacts')
        read_only_fields = ('id',)
    
    def create(self, validated_data):
        return User.objects.create(**validated_data)


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'user', 'state',)

    def create(self, validated_data):
        return Shop.objects.create(**validated_data)


class CategorySerializer(serializers.ModelSerializer):
    shops = ShopSerializer(read_only=True, many=True)
    class Meta:
        model = Category
        fields = ('id', 'name', 'shops',)


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('name', 'category',)


class ProductInfoParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductInfoParameter
        fields = ('parameter', 'value',)


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductInfoParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'shop', 'product', 'name', 'quantity', 'price', 'product_parameters',)
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product_info', 'quantity',)
        read_only_fields = ('id',)


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)

    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'status', 'date', 'total_sum', 'contact',)
        read_only_fields = ('id',)