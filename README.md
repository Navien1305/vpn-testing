# MVP сервиса тестирования VPN и мессенджеров

Django-сервис для сбора результатов тестирования VPN-приложений и мессенджеров.

Реализовано:

- регистрация и авторизация пользователей;
- роли и подтверждение пользователей администратором;
- организации, города, операторы связи и справочники;
- справочник VPN-приложений с периодами;
- VPN-анкеты, первый и второй замер;
- согласование и возврат замеров куратором;
- PostgreSQL в Docker.

Анкеты мессенджеров, Telegram-интеграция и аналитические дашборды пока не реализованы.

## Стек

- Python 3.12
- Django
- PostgreSQL 16
- Docker Compose
- Gunicorn
- Django Templates
- Bootstrap 5
- openpyxl

## Структура

```text
config/          настройки проекта и корневые URL
accounts/        пользователи, роли, регистрация, подтверждение
references/      организации, города, операторы связи, VPN, мессенджеры
questionnaires/  VPN-анкеты, замеры и результаты проверки
core/            главная страница и личный кабинет
templates/       HTML-шаблоны Bootstrap
static/          статические файлы
```

## Переменные окружения

Создайте `.env` из примера:

```bash
cp .env.example .env
```

На Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Минимально проверьте значения:

```env
SECRET_KEY=change-me
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost

POSTGRES_DB=vpn_testing
POSTGRES_USER=vpn_testing
POSTGRES_PASSWORD=change-me
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Реальный `.env` не добавляйте в репозиторий.

## Запуск через Docker Compose

Собрать и запустить PostgreSQL и Django:

```bash
docker compose up -d --build
```

Сервис Django будет доступен только локально:

```text
http://127.0.0.1:8010/
```

Nginx-контейнер не используется. Если нужен внешний доступ, проксируйте хостовым Nginx на `127.0.0.1:8010`.

## Миграции и статика

При старте `web` автоматически выполняет:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

Вручную применить миграции:

```bash
docker compose exec web python manage.py migrate
```

Заполнить базовые справочники:

```bash
docker compose exec web python manage.py seed_initial_data
```

Создать администратора без интерактивного ввода:

```bash
docker compose exec web python manage.py create_admin --username admin --password "change-me"
```

На Windows лучше не вводить кириллицу в интерактивной консоли Docker. Русское ФИО администратора можно поменять позже через Django Admin в браузере.

Если хотите использовать переменные из `.env`, заполните:

```env
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=change-me
DJANGO_SUPERUSER_FULL_NAME=admin
```

И выполните:

```bash
docker compose exec web python manage.py create_admin
```

## Логи

Посмотреть логи всех сервисов:

```bash
docker compose logs -f
```

Только Django:

```bash
docker compose logs -f web
```

Только PostgreSQL:

```bash
docker compose logs -f db
```

## Остановка

Остановить контейнеры без удаления данных:

```bash
docker compose down
```

Данные PostgreSQL хранятся в Docker volume `postgres_data`.

## Backup PostgreSQL

Создать дамп:

```bash
docker compose exec db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" > backup.sql
```

В PowerShell удобнее явно указать значения из `.env`:

```powershell
docker compose exec db pg_dump -U vpn_testing -d vpn_testing > backup.sql
```

## Restore PostgreSQL

Восстановить дамп в существующую базу:

```bash
docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < backup.sql
```

PowerShell-вариант:

```powershell
Get-Content backup.sql | docker compose exec -T db psql -U vpn_testing -d vpn_testing
```

## Основные URL

- `/` - главная страница;
- `/accounts/register/` - регистрация;
- `/accounts/login/` - вход;
- `/accounts/users/` - управление пользователями для администратора;
- `/references/` - справочники;
- `/vpn/forms/` - список VPN-анкет;
- `/vpn/forms/create/` - создание VPN-анкеты;
- `/vpn/review/` - VPN-анкеты на проверку;
- `/admin/` - Django Admin.

## Роли

- `tester` - создает и заполняет свои VPN-анкеты.
- `coordinator` - проверяет анкеты своей организации, согласует и возвращает замеры.
- `reader` - просматривает доступные данные без редактирования.
- `admin` - управляет пользователями, справочниками и анкетами.

Суперпользователь Django автоматически получает роль администратора и статус подтверждения.

## Проверка после запуска

1. Запустите контейнеры: `docker compose up -d --build`.
2. Выполните `docker compose exec web python manage.py seed_initial_data`.
3. Создайте администратора через `create_admin`.
4. Зайдите в `/admin/` и проверьте справочники.
5. Зарегистрируйте пользователя через `/accounts/register/`.
6. Подтвердите пользователя администратором.
7. Под тестировщиком создайте VPN-анкету.
8. Пройдите первый замер.
9. Отправьте анкету куратору.
10. Под куратором откройте `/vpn/review/`, проверьте замер, согласуйте или верните его.
