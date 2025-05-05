import sqlite3

def check_database(db_name):
    try:
        # Подключаемся к базе данных
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        
        # Выполняем простой запрос для проверки
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if tables:
            print("База данных подключена успешно. Существующие таблицы:")
            for table in tables:
                print(table[0])
        else:
            print("База данных подключена успешно, но таблицы не найдены.")
        
    except sqlite3.Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")
    finally:
        if connection:
            connection.close()

# Замените 'idioms.db' на имя вашей базы данных
check_database('idioms.db')