import sqlite3
import sys

DB_NAME = 'schedule.db'

def test_search(search_term):
    print(f"--- Тестируем поиск для: '{search_term}' ---")
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        search_query = f'{search_term}%'
        
        # Выполняем тот самый проблемный запрос
        cursor.execute("SELECT subject_name FROM schedule WHERE subject_name LIKE ? COLLATE NOCASE", (search_query,))
        
        results = cursor.fetchall()
        
        if results:
            print("Найдены следующие предметы:")
            for row in results:
                print(f"- {row[0]}")
        else:
            print("Ничего не найдено.")
            
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        if conn:
            conn.close()
        print("-" * 20 + "\n")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        term = sys.argv[1]
        test_search(term)
    else:
        print("Ошибка: Укажите предмет для поиска после имени файла.")
        print("Пример: python debug_search.py Алгебра")