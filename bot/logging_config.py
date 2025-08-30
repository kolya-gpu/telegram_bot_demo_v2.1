#!/usr/bin/env python3
"""
Конфигурация логирования для Telegram бота

Централизованные настройки логирования для всех модулей бота
"""

import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(module_name: str, log_filename: str = None, max_bytes: int = 5*1024*1024):
    """
    Настройка логирования для модуля
    
    Args:
        module_name: Имя модуля для логгера
        log_filename: Имя файла логов (если None, используется module_name.log)
        max_bytes: Максимальный размер файла логов в байтах
    """
    # Создаем директорию для логов, если её нет
    # Используем относительный путь для Docker контейнера
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Путь к файлу логов
    if log_filename is None:
        log_filename = f"{module_name}.log"
    
    log_file = os.path.join(log_dir, log_filename)
    
    # Настраиваем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Настраиваем файловый обработчик с ротацией
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Создаем логгер для модуля
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)
    
    # Убираем существующие обработчики, чтобы избежать дублирования
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    logger.addHandler(file_handler)
    
    # Добавляем консольный обработчик для отладки
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(module_name: str):
    """
    Получает настроенный логгер для модуля
    
    Args:
        module_name: Имя модуля
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    return logging.getLogger(module_name)
