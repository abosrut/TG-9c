from flask import Flask, render_template, jsonify, request
import os
import sys
from datetime import datetime
import psycopg2.extras

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
from app import database_manager

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/schedule')
def get_schedule():
    conn = database_manager.get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT day_of_week, lesson_number, subject_name, lesson_time FROM schedule ORDER BY day_of_week, lesson_number")
    rows = cursor.fetchall()
    conn.close()
    
    schedule_data = { 'Пн': [], 'Вт': [], 'Ср': [], 'Чт': [], 'Пт': [] }
    for row in rows:
        day = row['day_of_week']
        if day in schedule_data:
            # Вот здесь исправление - мы переименовываем ключи
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
    due_date = database_manager.get_next_lesson_date(subject, from_date)
    
    if due_date:
        database_manager.add_homework(subject, due_date, task)
        return jsonify({'status': 'success', 'message': f'Homework for {subject} added.'})
    else:
        return jsonify({'status': 'error', 'message': 'Could not find next lesson date.'}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)