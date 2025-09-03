import psycopg2
import psycopg2.extras
import os
from datetime import date, timedelta

DB_URL = os.getenv("DATABASE_URL")

HARDCODED_SCHEDULE = [
    ('Пн', 1, 'Французский язык', '08:10 - 08:55'), ('Пн', 2, 'Украинский язык', '09:00 - 09:45'),
    ('Пн', 3, 'Украинская литература', '09:55 - 10:40'), ('Пн', 4, 'Алгебра', '10:50 - 11:35'),
    ('Пн', 5, 'Зарубежная литература', '12:00 - 12:45'), ('Пн', 6, 'История Украины', '12:55 - 13:40'),
    ('Пн', 7, 'Физкультура', '13:50 - 14:35'), ('Вт', 1, 'Искусство', '08:10 - 08:55'),
    ('Вт', 2, 'Английский язык', '09:00 - 09:45'), ('Вт', 3, 'Физика', '09:55 - 10:40'),
    ('Вт', 4, 'Физика', '10:50 - 11:35'), ('Вт', 5, 'Алгебра', '12:00 - 12:45'),
    ('Вт', 6, 'Алгебра', '12:55 - 13:40'), ('Вт', 7, 'История Украины', '13:50 - 14:35'),
    ('Вт', 8, 'Английский язык', '14:40 - 15:25'), ('Ср', 1, 'Алгебра', '08:10 - 08:55'),
    ('Ср', 2, 'Химия', '09:00 - 09:45'), ('Ср', 3, 'Украинская литература', '09:55 - 10:40'),
    ('Ср', 4, 'Украинский язык', '10:50 - 11:35'), ('Ср', 5, 'Зарубежная литература', '12:00 - 12:45'),
    ('Ср', 6, 'Английский язык', '12:55 - 13:40'), ('Ср', 7, 'Английский язык', '13:50 - 14:35'),
    ('Ср', 8, 'Физика', '14:40 - 15:25'), ('Чт', 1, 'Классный час', '08:10 - 08:55'),
    ('Чт', 2, 'Биология', '09:00 - 09:45'), ('Чт', 3, 'Физкультура', '09:55 - 10:40'),
    ('Чт', 4, 'Химия', '10:50 - 11:35'), ('Чт', 5, 'Геометрия', '12:00 - 12:45'),
    ('Чт', 6, 'География', '12:55 - 13:40'), ('Чт', 7, 'Информатика', '13:50 - 14:35'),
    ('Пт', 1, 'Основы здоровья', '08:10 - 08:55'), ('Пт', 2, 'Всемирная история', '09:00 - 09:45'),
    ('Пт', 3, 'Технологии', '09:55 - 10:40'), ('Пт', 4, 'Французский язык', '10:50 - 11:35'),
    ('Пт', 5, 'Правоведение', '12:00 - 12:45'), ('Пт', 6, 'Информатика', '12:55 - 13:40'),
    ('Пт', 7, 'Биология', '13:50 - 14:35'), ('Пт', 8, 'Физкультура', '14:40 - 15:25'),
]
DAYS_ORDER = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт']

def get_db_connection():
    conn = psycopg2.connect(DB_URL)
    return conn

def init_and_populate_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS schedule, homework;")
    cursor.execute('''
    CREATE TABLE schedule (
        id SERIAL PRIMARY KEY, day_of_week TEXT NOT NULL, lesson_number INTEGER NOT NULL,
        subject_name TEXT NOT NULL, lesson_time TEXT );''')
    cursor.execute('''
    CREATE TABLE homework (
        id SERIAL PRIMARY KEY, subject_name TEXT NOT NULL, due_date DATE NOT NULL,
        task TEXT NOT NULL, is_completed BOOLEAN DEFAULT FALSE );''')
    
    insert_query = "INSERT INTO schedule (day_of_week, lesson_number, subject_name, lesson_time) VALUES (%s, %s, %s, %s)"
    psycopg2.extras.execute_batch(cursor, insert_query, HARDCODED_SCHEDULE)
    
    conn.commit()
    cursor.close()
    conn.close()

def add_homework(subject, due_date, task):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO homework (subject_name, due_date, task) VALUES (%s, %s, %s)",
        (subject, due_date, task)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_next_lesson_date(subject, from_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    start_day_index = from_date.weekday()
    ordered_days_of_week = DAYS_ORDER[start_day_index:] + DAYS_ORDER[:start_day_index]
    
    for day_offset, day_name_ukr in enumerate(ordered_days_of_week):
        cursor.execute("SELECT COUNT(*) FROM schedule WHERE day_of_week = %s AND subject_name = %s", (day_name_ukr, subject))
        if cursor.fetchone()[0] > 0:
            # Важно: смещение для сегодняшнего дня 0, если сегодня есть урок.
            # Если сегодня уроков нет, а есть завтра, смещение 1.
            # Но если сегодня пн, а урок во вт, то смещение = 1.
            # Если сегодня пт, а урок в пн, то смещение = 3.
            # Логика timedelta правильная.
            next_date = from_date + timedelta(days=day_offset)
            conn.close()
            return next_date.strftime("%Y-%m-%d")
            
    conn.close()
    return None