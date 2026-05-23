import sys
import os
import django
from django.test import Client
from django.conf import settings

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'showsystem.settings')
django.setup()

def check_errors():
    client = Client()
    
    print("Проверяю главную страницу...")
    try:
        response = client.get('/')
        print(f"Статус код: {response.status_code}")
        if response.status_code == 500:
            print("Ошибка 500 обнаружена!")
            # Попробуем получить больше информации
            from django.views.debug import ExceptionReporter
            import traceback
            print("\nПопытка получить traceback...")
        else:
            print("Страница загружается успешно!")
    except Exception as e:
        print(f"Исключение при запросе: {e}")
        print("\nTraceback:")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*50)
    print("Проверяю другие страницы...")
    
    # Проверяем другие URL
    urls_to_check = [
        '/catalog/',
        '/about/',
        '/contacts/',
        '/admin/',
    ]
    
    for url in urls_to_check:
        try:
            response = client.get(url)
            print(f"{url}: {response.status_code}")
        except Exception as e:
            print(f"{url}: Ошибка - {e}")

if __name__ == "__main__":
    check_errors()