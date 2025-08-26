"""
MessageHandler - Обработчик сообщений для Telegram бота

Этот класс отвечает за:
- Пересылку сообщений от пользователей в канал
- Обработку различных типов контента (текст, фото, видео, документы, аудио, голосовые)
- Сохранение маппинга сообщений в CSV для пересылки ответов пользователям

Автор: Николай Почернин/Коля П
Версия: 2.1 (с CSV хранилищем)
"""

import logging
from typing import Union
from aiogram import Bot
from aiogram.types import Message, ContentType
from logging_config import setup_logging

# Инициализируем логирование
logger = setup_logging("message_handler", "message_handler.log", 5*1024*1024)  # 5MB


class MessageHandler:
    """
    Класс для обработки сообщений Telegram бота
    
    Обрабатывает входящие сообщения от пользователей и пересылает их в указанный канал.
    Поддерживает все основные типы контента Telegram.
    Использует CSV хранилище для отслеживания соответствий сообщений.
    """
    
    def __init__(self, bot: Bot, channel_id: str, storage):
        """
        Инициализация обработчика сообщений
        
        Args:
            bot: Экземпляр бота для отправки сообщений
            channel_id: ID или username канала для пересылки сообщений
            storage: Хранилище для маппинга сообщений (CSV)
        """
        self.bot = bot
        self.channel_id = channel_id
        self.storage = storage
    
    async def handle_user_message(self, message: Message):
        """
        Обработка сообщения от пользователя
        
        Пересылает сообщение в канал, сохраняет маппинг и отправляет пользователю подтверждение.
        Поддерживает все типы контента: текст, фото, видео, документы, аудио, голосовые.
        
        Args:
            message: Сообщение от пользователя
        """
        try:
            # Пересылаем сообщение в канал
            channel_message = await self._forward_to_channel(message)
            
            if channel_message:
                # Сохраняем маппинг сообщения
                await self.storage.save_message_mapping(
                    user_id=message.from_user.id,
                    user_message_id=message.message_id,
                    channel_message_id=channel_message.message_id,
                    user_name=message.from_user.first_name
                )
                
                # Сообщение успешно переслано
                await message.answer("Ваше сообщение отправлено в канал!")
                logger.info(f"Сообщение от пользователя {message.from_user.id} переслано в канал")
            else:
                # Ошибка при пересылке
                await message.answer("Не удалось отправить сообщение в канал")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения пользователя: {e}")
            await message.answer("Произошла ошибка при обработке вашего сообщения")
    
    async def _forward_to_channel(self, message: Message) -> Union[Message, None]:
        """
        Пересылка сообщения в канал
        
        Обрабатывает различные типы контента и пересылает их в канал с пометкой
        от какого пользователя пришло сообщение.
        
        Args:
            message: Сообщение для пересылки
            
        Returns:
            Message: Объект сообщения в канале или None при ошибке
        """
        try:
            content_type = message.content_type
            
            # Обработка текстовых сообщений
            if content_type == ContentType.TEXT:
                return await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=f"Сообщение от пользователя {message.from_user.first_name}:\n\n{message.text}"
                )
            
            # Обработка фотографий
            elif content_type == ContentType.PHOTO:
                caption = f"Фото от пользователя {message.from_user.first_name}"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                
                return await self.bot.send_photo(
                    chat_id=self.channel_id,
                    photo=message.photo[-1].file_id,  # Берем фото с максимальным разрешением
                    caption=caption
                )
            
            # Обработка видео
            elif content_type == ContentType.VIDEO:
                caption = f"Видео от пользователя {message.from_user.first_name}"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                
                return await self.bot.send_video(
                    chat_id=self.channel_id,
                    video=message.video.file_id,
                    caption=caption
                )
            
            # Обработка документов
            elif content_type == ContentType.DOCUMENT:
                caption = f"Документ от пользователя {message.from_user.first_name}"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                
                return await self.bot.send_document(
                    chat_id=self.channel_id,
                    document=message.document.file_id,
                    caption=caption
                )
            
            # Обработка голосовых сообщений
            elif content_type == ContentType.VOICE:
                return await self.bot.send_voice(
                    chat_id=self.channel_id,
                    voice=message.voice.file_id,
                    caption=f"Голосовое сообщение от пользователя {message.from_user.first_name}"
                )
            
            # Обработка аудио файлов
            elif content_type == ContentType.AUDIO:
                caption = f"Аудио от пользователя {message.from_user.first_name}"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                
                return await self.bot.send_audio(
                    chat_id=self.channel_id,
                    audio=message.audio.file_id,
                    caption=caption
                )
            
            # Обработка неподдерживаемых типов контента
            else:
                return await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=f"Неподдерживаемый тип контента от пользователя {message.from_user.first_name}"
                )
                
        except Exception as e:
            logger.error(f"Ошибка при пересылке в канал: {e}")
            return None
    
    async def handle_channel_reply(self, message: Message):
        """
        Обработка ответа в канале
        
        Определяет, какому пользователю принадлежит исходное сообщение,
        и пересылает ответ из канала этому пользователю.
        
        Args:
            message: Ответ в канале
        """
        try:
            if not message.reply_to_message:
                # Если это не ответ на другое сообщение, игнорируем
                return
            
            replied_message_id = message.reply_to_message.message_id
            
            # Получаем информацию о пользователе из CSV хранилища
            user_id = await self.storage.get_user_by_channel_message(replied_message_id)
            
            if not user_id:
                logger.warning(f"Не найден пользователь для сообщения {replied_message_id}")
                return
            
            # Пересылаем ответ пользователю
            await self._forward_reply_to_user(message, user_id)
            
            logger.info(f"Ответ из канала переслан пользователю {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при обработке ответа из канала: {e}")
    
    async def _forward_reply_to_user(self, message: Message, user_id: int):
        """
        Пересылка ответа из канала пользователю
        
        Обрабатывает различные типы контента и пересылает их пользователю
        с пометкой, что это ответ из канала.
        
        Args:
            message: Ответ из канала
            user_id: ID пользователя для пересылки
        """
        try:
            logger.info(f"Пересылаем ответ пользователю {user_id}, тип контента: {message.content_type}")
            content_type = message.content_type
            
            if content_type == ContentType.TEXT:
                await self.bot.send_message(
                    chat_id=user_id,
                    text=f"Ответ из канала:\n\n{message.text}"
                )
                logger.info(f"Текстовый ответ отправлен пользователю {user_id}")
            
            elif content_type == ContentType.PHOTO:
                caption = "Ответ из канала"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                
                await self.bot.send_photo(
                    chat_id=user_id,
                    photo=message.photo[-1].file_id,
                    caption=caption
                )
                logger.info(f"Фото ответ отправлено пользователю {user_id}")
            
            elif content_type == ContentType.VIDEO:
                caption = "Ответ из канала"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                
                await self.bot.send_video(
                    chat_id=user_id,
                    video=message.video.file_id,
                    caption=caption
                )
                logger.info(f"Видео ответ отправлено пользователю {user_id}")
            
            elif content_type == ContentType.DOCUMENT:
                caption = "Ответ из канала"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                
                await self.bot.send_document(
                    chat_id=user_id,
                    document=message.document.file_id,
                    caption=caption
                )
                logger.info(f"Документ ответ отправлен пользователю {user_id}")
            
            elif content_type == ContentType.VOICE:
                await self.bot.send_voice(
                    chat_id=user_id,
                    voice=message.voice.file_id,
                    caption="Ответ из канала"
                )
                logger.info(f"Голосовой ответ отправлен пользователю {user_id}")
            
            elif content_type == ContentType.AUDIO:
                caption = "Ответ из канала"
                if message.caption:
                    caption += f"\n\n{message.caption}"
                
                await self.bot.send_audio(
                    chat_id=user_id,
                    audio=message.audio.file_id,
                    caption=caption
                )
                logger.info(f"Аудио ответ отправлен пользователю {user_id}")
            
            else:
                await self.bot.send_message(
                    chat_id=user_id,
                    text="Получен ответ из канала (неподдерживаемый тип контента)"
                )
                logger.info(f"Ответ с неподдерживаемым типом контента отправлен пользователю {user_id}")
                
        except Exception as e:
            logger.error(f"Ошибка при пересылке ответа пользователю {user_id}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
