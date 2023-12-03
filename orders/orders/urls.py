"""
URL configuration for orders project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mtv.views import RegisterUserAccount, RegisterOwnerAccount, ShopRegisterView, ContactUserAccount

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/register', RegisterUserAccount.as_view(), name='user-register'),
    path('user/contact', ContactUserAccount.as_view(), name='user-contact'),
    path('owner/register', RegisterOwnerAccount.as_view(), name='owner-register'),
    path('shop/register', ShopRegisterView.as_view(), name='shop-register'),
]
