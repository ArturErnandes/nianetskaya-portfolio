# nianetskaya-portfolio — сайт-портфолио Нии Винецкой

Проект на **FastAPI + PostgreSQL** для сайта художника-иллюстратора: публичные страницы работ/проектов, административные формы добавления контента, хранение изображений на диске и автоматическая генерация миниатюр.

Публичный веб работает через **Nginx**: он отдает HTML/CSS/JS и `assets`, а `/api/*` и защищенные `/admin/*` маршруты проксирует в backend.

## Онлайн-версия

- [https://nianetskaya.ru](https://nianetskaya.ru)

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

- Перед запуском создайте `data.json` в корне репозитория по спецификации из `docs/CONFIG.md`.
- Backend запускается на `app.host:app.port` из `data.json`.
- Для корректной работы нужен доступный PostgreSQL из `data.json.database`.

## Изображения и миниатюры

- Оригиналы хранятся в `assets/works/`.
- Миниатюры (`webp`) создаются в `assets/works/thumbs/`.

## Документация

- [docs/DATABASE.md](docs/DATABASE.md) — структура базы данных: таблицы, ключи, индексы и связи.
- [docs/CONFIG.md](docs/CONFIG.md) — описание конфигурации проекта (`data.json`)

## Структура репозитория

```text
backend/      FastAPI, авторизация, доступ к БД, обработчики загрузки
frontend/     HTML/CSS/JS (мультистраничный frontend)
assets/       статические файлы и изображения работ
migrations/   SQL-файлы структуры БД
docs/         техническая документация
nginx.conf    production-конфиг Nginx для домена
```
