# ShowSystem - Интернет-магазин

Django-приложение для интернет-магазина.

## Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd showsystem
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env:
```bash
cp .env.example .env
# Отредактируйте .env файл
```

5. Примените миграции:
```bash
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустите сервер:
```bash
python manage.py runserver
```

## Деплой на render.com

### Вариант 1: Используя render.yaml
1. Загрузите проект на GitHub
2. Войдите на [render.com](https://render.com)
3. Нажмите "New +" → "Blueprint"
4. Подключите ваш GitHub репозиторий
5. Render автоматически обнаружит render.yaml и настроит приложение

### Вариант 2: Вручную
1. Загрузите проект на GitHub
2. Войдите на [render.com](https://render.com)
3. Нажмите "New +" → "Web Service"
4. Подключите ваш GitHub репозиторий
5. Настройте:
   - **Name**: showsystem
   - **Environment**: Python
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn showsystem.wsgi:application`
6. Добавьте переменные окружения:
   - `SECRET_KEY` (сгенерировать)
   - `DEBUG`: `false`
   - `DATABASE_URL` (будет создана автоматически)
7. Нажмите "Create Web Service"

## Структура проекта

```
showsystem/
├── shop/              # Основное приложение магазина
├── api/               # API приложение
├── showsystem/        # Настройки проекта
├── static/            # Статические файлы
├── media/             # Медиа файлы
├── templates/         # Шаблоны
├── requirements.txt   # Зависимости Python
├── runtime.txt        # Версия Python
├── render.yaml        # Конфигурация Render
├── Procfile           # Конфигурация процесса
├── build.sh           # Скрипт сборки
└── .env.example       # Пример переменных окружения
```

## Особенности

- Использует PostgreSQL на production
- Статические файлы обслуживаются через WhiteNoise
- Поддержка CORS для API
- REST API через Django REST Framework
- Аутентификация пользователей
- Корзина покупок
- Система заказов
- Отзывы и рейтинги товаров