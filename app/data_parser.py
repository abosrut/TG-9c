# app/data_parser.py
import re

SUBJECT_TRANSLATIONS = {
    "Мист": "Искусство",
    "Англ.м": "Английский язык",
    "Укр.м": "Украинский язык",
    "Укр.л": "Украинская литература",
    "Фіз": "Физика",
    "Фіз.к-ра": "Физкультура",
    "Алгебра": "Алгебра",
    "Хім": "Химия",
    "Зар.літ": "Зарубежная литература",
    "Іст. Укр": "История Украины",
    "Геометрія": "Геометрия",
    "Кл. година": "Классный час",
    "Біол": "Биология",
    "Геогр": "География",
    "Осн.здор": "Основы здоровья",
    "Вс. іст": "Всемирная история",
    "Технології": "Технологии",
    "Франц. м": "Французский язык",
    "Право": "Правоведение",
    "Інф": "Информатика"
}

DAYS_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт"]

def parse_schedule(raw_text):
    lines = raw_text.split('\n')
    schedule_data = []
    
    current_day = None
    lesson_number = 0

    for i, line in enumerate(lines):
        cleaned_line = line.strip()

        # Ищем дни недели в строке
        found_days = [day for day in DAYS_SHORT if day in cleaned_line]
        if found_days:
            # Предполагаем, что дни идут по порядку, и берем первый найденный
            current_day = found_days[0]

        # Ищем номер урока - строка, состоящая только из одной цифры
        if re.fullmatch(r'\d', cleaned_line):
            lesson_number = int(cleaned_line)
            
            # После номера урока, следующие несколько строк могут содержать время и предмет
            # Мы ищем предмет в следующих 3 строках
            if lesson_number > 0:
                search_area = lines[i+1:i+4]
                found_subject = False
                for j, sub_line in enumerate(search_area):
                    for ukr_subject, rus_subject in SUBJECT_TRANSLATIONS.items():
                        # Ищем точное совпадение, чтобы не путать "Фіз" и "Фіз.к-ра"
                        if re.search(r'\b' + re.escape(ukr_subject) + r'\b', sub_line):
                            
                            time_str = "N/A"
                            # Попробуем найти время в строке перед предметом
                            if j > 0:
                                time_match = re.search(r'\d{2}:\d{2}\s*-\s*\d{2}:\d{2}', search_area[j-1])
                                if time_match:
                                    time_str = time_match.group(0)

                            schedule_data.append((current_day, lesson_number, rus_subject, time_str))
                            found_subject = True
                            break
                    if found_subject:
                        break
    
    # Удаляем дубликаты, которые могли возникнуть из-за несовершенства OCR
    unique_schedule = sorted(list(set(schedule_data)))
    return unique_schedule


def parse_homework(raw_text):
    # Эта функция остается без изменений, но ее тоже нужно будет адаптировать
    # когда у вас будет пример фото доски с домашним заданием
    homework_dict = {}
    for line in raw_text.split('\n'):
        if '-' in line or ':' in line:
            delimiter = '-' if '-' in line else ':'
            parts = line.split(delimiter, 1)
            if len(parts) == 2:
                subject = parts[0].strip()
                task = parts[1].strip()
                if subject and task:
                    homework_dict[subject] = task
    return homework_dict