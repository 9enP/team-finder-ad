## TeamFinder — Вариант 1

### Локальный запуск (Docker Compose)

Рекомендуемый способ: приложение и PostgreSQL поднимаются вместе.

1. Скопируйте окружение: `cp .env.example .env` и при необходимости отредактируйте. Для сервиса `web` в `docker-compose.yml` задано `DB_HOST=db` (подключение к контейнеру PostgreSQL).

2. Сборка и запуск:

```bash
docker compose up --build
```

3. После успешного старта загрузите тестовые данные (один раз или при необходимости):

```bash
docker compose exec web python manage.py create_test_data
```

4. Откройте в браузере: http://localhost:8000/

Остановка: `docker compose down`. Данные БД и медиа — в томах `postgres_data` и `media_data`.

### Локально без Docker

Нужен установленный PostgreSQL; в `.env` укажите `DB_HOST=localhost` и остальные `DB_*` как у вашего сервера.

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Тесты

```bash
pip install -r requirements.txt
pytest
# или
python manage.py test
```

В CI (GitHub Actions) тесты выполняются с PostgreSQL (см. `.github/workflows/check.yml`).
