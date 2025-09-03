#!/bin/bash

pip install -r requirements.txt

echo "--- Initializing Database ---"
python -c "from app import database_manager; database_manager.init_and_populate_db()"
echo "--- Starting Web Server ---"
gunicorn --worker-class gevent --bind 0.0.0.0:$PORT webapp.backend.server:app &

echo "--- Starting Telegram Bot ---"
python main.py