# Система аутентификации и авторизации

Собственная реализация системы управления доступом на Django REST Framework.

## Архитектура системы

Система построена на комбинированной модели управления доступом:

1. Дискреционное управление (через роли) - пользователи объединяются в роли, ролям назначаются разрешения
2. Привилегированный доступ - флаг is_superuser дает полный доступ без проверки прав

Схема взаимодействия компонентов:
- Обычный путь: Пользователь → Роли → Разрешения → Доступ к ресурсам
- Путь суперпользователя: is_superuser = true → Полный доступ

## Модели данных

### Модель пользователя (accounts.CustomUser)

Наследуется от AbstractBaseUser и PermissionsMixin. В качестве идентификатора используется email.

Поля:
- email - уникальный email для входа
- first_name - имя
- last_name - фамилия
- patronymic - отчество
- is_active - флаг мягкого удаления
- is_staff - доступ к админке
- is_superuser - полные права

### Модель Role (Роль)

Поля:
- name - название роли
- description - описание роли

### Модель Permission (Разрешение)

Поля:
- codename - код разрешения (например "user_view")
- description - описание

### Модель RolePermission

Связывает роли с разрешениями.

### Модель UserRole

Связывает пользователей с ролями.

## Установка и запуск

1. Клонирование репозитория
   git clone <url>
   cd auth_project

2. Виртуальное окружение
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows

3. Зависимости
   pip install -r requirements.txt

4. Создайте базу данных PostgreSQL
   CREATE DATABASE auth_db;

5. Создайте файл .env
   SECRET_KEY=your-secret-key
   DEBUG=True
   DB_NAME=auth_db
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432

6. Миграции
   python manage.py migrate
   python manage.py loaddata access_control/fixtures/initial_data.json
   python manage.py createsuperuser
   python manage.py runserver

## API Эндпоинты

### Аутентификация
- POST /api/auth/register/ - регистрация
- POST /api/auth/login/ - вход
- POST /api/auth/logout/ - выход
- GET /api/auth/profile/ - профиль
- PUT/PATCH /api/auth/profile/update/ - обновление профиля
- DELETE /api/auth/profile/delete/ - мягкое удаление аккаунта

### Управление доступом
- GET /api/access/documents/ - список документов (требуется document_view)
- GET /api/access/projects/ - список проектов (требуется project_view)
- GET /api/access/users/ - список пользователей (требуется user_view)
- GET /api/access/check-permissions/ - проверка прав текущего пользователя
- POST /api/access/assign-role/ - назначение роли (только для администраторов)

## Примеры запросов

### Регистрация
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "first_name": "Иван", "last_name": "Иванов", "password": "Test123456", "password2": "Test123456"}'

### Логин
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Test123456"}' \
  -c cookies.txt

### Проверка прав
curl -X GET http://localhost:8000/api/access/check-permissions/ -b cookies.txt

### Доступ к документам
curl -X GET http://localhost:8000/api/access/documents/ -b cookies.txt

## Коды ответов

- 401 - не аутентифицирован или аккаунт деактивирован
- 403 - аутентифицирован, но нет прав
- 200 - успешно
- 400 - ошибка в данных запроса
- 201 - создано успешно