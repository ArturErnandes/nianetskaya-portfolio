# PostgreSQL Schema

Техническая спецификация структуры базы данных в PostgreSQL.

- Текущая SQL-реализация: `migrations/db_structure.sql`.

---

## 1. Логическая структура

| Таблица | Назначение |
|--------|------------|
| `works` | Отдельные работы портфолио по категориям |
| `projects` | Проекты (обложка + общий текст) по категориям |
| `project_images` | Галерея дополнительных изображений проекта с порядком показа |

---

## 2. Таблицы и поля

### 2.1. `works`

| Столбец | Тип / атрибут | Обязательность | Описание |
|--------|----------------|----------------|----------|
| `work_id` | `serial PK` | да | Идентификатор работы |
| `section_name` | `text` | да | Слаг категории (раздела) |
| `title` | `text` | да | Название работы |
| `caption` | `text` | да | Короткое описание для карточки |
| `description` | `text` | да | Полное описание работы |
| `img_name` | `text` | да | Имя файла изображения в `assets/works` |

Ограничения:

| Тип | Имя | Выражение |
|-----|-----|-----------|
| `PRIMARY KEY` | `works_pkey` | `(work_id)` |

### 2.2. `projects`

| Столбец | Тип / атрибут | Обязательность | Описание |
|--------|----------------|----------------|----------|
| `project_id` | `serial PK` | да | Идентификатор проекта |
| `section_name` | `text` | да | Слаг категории (раздела) |
| `title` | `text` | да | Название проекта |
| `caption` | `text` | да | Короткое описание проекта |
| `cover_img_name` | `text` | да | Имя файла обложки проекта |
| `description` | `text` | нет | Полное описание проекта |

Ограничения и индексы:

| Тип | Имя | Выражение |
|-----|-----|-----------|
| `PRIMARY KEY` | `projects_pkey` | `(project_id)` |
| `INDEX` | `idx_projects_section_name` | `(section_name)` |

### 2.3. `project_images`

| Столбец | Тип / атрибут | Обязательность | Описание |
|--------|----------------|----------------|----------|
| `image_id` | `serial PK` | да | Идентификатор изображения |
| `project_id` | `integer FK` | да | Ссылка на проект (`projects.project_id`) |
| `description` | `text` | нет | Подпись/описание изображения |
| `img_name` | `text` | да | Имя файла изображения в `assets/works` |
| `order_index` | `integer` | да | Позиция изображения в галерее проекта |

Ограничения и индексы:

| Тип | Имя | Выражение |
|-----|-----|-----------|
| `PRIMARY KEY` | `project_images_pkey` | `(image_id)` |
| `UNIQUE` | `project_images_project_order_key` | `(project_id, order_index)` |
| `INDEX` | `idx_project_images_project_id` | `(project_id)` |
| `FOREIGN KEY` | `project_images_project_id_fkey` | `(project_id) -> projects(project_id) ON DELETE CASCADE` |

---

## 3. Последовательности (Sequences)

| Sequence | Используется для |
|----------|------------------|
| `project_images_image_id_seq` | `project_images.image_id` |
| `projects_project_id_seq` | `projects.project_id` |
| `works_work_id_seq` | `works.work_id` |
