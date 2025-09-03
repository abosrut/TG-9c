from flask import Flask, render_template, jsonify, request
import sqlite3
import os
import sys
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
from app.database_manager import DB_NAME, get_next_lesson_date, add_homework

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/schedule')
def get_schedule():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT day_of_week, lesson_number, subject_name, lesson_time FROM schedule ORDER BY day_of_week, lesson_number")
    rows = cursor.fetchall()
    conn.close()
    
    schedule_data = {
        'Пн': [], 'Вт': [], 'Ср': [], 'Чт': [], 'Пт': []
    }
    for row in rows:
        day = row['day_of_week']
        if day in schedule_data:
            schedule_data[day].append({
                'number': row['lesson_number'],
                'subject': row['subject_name'],
                'time': row['lesson_time']
            })
            
    return jsonify(schedule_data)

@app.route('/api/add_homework', methods=['POST'])
def add_homework_route():
    data = request.get_json()
    if not data or 'subject' not in data or 'task' not in data:
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400
    
    subject = data['subject']
    task = data['task']
    
    from_date = datetime.now().date()
    due_date = get_next_lesson_date(subject, from_date)
    
    if due_date:
        add_homework(subject, due_date, task)
        return jsonify({'status': 'success', 'message': f'Homework for {subject} added.'})
    else:
        return jsonify({'status': 'error', 'message': 'Could not find next lesson date.'}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)