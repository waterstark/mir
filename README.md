# mir

## Dependencies
* python 3.10/3.11/3.12
* python-poetry
* postgresql
* mongodb
* redis


## Запуск в докере
Создать файл .env в корне проекта: скопировать содержимое из .env-example и настроить под себя, если надо
```sh
cat .env-example > .env
```
Поднять контейнеры
```sh
docker compose up app
```
После этого бэкенд будет доступен по адресу http://localhost:8000 

## Локальная установка
Активация виртуального окружения
```sh
poetry shell
```
Установить зависимости
```sh
poetry install
```
Создать файл .env в корне проекта: скопировать содержимое из .env-example и настроить под себя, если надо
```sh
cat .env-example > .env
```
Создать файлы с ключами RSA для выпуска токенов
```shell
# Создание приватного RSA ключа, размер 2048
openssl genrsa -out jwt-private.pem 2048

# Создание публичного ключа при помощи приватного ключа
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```
Запустить сервисы (postgresql, mongodb и redis) или поднять их в контейнере с помощью:
```sh
docker compose up -d --build --remove-orphans
```
Сделать миграции
```sh
alembic upgrade head
```
Запустить проект
```sh
uvicorn src.main:app --reload
```

## Запуск тестов в докере
```sh
docker-compose up test_app
```

### Работа с pgAdmin
1. Вход в систему  
Логин - указать значение PGADMIN_DEFAULT_EMAIL из файла .env
Пароль - указать значение PGADMIN_DEFAULT_PASSWORD из файла .env
2. Добавление базы
 - правой кнопкой по servers. Далее register -> server
 - В открывшемся окне (Вкладка Generals) указать имя
 - Вкладка connection, указать:
host name - db
Port - указать значение DB_PORT из файла .env
Maintenance database - указать значение DB_NAME из файла .env
Username - указать значение DB_USER из файла .env
Password - указать значение DB_PASS из файла .env
