#!/bin/bash

# Устанавливаем все зависимости
pip install -r requirements.txt

# Запускаем веб-сервер Flask в фоновом режиме
# Знак '&' в конце означает "запустить в фоне"
python webapp/backend/server.py &

# Запускаем бота в основном (foreground) режиме
# Этот процесс будет держать сервис активным
python main.py