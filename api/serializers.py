from rest_framework import serializers
from shop.models import Product, Category, Review, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'products_count']

    def get_products_count(self, obj):
        return obj.products.filter(is_available=True).count()


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'username', 'rating', 'text', 'created_at']
        read_only_fields = ['id', 'username', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    avg_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'category_name',
            'short_description', 'price', 'old_price', 'image',
            'stock', 'is_available', 'is_popular', 'is_new',
            'brand', 'avg_rating', 'reviews_count', 'discount_percent'
        ]

    def get_avg_rating(self, obj):
        return obj.get_avg_rating()

    def get_reviews_count(self, obj):
        return obj.get_reviews_count()


class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    specs = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'category_name',
            'description', 'short_description', 'price', 'old_price',
            'image', 'image_2', 'image_3', 'stock', 'is_available',
            'is_popular', 'is_new', 'brand', 'specifications',
            'avg_rating', 'reviews_count', 'reviews', 'specs',
            'views_count', 'created_at', 'discount_percent'
        ]

    def get_avg_rating(self, obj):
        return obj.get_avg_rating()

    def get_reviews_count(self, obj):
        return obj.get_reviews_count()

    def get_specs(self, obj):
        return obj.get_specs_list()


class OrderItemSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'price', 'quantity', 'total']

    def get_total(self, obj):
        return float(obj.get_total())


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'status_display', 'total_price',
            'first_name', 'last_name', 'email', 'phone',
            'address', 'comment', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'total_price', 'created_at']