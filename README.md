# API_YaMDb

### Описание проекта

Проект создан в рамках учебного курса Яндекс.Практикум.

Проект сервиса API для YaMDB - социальной сети, которая собирает отзывы и оценки пользователей на произведения в разных категориях и жанрах, а так же комментарии к отзывам. На основании оценок рассчитывается общий рейтинг произведения. Произведения делятся на категории и жанры, список которых может быть расширен только администратором. Для авторизации пользователей используется код подтверждения.

Реализован REST API CRUD для моделей проекта, для аутентификации примненяется JWT-токен. В проекте реализованы пермишены, фильтрации, сортировки и поиск по запросам клиентов, реализована пагинация ответов от API. Проект разворачивается в Docker контейнерах: web-приложение, postgresql-база данных и nginx-сервер.

### Системные требования

* Python 3.7+
* Docker
* Works on Linux, Windows, macOS


### Стек технологий

* Python 3.7
* Django 2.2
* Django Rest Framework
* Simple-JWT
* PostreSQL
* Nginx
* Gunicorn
* Docker
* DockerHub


### Установка проекта из репозитория

1. Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone git@github.com:olyakorchagina/API_YaMDb.git

cd API_YaMDb
```

2. Cоздать и открыть файл ```.env``` с переменными окружения:
```bash
cd infra

touch .env
```

3. Заполнить ```.env``` файл с переменными окружения по примеру:
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgrespassword
DB_HOST=db
DB_PORT=5432
```

4. Запустить приложения в контейнерах:
```bash
docker-compose up -d --build
```

5. Выполнить миграции, создать суперпользователя, собрать статику, заполнить базу данными:
```bash
docker-compose exec web python manage.py migrate

docker-compose exec web python manage.py createsuperuser

docker-compose exec web python manage.py collectstatic --no-input

docker-compose exec web python manage.py loaddata fixtures.json
```

### Документация к проекту

Документация для API доступна по адресу [/redoc/](http://localhost/redoc/) после установки приложения.
