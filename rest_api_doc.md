## REST API Документация

## 🐭 Запросы для покупателей

### Регистрация

Первоначально Вам нужно создать несколько пользователей при помощи отправки **http** запросов:
* Покупатель
* Продавец/поставщик

В этом поможет файл `requests_api.http`. Его можно использовать с `rest-client.`

Регистрация для **покупателя** выглядит так:

```
POST http://127.0.0.1:8000/user/register
Content-Type: application/json

{
    "first_name": "Paul",
    "last_name" : "Wesson",
    "email": "wesson@box.com",
    "password": "password"
    
}
```

Для регистрации **продавца/поставщика** необходимо добавить **ключ/значение** в виде `"type": "shop"`

**ВАЖНО!!!**

Необходимо указывать **реальный почтовый ящик**, так как после регистрации на него придёт **токен** для **подтверждения** регистрации аккаунта.

### Подтверждение регистрации аккаунта

Токен необходимо отправить следующим **http** запросом:

```
POST http://127.0.0.1:8000/user/confirm
Content-Type: application/json

{
    "email": "wesson@box.com",
    "token": "886c39faf1253eb1b20576e2684828d889686"
    
}
```

### Логин

Для входа в систему есть **http** запрос:

```
POST http://127.0.0.1:8000/user/login
Content-Type: application/json

{
    "email": "wesson@box.com",
    "password": "password"
    
}
```

В **ответ** на данный запрос Вы получите `токен аутентификации`, который в последующем будет использован для остальных запросов в систему.

### Контакты пользователя

```
POST http://127.0.0.1:8000/user/contact
Content-Type: application/json
Authorization: token 38de7958cdd5fd9469c121499768eb98788b57e0

{
    "city": "Moscow",
    "street": "Beloborodova St., 4",
    "phone": "893723123123" 
}
```
В `header` запроса теперь необходимо указывать `Authorization: token`

Для проверки сохранения данных есть `GET` запрос:

```
GET http://127.0.0.1:8000/user/contact
Content-Type: application/json
Authorization: token 38de7958cdd5fd9469c121499768eb98788b57e0
```
----
### Магазины
Просмотреть список магазинов:

```
GET http://127.0.0.1:8000/shops
Content-Type: application/json
```

Просмотреть список категорий:
```
GET http://127.0.0.1:8000/categories
Content-Type: application/json
```

Просмотреть список товаров в определенном магазине, либо в целом:

```
GET http://127.0.0.1:8000/products?shop_id=1
Content-Type: application/json
```
----
### Корзина

Запрос на создание **корзины** и заполнения её товарами. `product_info` - ID товара, который можно посмотреть в запросах выше. `quantity` - кол-во позиций.
```
POST http://127.0.0.1:8000/basket
Content-Type: application/json
Authorization: token 94e1880d42d8588f3745bf3e5fd374212aa8acb0

{
    "items":
        {
            "product_info": 6,
            "quantity": 1,
        }
}
```
**Удаление** позиций из корзины:
```
DELETE http://127.0.0.1:8000/basket
Content-Type: application/json
Authorization: token 94e1880d42d8588f3745bf3e5fd374212aa8acb0

{
    "items":
        {
            "id": 1
        }
}
```
**Изменение** кол-во позиций определенного товара:
```
PUT http://127.0.0.1:8000/basket
Content-Type: application/json
Authorization: token 94e1880d42d8588f3745bf3e5fd374212aa8acb0

{
    "items":
        {
            "id": 5,
            "quantity": 1
        }
}
```
**Просмотр** корзины:
```
GET http://127.0.0.1:8000/basket
Content-Type: application/json
Authorization: token 94e1880d42d8588f3745bf3e5fd374212aa8acb0
```

### Заказы

Для **подтверждения заказа** необходимо отправить запрос с номером заказа и `id` вашего контакта:
```
POST http://127.0.0.1:8000/order
Content-Type: application/json
Authorization: token 94e1880d42d8588f3745bf3e5fd374212aa8acb0

{
    "id": 1,
    "contact": 1
}
```
Напоминаем, что `id` контакта можно найти в запросах `contact`

Далее вы сможете **просмотреть**, как выглядит Ваш **заказ**:
```
GET http://127.0.0.1:8000/order
Content-Type: application/json
Authorization: token 94e1880d42d8588f3745bf3e5fd374212aa8acb0
```

## 🐸 Запросы для продавцов/поставщиков

### Статусы магазина

Вы можете проверить в каком статусе **Ваш магазин**. Работает он или нет:

```
GET http://127.0.0.1:8000/partner/state
Content-Type: application/json
Authorization: token 04c5752b60b903bb2dc95ecf2ecf43c113489f0b
```

Так же можно изменить статус работы. `true` - готов принимать заказы, `false` -  не готов:
```
POST http://127.0.0.1:8000/partner/state
Content-Type: application/json
Authorization: token 04c5752b60b903bb2dc95ecf2ecf43c113489f0b

{
    "state": true
}
```
### Заказы для магазина

Вы можете просматривать заказы, которые перешли из статуса `new` в `in work`:
```
GET http://127.0.0.1:8000/partner/orders
Content-Type: application/json
Authorization: token 38de7958cdd5fd9469c121499768eb98788b57e0
```
### Товары

Вы, как поставщик, можете добавлять новые товары в свой магазин. Для этого укажите `id магазина`, `id продукта`, `название`, `кол-во` и `цену`:

```
POST http://127.0.0.1:8000/partner/update
Content-Type: application/json
Authorization: token 38de7958cdd5fd9469c121499768eb98788b57e0

{
    "items":
        {
            "shop_id": 1,
            "product_id": 4,
            "name": "MAC",
            "quantity": 4,
            "price": 1290

        }
}
```
