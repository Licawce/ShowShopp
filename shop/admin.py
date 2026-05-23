from django.contrib import admin
from .models import Category, Product, Review, Cart, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order']


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['user', 'rating', 'text', 'created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'old_price', 'stock', 'is_available', 'is_popular', 'is_new',
                    'views_count', 'created_at']
    list_filter = ['category', 'is_available', 'is_popular', 'is_new', 'brand']
    search_fields = ['name', 'description', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_available', 'is_popular', 'is_new']
    inlines = [ReviewInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'category', 'brand', 'short_description', 'description')
        }),
        ('Цены и наличие', {
            'fields': ('price', 'old_price', 'stock', 'is_available')
        }),
        ('Изображения', {
            'fields': ('image', 'image_2', 'image_3')
        }),
        ('Дополнительно', {
            'fields': ('is_popular', 'is_new', 'specifications')
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    readonly_fields = ['created_at']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_items_count', 'get_total', 'updated_at']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'price', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'phone', 'created_at']
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['user__username', 'first_name', 'last_name', 'phone', 'email']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at']