### Requirements:
    python3.8+
    linux (ubuntu)

### Deploy:
    
    Перейти в папку, в которой будет находиться проект.
    Склонировать данный репозиторий командой:
        git clone https://github.com/Deskent/pushapi.git

    Либо скачать его архивом и распаковать.    

    Перейти в созданную папку:
        cd pushapi

    Создать виртуальное окружение для python:
        python3.8 -m venv venv
    Активировать его:
        source ./venv/bin/activate

    Запустить команду  
        python -m pip install -U && python -m pip install -r requirements.txt

    Создать файл ".env"
    Скопировать в него переменные окружения из файла ".env-template"
    и настроить их.

    Запустить сервер:
        . ./start.sh
    или, если окружение активировано:
        python app/main.py