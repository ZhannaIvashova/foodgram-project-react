# Проект «Foodgram»
**Foodgram — социальная сеть для публикации рецептов.**
## Описание
*Проект «Foodgram» - это сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.*
## Технологии
- Python 3.10
- Django 3.2.3
- DjangoRestFramework 3.12.4
- PostgreSQL
- Nginx
- React
- Node.js
- Docker
## Ссылка на развернутое приложение
- https://foodgr.ddns.net/
### Запуск проекта через docker-compose
- Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:ZhannaIvashova/foodgram-project-react.git
cd foodgram-project-react
```
- В корне проекта создать файл .env:
(например)
```
POSTGRES_DB=foodgram
POSTGRES_USER=food_user
POSTGRES_PASSWORD=Ff1234567
```
- Запустить проект:
```
docker compose up
``` 
- Выполнить миграции, создать суперпользователя и собрать статику:
```
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py collectstatic
```
- Загрузить файл с ингредиентами:
```
docker-compose exec backend python manage.py ingredients_import
```
### Пользователи для проекта на удаленном сервере
- Админ: логин: user1, почта: user1@gmail.com, пароль: Uu123456
- Тестовый пользователь1: user2, user2@gmail.com, ss123456
- Тестовый пользователь2: user3, user3@gmail.com, rr123456

### Обратная связь
IvashovaHome@yandex.ru
