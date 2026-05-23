import os
import django
from django.core.files import File
from io import BytesIO
from PIL import Image

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'showsystem.settings')
django.setup()

from shop.models import Category, Product, User
from django.contrib.auth.models import User as AuthUser

def create_test_data():
    # Создаем тестового пользователя
    if not AuthUser.objects.filter(username='testuser').exists():
        user = AuthUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f'Создан пользователь: {user.username}')
    
    # Создаем категории
    categories_data = [
        {'name': 'Свет', 'slug': 'light', 'icon': 'light', 'order': 1},
        {'name': 'Звук', 'slug': 'sound', 'icon': 'sound', 'order': 2},
        {'name': 'Эффекты', 'slug': 'effects', 'icon': 'effects', 'order': 3},
        {'name': 'Сцена', 'slug': 'stage', 'icon': 'stage', 'order': 4},
        {'name': 'Кабели', 'slug': 'cables', 'icon': 'cables', 'order': 5},
        {'name': 'Управление', 'slug': 'control', 'icon': 'control', 'order': 6},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        if created:
            print(f'Создана категория: {category.name}')
        categories[cat_data['slug']] = category
    
    # Создаем тестовые товары
    products_data = [
        {
            'name': 'Профессиональный прожектор LED 200W',
            'slug': 'led-projector-200w',
            'category': categories['light'],
            'description': 'Мощный LED прожектор для сцены с яркостью 20000 люмен.',
            'short_description': 'Мощный LED прожектор 200W',
            'price': 24999.99,
            'old_price': 29999.99,
            'stock': 15,
            'is_popular': True,
            'is_new': True,
            'brand': 'StageLight Pro',
        },
        {
            'name': 'Концертная акустическая система 1000W',
            'slug': 'concert-speaker-1000w',
            'category': categories['sound'],
            'description': 'Мощная акустическая система для концертов и мероприятий.',
            'short_description': 'Акустика 1000W для концертов',
            'price': 54999.99,
            'stock': 8,
            'is_popular': True,
            'brand': 'SoundMaster',
        },
        {
            'name': 'Дым-машина профессиональная',
            'slug': 'fog-machine-pro',
            'category': categories['effects'],
            'description': 'Профессиональная дым-машина для создания эффектов.',
            'short_description': 'Профессиональная дым-машина',
            'price': 18999.99,
            'stock': 12,
            'is_new': True,
            'brand': 'EffectPro',
        },
        {
            'name': 'Сценический кабель XLR 10м',
            'slug': 'xlr-cable-10m',
            'category': categories['cables'],
            'description': 'Качественный сценический кабель XLR длиной 10 метров.',
            'short_description': 'Кабель XLR 10 метров',
            'price': 1499.99,
            'stock': 50,
            'brand': 'CablePro',
        },
        {
            'name': 'Световой контроллер DMX',
            'slug': 'dmx-light-controller',
            'category': categories['control'],
            'description': 'Профессиональный контроллер для управления светом по протоколу DMX.',
            'short_description': 'Контроллер DMX для света',
            'price': 32999.99,
            'old_price': 35999.99,
            'stock': 6,
            'is_popular': True,
            'brand': 'ControlTech',
        },
        {
            'name': 'Сценический монитор 300W',
            'slug': 'stage-monitor-300w',
            'category': categories['sound'],
            'description': 'Сценический монитор для музыкантов мощностью 300W.',
            'short_description': 'Сценический монитор 300W',
            'price': 21999.99,
            'stock': 10,
            'is_new': True,
            'brand': 'StageSound',
        },
        {
            'name': 'Лазерный проектор RGB',
            'slug': 'laser-projector-rgb',
            'category': categories['effects'],
            'description': 'Профессиональный лазерный проектор с RGB лучами.',
            'short_description': 'Лазерный проектор RGB',
            'price': 42999.99,
            'stock': 4,
            'brand': 'LaserPro',
        },
        {
            'name': 'Сценическая конструкция 3x3м',
            'slug': 'stage-construction-3x3',
            'category': categories['stage'],
            'description': 'Прочная сценическая конструкция размером 3x3 метра.',
            'short_description': 'Сценическая конструкция 3x3м',
            'price': 89999.99,
            'stock': 3,
            'brand': 'StageBuild',
        },
    ]
    
    # Создаем простое изображение для товаров
    def create_test_image():
        image = Image.new('RGB', (800, 600), color='purple')
        image_io = BytesIO()
        image.save(image_io, 'JPEG')
        return File(image_io, name='test_product.jpg')
    
    for prod_data in products_data:
        product, created = Product.objects.get_or_create(
            slug=prod_data['slug'],
            defaults=prod_data
        )
        if created:
            # Создаем тестовое изображение
            product.image.save('test_product.jpg', create_test_image())
            product.save()
            print(f'Создан товар: {product.name} - {product.price} руб.')
    
    print('\nТестовые данные созданы успешно!')
    print(f'Категорий: {Category.objects.count()}')
    print(f'Товаров: {Product.objects.count()}')
    print(f'Пользователей: {AuthUser.objects.count()}')

if __name__ == '__main__':
    create_test_data()