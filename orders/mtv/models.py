from django.db import models


# Create your models here.
class Owner(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Имя', null=False, blank=False)
    last_name = models.CharField(max_length=100, verbose_name='Фамилия', null=False, blank=False)
    login = models.CharField(max_length=50, verbose_name='login', null=False, blank=False, unique=True)
    password = models.CharField(max_length=50, verbose_name='password', help_text='Пароль должен содерждать символы', null=False, blank=False, unique=False)

    class Meta:
        verbose_name = 'Владелец'
        verbose_name_plural = 'Владельцы'
        ordering = ['-login']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class User(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя', blank=False, null=False)
    login = models.CharField(max_length=50, verbose_name='login', blank=False, null=False, unique=True)
    password = models.CharField(max_length=50, verbose_name='password', blank=False, null=False)
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural= 'Пользователи'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Contact(models.Model):
    user = models.OneToOneField(User, verbose_name='Пользователь',
                                null=False, blank=False,
                                on_delete=models.CASCADE)
    city = models.CharField(max_length=100, null=False, blank=False)
    street = models.CharField(max_length=100, null=False, blank=False)
    phone = models.CharField(max_length=20, null=False, blank=False)

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
        ordering = ['-user']

    def __str__(self):
        return f'г.{self.city}, ул.{self.street}, тел. {self.phone}'
    

class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    owner = models.OneToOneField(Owner, verbose_name='Владелец',
                                blank=True, null=True,
                                on_delete=models.CASCADE)
    state = models.BooleanField(verbose_name='Cтатус получения заказов', default=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        ordering = ['-name',]

    def __str__(self):
        return self.name
    

class Category(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название')
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Список категорий"
        ordering = ['-name',]

    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                                 related_name='products', null=False)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-name']

    def __str__(self):
        return self.name
    

class ProductInfo(models.Model):
    shop = models.ForeignKey(Shop, verbose_name='Магазин',
                             related_name='products_infos', on_delete=models.CASCADE,
                             null=False)
    product = models.ForeignKey(Product, verbose_name='Продукт',
                            related_name='products_infos', on_delete=models.CASCADE,
                            null=False)
    name = models.CharField(verbose_name='Название',max_length=50, blank=False, null=False)
    quantity = models.PositiveIntegerField(verbose_name='Кол-во', null=False)
    price = models.PositiveIntegerField(verbose_name='Цена', null=False)

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информация о продуктах'


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', 
                             related_name='orders', on_delete=models.CASCADE,
                             null=False)
    status = models.CharField(max_length=15, null=False, blank=False, default='Заказ собирается')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-date']

    def __str__(self):
        return self.status
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ',
                            related_name='ordered_items', on_delete=models.CASCADE,
                            null=False)
    product_info = models.ForeignKey(ProductInfo, verbose_name='Инфо о продукте',
                            related_name='ordered_items', on_delete=models.CASCADE,
                            null=False)
    quantity = models.PositiveIntegerField(verbose_name='Кол-во', null=False)

    class Meta:
        verbose_name = 'Информация о заказе'

    
class Parameter(models.Model):
    name = models.CharField(verbose_name='Название', max_length=50, null=False, blank=False)

    class Meta:
        verbose_name = 'Параметр'

    def __str__(self):
        return self.name
    

class ProductInfoParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте',
                                     related_name='parameters', on_delete=models.CASCADE,
                                     null=False)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметры',
                                  related_name='parameters', on_delete=models.CASCADE,
                                  null=False)
    value = models.CharField(max_length=50, verbose_name='Описание')

    class Meta:
        verbose_name = 'Параметр'

