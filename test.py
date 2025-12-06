import sqlite3
import pandas as pd
import json

DB_NAME = 'universities.db'
EXCEL_FILE = 'university_data.xlsx'

def init_and_load_db():
    """Инициализация БД и загрузка данных из Excel"""
    
    # Создаём подключение
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Создаём таблицу
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS universities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            specialties TEXT,
            website TEXT,
            contacts TEXT,
            address TEXT,
            chatgpt_data TEXT
        )
    ''')
    
    # Очищаем таблицу
    cursor.execute('DELETE FROM universities')
    
    # Читаем данные из Excel
    try:
        df = pd.read_excel(EXCEL_FILE)
        print(f"Загружено {len(df)} записей из {EXCEL_FILE}")
        
        for idx, row in df.iterrows():
            # Извлекаем название из paragraph_text или используем page_url
            name = "Университет"
            description = str(row.get('paragraph_text', ''))
            
            # Пытаемся извлечь название из первых строк описания
            if description and len(description) > 10:
                first_lines = description.split('\n')[:3]
                for line in first_lines:
                    if len(line) > 5 and len(line) < 150:
                        name = line.strip()
                        break
            
            specialties = str(row.get('specialities', ''))
            website = str(row.get('websites', ''))
            contacts = str(row.get('contacts', ''))
            address = str(row.get('address', ''))
            
            # Создаём базовый chatgpt_data
            chatgpt_data = json.dumps({
                'academic_programs': 'Информация о программах уточняется. Посетите официальный сайт университета.',
                'admission_info': 'Для получения информации о поступлении обращайтесь в приемную комиссию.',
                'international_cooperation': 'Информация о международном сотрудничестве уточняется.',
                'general_info': 'Для получения актуальной информации посетите официальный сайт университета.'
            }, ensure_ascii=False)
            
            cursor.execute('''
                INSERT INTO universities (name, description, specialties, website, contacts, address, chatgpt_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, specialties, website, contacts, address, chatgpt_data))
            
            print(f"Добавлен: {name}")
        
        conn.commit()
        print(f"\nУспешно загружено {len(df)} университетов в базу данных!")
        
    except FileNotFoundError:
        print(f"ОШИБКА: Файл {EXCEL_FILE} не найден!")
        print("Убедитесь, что файл university_data.xlsx находится в той же папке.")
    except Exception as e:
        print(f"ОШИБКА при загрузке данных: {e}")
    
    conn.close()

if __name__ == '__main__':
    print("Инициализация базы данных...")
    init_and_load_db()
    print("\nГотово! Теперь можно запускать app.py")