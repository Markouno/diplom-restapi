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
# from django.contrib import admin
from baton.autodiscover import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from mtv.views import RegisterAccount, LoginAccount, ConfirmAccount, CategoryView, ShopView, ProductInfoView, BasketView, PartnerState, PartnerOrders, ContactView, OrderView, PartnerUpdate


urlpatterns = [
    path('admin/', admin.site.urls),
    path('baton/', include('baton.urls')),
    path('user/register', RegisterAccount.as_view(), name='register-account'),
    path('user/login', LoginAccount.as_view(), name='login'),
    path('user/confirm', ConfirmAccount.as_view(), name='confirm-account'),
    path('user/contact', ContactView.as_view(), name='user-contact'),
    path('categories/', CategoryView.as_view(), name='category-list'),
    path('shops/', ShopView.as_view(), name='shop-list'),
    path('products/', ProductInfoView.as_view(), name='product-info-view'),
    path('basket/', BasketView.as_view(), name='basket'),
    path('order/', OrderView.as_view(), name='order'),
    path('partner/state', PartnerState.as_view(), name='partner-state'),
    path('partner/orders', PartnerOrders.as_view(), name='partner-orders'),
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    path('api/schema', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]