### Requirements:
    python3.8+
    linux (ubuntu)

### Deploy:
    
    1. Перейти в папку, в которой будет находиться проект.
    2. Склонировать данный репозиторий командой:
        git clone https://github.com/Deskent/pushapi.git

    3. Либо скачать его архивом и распаковать.    

    4. Перейти в созданную папку:
        cd pushapi

    5. Создать виртуальное окружение для python:
        python3.8 -m venv venv

    6. Активировать его:
        source ./venv/bin/activate

    7. Запустить команду  
        python -m pip install -U && python -m pip install -r requirements.txt

    8. Создать файл ".env"
    9. Скопировать в него переменные окружения из файла ".env-template"
    и настроить их.

    10. Запустить сервер:
        . ./start.sh
    или, если окружение активировано:
        python app/main.py