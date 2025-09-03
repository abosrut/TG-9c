import sqlite3
from datetime import date, timedelta

DB_NAME = 'schedule.db'

HARDCODED_SCHEDULE = [
    ('Пн', 1, 'Французский язык', '08:10 - 08:55'),
    ('Пн', 2, 'Украинский язык', '09:00 - 09:45'),
    ('Пн', 3, 'Украинская литература', '09:55 - 10:40'),
    ('Пн', 4, 'Алгебра', '10:50 - 11:35'),
    ('Пн', 5, 'Зарубежная литература', '12:00 - 12:45'),
    ('Пн', 6, 'История Украины', '12:55 - 13:40'),
    ('Пн', 7, 'Физкультура', '13:50 - 14:35'),
    ('Вт', 1, 'Искусство', '08:10 - 08:55'),
    ('Вт', 2, 'Английский язык', '09:00 - 09:45'),
    ('Вт', 3, 'Физика', '09:55 - 10:40'),
    ('Вт', 4, 'Физика', '10:50 - 11:35'),
    ('Вт', 5, 'Алгебра', '12:00 - 12:45'),
    ('Вт', 6, 'Алгебра', '12:55 - 13:40'),
    ('Вт', 7, 'История Украины', '13:50 - 14:35'),
    ('Вт', 8, 'Английский язык', '14:40 - 15:25'),
    ('Ср', 1, 'Алгебра', '08:10 - 08:55'),
    ('Ср', 2, 'Химия', '09:00 - 09:45'),
    ('Ср', 3, 'Украинская литература', '09:55 - 10:40'),
    ('Ср', 4, 'Украинский язык', '10:50 - 11:35'),
    ('Ср', 5, 'Зарубежная литература', '12:00 - 12:45'),
    ('Ср', 6, 'Английский язык', '12:55 - 13:40'),
    ('Ср', 7, 'Английский язык', '13:50 - 14:35'),
    ('Ср', 8, 'Физика', '14:40 - 15:25'),
    ('Чт', 1, 'Классный час', '08:10 - 08:55'),
    ('Чт', 2, 'Биология', '09:00 - 09:45'),
    ('Чт', 3, 'Физкультура', '09:55 - 10:40'),
    ('Чт', 4, 'Химия', '10:50 - 11:35'),
    ('Чт', 5, 'Геометрия', '12:00 - 12:45'),
    ('Чт', 6, 'География', '12:55 - 13:40'),
    ('Чт', 7, 'Информатика', '13:50 - 14:35'),
    ('Пт', 1, 'Основы здоровья', '08:10 - 08:55'),
    ('Пт', 2, 'Всемирная история', '09:00 - 09:45'),
    ('Пт', 3, 'Технологии', '09:55 - 10:40'),
    ('Пт', 4, 'Французский язык', '10:50 - 11:35'),
    ('Пт', 5, 'Правоведение', '12:00 - 12:45'),
    ('Пт', 6, 'Информатика', '12:55 - 13:40'),
    ('Пт', 7, 'Биология', '13:50 - 14:35'),
    ('Пт', 8, 'Физкультура', '14:40 - 15:25'),
]
DAYS_ORDER = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт']

def init_and_populate_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT, day_of_week TEXT NOT NULL, lesson_number INTEGER NOT NULL,
        subject_name TEXT NOT NULL, lesson_time TEXT )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS homework (
        id INTEGER PRIMARY KEY AUTOINCREMENT, subject_name TEXT NOT NULL, due_date TEXT NOT NULL,
        task TEXT NOT NULL, is_completed INTEGER DEFAULT 0 )''')
    cursor.execute("DELETE FROM schedule")
    cursor.executemany(
        "INSERT INTO schedule (day_of_week, lesson_number, subject_name, lesson_time) VALUES (?, ?, ?, ?)",
        HARDCODED_SCHEDULE )
    conn.commit()
    conn.close()

def add_homework(subject, due_date, task):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO homework (subject_name, due_date, task) VALUES (?, ?, ?)",
        (subject, due_date, task) )
    conn.commit()
    conn.close()

def get_schedule_for_day(day_of_week):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT lesson_number, subject_name, lesson_time FROM schedule WHERE day_of_week = ? ORDER BY lesson_number", (day_of_week,))
    schedule = cursor.fetchall()
    conn.close()
    return schedule

def find_subject_schedule(subject_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT subject_name FROM schedule")
    all_subjects = [row[0] for row in cursor.fetchall()]

    user_query_lower = subject_name.lower()
    matching_subjects = [
        s for s in all_subjects if s.lower().startswith(user_query_lower)
    ]

    if not matching_subjects:
        conn.close()
        return []

    placeholders = ', '.join('?' for s in matching_subjects)
    query = f"SELECT day_of_week, lesson_number, lesson_time FROM schedule WHERE subject_name IN ({placeholders}) ORDER BY day_of_week, lesson_number"
    
    cursor.execute(query, matching_subjects)
    result = cursor.fetchall()
    conn.close()
    return result

def get_homework_for_date(due_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT subject_name, task FROM homework WHERE due_date = ?", (due_date,))
    homework = cursor.fetchall()
    conn.close()
    return homework

def get_subjects_by_frequency():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT subject_name, COUNT(subject_name) as c FROM schedule GROUP BY subject_name ORDER BY c DESC")
    subjects = [row[0] for row in cursor.fetchall()]
    conn.close()
    return subjects

def get_next_lesson_date(subject, from_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    start_day_index = from_date.weekday()
    ordered_days_of_week = DAYS_ORDER[start_day_index:] + DAYS_ORDER[:start_day_index]
    for day_offset, day_name_ukr in enumerate(ordered_days_of_week):
        if day_offset == 0 and from_date.weekday() != DAYS_ORDER.index(day_name_ukr):
            continue
        cursor.execute("SELECT COUNT(*) FROM schedule WHERE day_of_week = ? AND subject_name = ?", (day_name_ukr, subject))
        if cursor.fetchone()[0] > 0:
            next_date = from_date + timedelta(days=day_offset)
            conn.close()
            return next_date.strftime("%Y-%m-%d")
    conn.close()
    return None

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn