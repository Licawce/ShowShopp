from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q

from shop.models import Product, Category, Review, Cart, CartItem, Order, OrderItem
from .serializers import (
    ProductListSerializer, ProductDetailSerializer,
    CategorySerializer, ReviewSerializer,
    OrderSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_available=True)
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('q')
        sort = self.request.query_params.get('sort')

        if category:
            queryset = queryset.filter(category__slug=category)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__icontains=search)
            )

        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'popular':
            queryset = queryset.order_by('-views_count')
        elif sort == 'new':
            queryset = queryset.order_by('-created_at')

        return queryset

    @action(detail=False, methods=['get'])
    def popular(self, request):
        products = Product.objects.filter(is_popular=True, is_available=True)[:10]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def review(self, request, slug=None):
        product = self.get_object()
        if Review.objects.filter(product=product, user=request.user).exists():
            return Response({'error': 'Вы уже оставили отзыв'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def cart_api(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = []
    for item in cart.items.select_related('product').all():
        items.append({
            'id': item.id,
            'product_id': item.product.id,
            'product_name': item.product.name,
            'product_slug': item.product.slug,
            'product_image': request.build_absolute_uri(item.product.image.url) if item.product.image else None,
            'price': float(item.product.price),
            'quantity': item.quantity,
            'total': float(item.get_total()),
        })
    return Response({
        'items': items,
        'total': float(cart.get_total()),
        'count': cart.get_items_count(),
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cart_add_api(request):
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))

    try:
        product = Product.objects.get(pk=product_id, is_available=True)
    except Product.DoesNotExist:
        return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={'quantity': quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()

    return Response({
        'success': True,
        'cart_count': cart.get_items_count(),
        'cart_total': float(cart.get_total()),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def orders_api(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)