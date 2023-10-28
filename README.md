## Гайд по запуску

### Докер (рекомендуется)
1. Скачать докер (можно и докер декстоп)
2. Запуск проекта (запускается сразу бэк и бд):
   1. Без изменений: `sudo docker-compose up` (для линукса, на винде должно быть без судо вроде)
   2. С изменениями: `sudo docker-compose up --build` (в целом всегда можно запускать билд и не париться)
3. Если запускается первый раз/контейнер удалялся/выскакивает ошибка с бд:
   1. `sudo docker-compose run --rm backend python manage.py makemigrations`
   2. `sudo docker-compose run --rm backend python manage.py migrate`


### Локалка
1. Скачать, установить и запустить MySQL
2. Создать базу данных и рут пользователя, настроить как в файлах в `db-config/`
3. Запустить на локалке на порту 3306 (дефолтный)
4. Сделать миграции в бд и применить их (makemigrations и migrate)
5. Запустить сервер (`python manage.py runserver`)