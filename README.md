# mir

## Установка   
Активация виртуального окружения
```sh
poetry shell
```
Установить зависимости
```sh
poetry install
```
Создать файл .env в корне проекта, и скопировать содержимое из .env-example
```sh
cat .env-example > .env
```
Развернуть Postgres 
```sh
docker compose up -d
```
Запустить проект
```sh
uvicorn src.main:app --reload
```