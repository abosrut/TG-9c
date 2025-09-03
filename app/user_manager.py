import json
import os

USER_FILE = 'user_data.json'

def load_user_data():
    if not os.path.exists(USER_FILE):
        return {'users': {}, 'next_user_number': 1}
    try:
        with open(USER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {'users': {}, 'next_user_number': 1}

def save_user_data(data):
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def register_user(chat_id):
    chat_id_str = str(chat_id)
    data = load_user_data()
    
    if chat_id_str in data['users']:
        return data['users'][chat_id_str]
    
    if data['next_user_number'] > 30:
        return None 

    new_user_number = data['next_user_number']
    data['users'][chat_id_str] = new_user_number
    data['next_user_number'] += 1
    
    save_user_data(data)
    return new_user_number