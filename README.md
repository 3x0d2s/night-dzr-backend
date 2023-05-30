# night-dzr-backend

Backend-часть сервиса для проведения игры Ночной Дозор.

Шаги настройки проекта:
### Запустить БД
Для этого нужно скопировать файл `example.docker-compose.yaml` в файл с именем `docker-compose.yaml`.
После этого запустить docker-compose контейнер.

### Настроить переменные окружения
Для этого нужно скопировать файл `example.env` в файл с именем `.env`.
Затем нужно отредактировать файл `.env`, вписав свои локальные значения.

### Установка зависимостей
Сперва нужно установить Poetry - https://python-poetry.org/docs/#installation

Потом в директории проекта прописать:
```sh
$> poetry env use python
$> poetry shell
$> poetry install
```
