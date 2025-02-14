# Итоговый проект

------------


### Создание и активация виртуального окружения:

- **sudo apt install python3-virtualenv**
- **virtualenv venv**
- **source venv/bin/activate**

### Установка зависимостей:

- **pip install poetry**
- **poetry install**

### Вводная информация:
Т.к. у нас нет регистрации, то при запуске сразу создаётся тестовый пользователь с api-key: test, и если введённый api-key не существует, то программа автоматически переключит на тестового пользователя.

### 
### Запуск:
- **Разработка:**

    Если мы запускаем в режиме разработки, то в **my_twitter/app/database/DB_docker_for_debug/** есть **docker-compose.yaml** для БД, запускаем сначала его. А запускаем проект через **my_twitter/main_debug.py** .
    Папку **my_twitter** помечаем как **Sources Root**
- **На сервере:**
    
    Создаём и запускаем контейнеры **docker compose up -d --build**
    Переходим по адресу http://0.0.0.0/ (если запускаем на компьютере)

### Создание пользователей:

- **Разработка:**

    Переходим в **my_twitter** и выполняем **python manage.py createuser --debug**
- **На сервере**

    **docker exec -it fastapi_app python manage.py createuser**

Следуем сообщениям и вводим данные.
Примечание: Почему-то переключение языка при вводе python воспринимает (не всегда, что странно) как за символ, что вызывает исключение, поэтому удаляем этот невидимый символ путём нажатия клавиши **backspace**