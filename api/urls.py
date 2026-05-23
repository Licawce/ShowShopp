from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('cart/', views.cart_api, name='api_cart'),
    path('cart/add/', views.cart_add_api, name='api_cart_add'),
    path('orders/', views.orders_api, name='api_orders'),
]