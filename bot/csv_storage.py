"""
CSVMessageStore - Хранилище сообщений в формате CSV (сделал сам)

Этот класс отвечает за:
- Сохранение маппинга сообщений пользователей и канала
- Поиск пользователей по ID сообщения в канале
- Асинхронную работу с CSV файлами
- Автоматическое создание файла при инициализации

Автор: Николай Почернин/Коля П
Версия: 1.0
"""

import csv
import logging
import os
import asyncio
from typing import Optional, List, Dict
from datetime import datetime
from logging_config import setup_logging

# Инициализируем логирование
logger = setup_logging("csv_storage", "csv_storage.log", 5*1024*1024)  # 5MB


class CSVMessageStore:
    """
    Класс для хранения маппинга сообщений в CSV формате
    
    Структура CSV файла:
    user_id,user_message_id,channel_message_id,created_at,user_name
    
    Позволяет отслеживать, какое сообщение пользователя
    соответствует какому сообщению в канале.
    """
    
    def __init__(self, filename: str):
        """
        Инициализация CSV хранилища
        
        Args:
            filename: Путь к CSV файлу для хранения данных
        """
        self.filename = filename
        self._lock = asyncio.Lock()  # Блокировка для безопасной записи
        
        # Заголовки CSV файла
        self.headers = [
            'user_id',
            'user_message_id', 
            'channel_message_id',
            'created_at',
            'user_name'
        ]
    
    async def init(self):
        """
        Инициализация хранилища
        
        Создает CSV файл с заголовками, если он не существует
        """
        try:
            # Создаем директорию для файла, если она не существует
            directory = os.path.dirname(self.filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Создана директория: {directory}")
            
            # Проверяем, существует ли файл
            if not os.path.exists(self.filename):
                await self._create_csv_file()
                logger.info(f"Создан новый CSV файл: {self.filename}")
            else:
                logger.info(f"CSV файл уже существует: {self.filename}")
                
        except Exception as e:
            logger.error(f"Ошибка при инициализации CSV хранилища: {e}")
            logger.error(f"Попытка создания файла: {self.filename}")
            logger.error(f"Текущая рабочая директория: {os.getcwd()}")
            logger.error(f"Права доступа к директории: {os.access(os.path.dirname(self.filename), os.W_OK) if os.path.dirname(self.filename) else 'N/A'}")
            raise
    
    async def _create_csv_file(self):
        """
        Создает новый CSV файл с заголовками
        
        Использует блокировку для безопасной записи
        """
        async with self._lock:
            try:
                with open(self.filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=self.headers)
                    writer.writeheader()
                logger.info(f"CSV файл создан с заголовками: {self.filename}")
            except Exception as e:
                logger.error(f"Ошибка при создании CSV файла: {e}")
                raise
    
    async def save_message_mapping(
        self, 
        user_id: int, 
        user_message_id: int, 
        channel_message_id: int,
        user_name: str = None
    ) -> bool:
        """
        Сохраняет маппинг сообщения пользователя и сообщения в канале
        
        Args:
            user_id: ID пользователя
            user_message_id: ID сообщения пользователя
            channel_message_id: ID сообщения в канале
            user_name: Имя пользователя (опционально)
            
        Returns:
            bool: True если сохранение успешно, False в случае ошибки
        """
        try:
            async with self._lock:
                # Подготавливаем данные для записи
                row_data = {
                    'user_id': user_id,
                    'user_message_id': user_message_id,
                    'channel_message_id': channel_message_id,
                    'created_at': datetime.now().isoformat(),
                    'user_name': user_name or f"user_{user_id}"
                }
                
                # Записываем в CSV файл
                with open(self.filename, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=self.headers)
                    writer.writerow(row_data)
                
                logger.info(f"Маппинг сохранен: user_id={user_id}, channel_message_id={channel_message_id}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка сохранения маппинга: {e}")
            return False
    
    async def get_user_by_channel_message(self, channel_message_id: int) -> Optional[int]:
        """
        Получает ID пользователя по ID сообщения в канале
        
        Args:
            channel_message_id: ID сообщения в канале
            
        Returns:
            Optional[int]: ID пользователя или None, если не найден
        """
        try:
            async with self._lock:
                logger.info(f"Ищем пользователя для channel_message_id: {channel_message_id}")
                
                with open(self.filename, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    # Ищем точное совпадение по channel_message_id
                    for row in reader:
                        if int(row['channel_message_id']) == channel_message_id:
                            user_id = int(row['user_id'])
                            logger.info(f"Найден пользователь: {user_id} для сообщения {channel_message_id}")
                            return user_id
                    
                    logger.warning(f"Пользователь для сообщения {channel_message_id} не найден")
                    return None
                    
        except Exception as e:
            logger.error(f"Ошибка получения пользователя: {e}")
            return None
    
    async def get_user_message_id(self, user_id: int, channel_message_id: int) -> Optional[int]:
        """
        Получает ID сообщения пользователя по ID сообщения в канале
        
        Args:
            user_id: ID пользователя
            channel_message_id: ID сообщения в канале
            
        Returns:
            Optional[int]: ID сообщения пользователя или None, если не найден
        """
        try:
            async with self._lock:
                with open(self.filename, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    for row in reader:
                        if (int(row['user_id']) == user_id and 
                            int(row['channel_message_id']) == channel_message_id):
                            return int(row['user_message_id'])
                    
                    return None
                    
        except Exception as e:
            logger.error(f"Ошибка получения user_message_id: {e}")
            return None
    
    async def get_all_mappings(self) -> List[Dict]:
        """
        Получает все маппинги сообщений
        
        Returns:
            List[Dict]: Список всех маппингов
        """
        try:
            async with self._lock:
                mappings = []
                with open(self.filename, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        mappings.append(row)
                
                return mappings
                
        except Exception as e:
            logger.error(f"Ошибка получения всех маппингов: {e}")
            return []
    
    async def close(self):
        """
        Закрывает хранилище
        
        В CSV хранилище нет активных соединений, поэтому просто логируем
        """
        logger.info("CSV хранилище закрыто")
    
    def get_file_size(self) -> int:
        """
        Получает размер CSV файла в байтах
        
        Returns:
            int: Размер файла в байтах
        """
        try:
            if os.path.exists(self.filename):
                return os.path.getsize(self.filename)
            return 0
        except Exception:
            return 0
    
    def get_mappings_count(self) -> int:
        """
        Получает количество записей в CSV файле
        
        Returns:
            int: Количество записей (без учета заголовка)
        """
        try:
            if not os.path.exists(self.filename):
                return 0
            
            with open(self.filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                return sum(1 for _ in reader)
                
        except Exception:
            return 0
    
    async def check_file_accessibility(self) -> bool:
        """
        Проверяет доступность файла для чтения и записи
        
        Returns:
            bool: True если файл доступен, False в противном случае
        """
        try:
            directory = os.path.dirname(self.filename)
            
            # Проверяем права на директорию
            if directory and not os.access(directory, os.W_OK):
                logger.error(f"Нет прав на запись в директорию: {directory}")
                return False
            
            # Проверяем права на файл (если существует)
            if os.path.exists(self.filename):
                if not os.access(self.filename, os.R_OK):
                    logger.error(f"Нет прав на чтение файла: {self.filename}")
                    return False
                if not os.access(self.filename, os.W_OK):
                    logger.error(f"Нет прав на запись в файл: {self.filename}")
                    return False
            
            logger.info(f"Файл {self.filename} доступен для чтения и записи")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при проверке доступности файла: {e}")
            return False

    def debug_print_mappings(self):
        """
        Выводит отладочную информацию о содержимом CSV файла
        """
        try:
            logger.info(f"=== Отладка CSV хранилища ===")
            logger.info(f"Файл: {self.filename}")
            logger.info(f"Файл существует: {os.path.exists(self.filename)}")
            logger.info(f"Абсолютный путь: {os.path.abspath(self.filename)}")
            logger.info(f"Текущая рабочая директория: {os.getcwd()}")
            
            if os.path.exists(self.filename):
                file_size = os.path.getsize(self.filename)
                logger.info(f"Размер файла: {file_size} байт")
                
                if file_size > 0:
                    try:
                        with open(self.filename, 'r', encoding='utf-8') as csvfile:
                            content = csvfile.read()
                            logger.info(f"Содержимое файла:\n{content}")
                    except Exception as e:
                        logger.error(f"Ошибка при чтении файла: {e}")
                else:
                    logger.info("Файл пустой")
            else:
                logger.warning("Файл не существует")
                
            logger.info(f"===============================")
            
        except Exception as e:
            logger.error(f"Ошибка при отладке CSV хранилища: {e}")
