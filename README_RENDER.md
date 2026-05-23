# Гайд по деплою Django проекта на Render.com

## 📋 Подготовка проекта

### 1. Убедитесь, что у вас есть все необходимые файлы:
```
showsystem/
├── requirements.txt          # Зависимости Python
├── runtime.txt              # Версия Python (python-3.11.0)
├── render.yaml              # Конфигурация Render
├── Procfile                 # Конфигурация процесса
├── build.sh                 # Скрипт сборки
├── start.sh                 # Скрипт запуска
├── .env.example             # Пример переменных окружения
├── .gitignore              # Игнорируемые файлы
└── showsystem/             # Настройки Django
```

### 2. Проверьте ключевые настройки в `settings.py`:
```python
# Должны быть настроены:
DEBUG = os.environ.get('DEBUG', 'True') == 'True'  # По умолчанию True для разработки
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') if os.environ.get('ALLOWED_HOSTS') else ['*']

# Для production:
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## 🚀 Шаги для деплоя на Render.com

### Вариант 1: Используя Blueprint (рекомендуется)

1. **Загрузите проект на GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/ваш-username/ваш-репозиторий.git
   git push -u origin main
   ```

2. **Создайте аккаунт на Render.com**
   - Перейдите на [render.com](https://render.com)
   - Зарегистрируйтесь через GitHub

3. **Создайте новый Blueprint**
   - Нажмите "New +" → "Blueprint"
   - Подключите ваш GitHub репозиторий
   - Render автоматически обнаружит `render.yaml`

4. **Настройте Blueprint**
   - Проверьте настройки в интерфейсе
   - Нажмите "Apply" для создания сервисов

### Вариант 2: Вручную через Web Service

1. **Загрузите проект на GitHub** (как в варианте 1)

2. **Создайте Web Service**
   - Нажмите "New +" → "Web Service"
   - Подключите ваш GitHub репозиторий

3. **Настройте сервис:**
   - **Name**: `showsystem` (или любое другое имя)
   - **Environment**: `Python`
   - **Build Command**: `./build.sh`
   - **Start Command**: `./start.sh`

4. **Добавьте переменные окружения:**
   - `SECRET_KEY`: (сгенерировать)
   - `DEBUG`: `false`
   - `ALLOWED_HOSTS`: `.onrender.com`
   - `DATABASE_URL`: (будет создана автоматически)

5. **Создайте базу данных:**
   - Нажмите "New +" → "PostgreSQL"
   - Название: `showsystem-db`
   - План: `Free`

6. **Свяжите базу данных с сервисом**
   - В настройках Web Service добавьте ссылку на базу данных

### Вариант 3: Через командную строку (Render CLI)

1. **Установите Render CLI**
   ```bash
   npm install -g @renderinc/cli
   ```

2. **Войдите в систему**
   ```bash
   render login
   ```

3. **Создайте сервисы из render.yaml**
   ```bash
   render blueprint launch
   ```

## ⚙️ Настройки для Production

### Переменные окружения на Render.com:
```
SECRET_KEY=ваш-секретный-ключ-сгенерировать
DEBUG=false
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=postgresql://user:pass@host:port/dbname
DISABLE_COLLECTSTATIC=0
```

### Важные моменты:

1. **Статические файлы**: Используется WhiteNoise для обслуживания статических файлов
2. **База данных**: PostgreSQL автоматически создается и настраивается
3. **Медиа файлы**: Для production рекомендуется использовать облачное хранилище (S3, Cloudinary)
4. **Логи**: Доступны в панели управления Render

## 🔧 Устранение неполадок

### Если возникает ошибка 500:

1. **Проверьте логи в Render Dashboard**
   - Зайдите в ваш сервис на Render
   - Нажмите "Logs" для просмотра ошибок

2. **Распространенные проблемы:**

   **Проблема**: `Missing staticfiles manifest entry`
   **Решение**: Убедитесь, что `collectstatic` выполняется в build.sh

   **Проблема**: `Database connection error`
   **Решение**: Проверьте переменную `DATABASE_URL`

   **Проблема**: `ImportError: No module named`
   **Решение**: Проверьте `requirements.txt`

3. **Локальная проверка перед деплоем:**
   ```bash
   # Установите зависимости
   pip install -r requirements.txt
   
   # Примените миграции
   python manage.py migrate
   
   # Соберите статические файлы
   python manage.py collectstatic
   
   # Запустите сервер
   python manage.py runserver
   ```

## 📞 Поддержка

### Полезные ссылки:
- [Документация Render](https://render.com/docs)
- [Документация Django](https://docs.djangoproject.com/)
- [Документация WhiteNoise](http://whitenoise.evans.io/)

### Контакты:
- Поддержка Render: https://render.com/contact
- Сообщество: https://community.render.com/

## 🎉 Поздравляем!

Ваш Django проект теперь готов к деплою на Render.com. После успешного деплоя вы получите URL вида:
```
https://showsystem.onrender.com
```

Не забудьте:
1. Создать суперпользователя через консоль Render
2. Настроить домен (если нужно)
3. Регулярно делать бэкапы базы данных