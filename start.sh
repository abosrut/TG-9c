#!/bin/bash

pip install -r requirements.txt

# Шаг 1: Создаем/очищаем таблицы в базе данных PostgreSQL
echo "Initializing database..."
python -c "from app import database_manager; database_manager.init_and_populate_db()"
echo "Database initialized."

# Шаг 2: Запускаем веб-сервер в фоновом режиме
echo "Starting web server..."
python webapp/backend/server.py &

# Шаг 3: Запускаем бота в основном режиме
echo "Starting Telegram bot..."
python main.py