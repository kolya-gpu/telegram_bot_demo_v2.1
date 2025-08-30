#!/usr/bin/env python3
"""
Тестовый скрипт для проверки доступа к CSV файлу
"""

import os
import sys
from csv_storage import CSVMessageStore
from logging_config import setup_logging

def test_csv_access():
    """Тестирует доступ к CSV файлу"""
    logger = setup_logging("test_csv", "test_csv.log", 1024*1024)
    
    # Тестируем разные пути
    test_paths = [
        "logs/message_mapping.csv",
        "/app/logs/message_mapping.csv",
        os.path.join(os.getcwd(), "logs", "message_mapping.csv")
    ]
    
    logger.info("=== Тест доступа к CSV файлу ===")
    logger.info(f"Текущая рабочая директория: {os.getcwd()}")
    
    for path in test_paths:
        logger.info(f"\nТестируем путь: {path}")
        logger.info(f"Абсолютный путь: {os.path.abspath(path)}")
        
        # Проверяем существование
        exists = os.path.exists(path)
        logger.info(f"Файл существует: {exists}")
        
        if exists:
            # Проверяем размер
            size = os.path.getsize(path)
            logger.info(f"Размер файла: {size} байт")
            
            # Проверяем права доступа
            readable = os.access(path, os.R_OK)
            writable = os.access(path, os.W_OK)
            logger.info(f"Читаемый: {readable}, Записываемый: {writable}")
            
            # Пробуем прочитать
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logger.info(f"Содержимое (первые 200 символов): {content[:200]}")
            except Exception as e:
                logger.error(f"Ошибка чтения: {e}")
        else:
            # Проверяем директорию
            dir_path = os.path.dirname(path)
            if dir_path:
                dir_exists = os.path.exists(dir_path)
                dir_writable = os.access(dir_path, os.W_OK) if dir_exists else False
                logger.info(f"Директория существует: {dir_exists}, Записываемая: {dir_writable}")
        
        # Пробуем создать CSV хранилище
        try:
            csv_store = CSVMessageStore(path)
            logger.info("CSV хранилище создано успешно")
            
            # Пробуем инициализировать
            import asyncio
            async def test_init():
                try:
                    await csv_store.init()
                    logger.info("CSV хранилище инициализировано успешно")
                    return True
                except Exception as e:
                    logger.error(f"Ошибка инициализации: {e}")
                    return False
            
            success = asyncio.run(test_init())
            logger.info(f"Инициализация: {'успешно' if success else 'ошибка'}")
            
        except Exception as e:
            logger.error(f"Ошибка создания CSV хранилища: {e}")
    
    logger.info("\n=== Тест завершен ===")

if __name__ == "__main__":
    test_csv_access()
