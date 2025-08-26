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

logger = logging.getLogger(__name__)


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
            # Проверяем, существует ли файл
            if not os.path.exists(self.filename):
                await self._create_csv_file()
                logger.info(f"Создан новый CSV файл: {self.filename}")
            else:
                logger.info(f"CSV файл уже существует: {self.filename}")
                
        except Exception as e:
            logger.error(f"Ошибка при инициализации CSV хранилища: {e}")
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
    
    def debug_print_mappings(self):
        """
        Отладочный метод для вывода содержимого CSV файла
        """
        try:
            if not os.path.exists(self.filename):
                logger.info("CSV файл не существует")
                return
            
            logger.info(f"Содержимое CSV файла {self.filename}:")
            with open(self.filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for i, row in enumerate(reader, 1):
                    logger.info(f"  {i}: {row}")
                    
        except Exception as e:
            logger.error(f"Ошибка при чтении CSV файла для отладки: {e}")
