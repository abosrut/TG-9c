# app/scheduler_logic.py
from datetime import date
from app import ocr_processor, data_parser, database_manager

def process_and_store_schedule(image_bytes):
    raw_text = ocr_processor.extract_text_from_image(image_bytes)
    if not raw_text:
        return False, "Не удалось распознать текст на изображении."
    
    schedule_data = data_parser.parse_schedule(raw_text)
    if not schedule_data:
        return False, "Не удалось проанализировать расписание. Проверьте формат текста."
        
    database_manager.add_schedule_data(schedule_data)
    return True, f"Расписание успешно обновлено. Добавлено {len(schedule_data)} уроков."

def process_and_store_homework(image_bytes):
    raw_text = ocr_processor.extract_text_from_image(image_bytes)
    if not raw_text:
        return False, "Не удалось распознать текст домашнего задания."
        
    homework_data = data_parser.parse_homework(raw_text)
    if not homework_data:
        return False, "Не удалось найти домашние задания на изображении."
    
    today = date.today()
    for subject, task in homework_data.items():
        due_date = database_manager.get_next_lesson_date(subject, today)
        database_manager.add_homework(subject, due_date, task)
        
    return True, f"Домашнее задание добавлено для {len(homework_data)} предметов."