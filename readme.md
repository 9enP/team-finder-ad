# TeamFinder — Вариант 1

## Автор

ФИО: Просвирнин Денис Александрович  
GitHub: [9enP](https://github.com/9enP)

---

## Технологии

- Python
- Django
- PostgreSQL
- Docker
- Docker Compose
- Pytest
- GitHub Actions

---

## Клонирование репозитория

```bash
git clone https://github.com/9enP/team-finder-ad.git
cd team-finder-ad
```

---

## Локальный запуск (Docker Compose)

Рекомендуемый способ: приложение и PostgreSQL поднимаются вместе.

### 1. Настройка окружения

Скопируйте файл окружения:

```bash
cp .env_example .env
```

При необходимости отредактируйте `.env`.

Для сервиса `web` в `docker-compose.yml` используется:

```env
DB_HOST=db
```

что позволяет приложению подключаться к контейнеру PostgreSQL.

---

### 2. Сборка и запуск контейнеров

```bash
docker compose up --build
```

Миграции выполняются автоматически при старте.

---

### 3. Загрузка тестовых данных

```bash
docker compose exec web python manage.py create_test_data
```

Команда выполняется один раз после первого запуска или при необходимости повторного заполнения базы.

---

### 4. Открытие проекта

- [Сайт](http://localhost:8000)
- [Админ-панель](http://localhost:8000/admin/)

---

## Тестовые аккаунты

| Роль | Email | Пароль |
|------|--------|--------|
| Администратор | admin@admin.com | admin |
| Пользователь | maria@example.com | password123 |
| Пользователь | alex@example.com | password123 |
| Пользователь | kate@example.com | password123 |

---

### Остановка контейнеров

```bash
docker compose down
```

Данные PostgreSQL и медиафайлы сохраняются в Docker volumes:

- `postgres_data`
- `media_data`

Для полной очистки:

```bash
docker compose down -v
```

---

## Локальный запуск без Docker

Требуется установленный PostgreSQL.

В файле `.env` укажите:

```env
DB_HOST=localhost
```

а также остальные параметры `DB_*` в соответствии с настройками локальной базы данных.

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Применение миграций

```bash
python manage.py migrate
```

### Загрузка тестовых данных

```bash
python manage.py create_test_data
```

### Запуск сервера

```bash
python manage.py runserver
```

---

## Тесты

### Запуск через pytest

```bash
pytest
```

### Запуск через Docker

```bash
docker compose exec web pytest
```

В CI (GitHub Actions) тесты выполняются с PostgreSQL  
(см. `.github/workflows/check.yml`).
