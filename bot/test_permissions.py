#!/usr/bin/env python3
"""
Тестовый скрипт для проверки прав доступа к директории logs
"""

import os
import stat

def test_logs_directory():
    """Тестирует доступ к директории logs"""
    print("Тестирование прав доступа к директории logs...")
    
    # Проверяем текущую рабочую директорию
    print(f"Текущая рабочая директория: {os.getcwd()}")
    
    # Проверяем содержимое текущей директории
    print(f"Содержимое текущей директории: {os.listdir('.')}")
    
    # Проверяем директорию logs
    logs_dir = "logs"
    
    if os.path.exists(logs_dir):
        print(f"Директория {logs_dir} существует")
        
        # Проверяем права доступа
        st = os.stat(logs_dir)
        print(f"Права доступа: {oct(st.st_mode)}")
        print(f"Владелец: {st.st_uid}")
        print(f"Группа: {st.st_gid}")
        
        # Проверяем, можем ли мы писать в директорию
        test_file = os.path.join(logs_dir, "test.txt")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            print("✓ Можем писать в директорию logs")
            os.remove(test_file)
            print("✓ Можем удалять файлы из директории logs")
        except Exception as e:
            print(f"✗ Ошибка при записи в директорию logs: {e}")
    else:
        print(f"Директория {logs_dir} не существует")
        
        # Пытаемся создать директорию
        try:
            os.makedirs(logs_dir, exist_ok=True)
            print(f"✓ Директория {logs_dir} создана успешно")
        except Exception as e:
            print(f"✗ Ошибка при создании директории {logs_dir}: {e}")

if __name__ == "__main__":
    test_logs_directory()
