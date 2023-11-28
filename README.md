# mir

## Dependencies
* python 3.10+
* python-poetry
* postgresql
* mongodb
* redis


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
Развернуть контейнеры для подключения к базам данных 
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

## Запуск в докере
```shell
docker-compose up
```

## Запуск тестов в докере
Создать файл .env в корне проекта: скопировать содержимое из .env-example и настроить под себя, если надо
```sh
cat .env-example > .env
```
Поднять контейнеры
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
