"""
Telegram Bot - Пересылка сообщений в канал

Основной файл бота, который:
- Настраивает webhook для получения обновлений от Telegram
- Обрабатывает входящие сообщения
- Пересылает сообщения пользователей в указанный канал
- Запускает HTTP-сервер для webhook
- Использует CSV для хранения данных о сообщениях

Автор: Николай Почернин/Коля П
Версия: 2.1 (с CSV хранилищем)
"""

import asyncio
import logging
import os
from typing import Union
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv
from message_handler import MessageHandler
from csv_storage import CSVMessageStore

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем обязательные переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")        # Токен бота от @BotFather
WEBHOOK_URL = os.getenv("WEBHOOK_URL")    # URL для webhook (должен быть HTTPS)
CHANNEL_ID = os.getenv("CHANNEL_ID")      # ID или username канала для пересылки
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "true").lower() == "true"  # Режим работы: webhook или long polling

# Проверяем, что все обязательные переменные установлены
if not all([BOT_TOKEN, CHANNEL_ID]):
    raise ValueError("Не все обязательные переменные окружения установлены (нужны BOT_TOKEN и CHANNEL_ID)")

# Для режима webhook обязателен WEBHOOK_URL
if USE_WEBHOOK and not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL обязателен при USE_WEBHOOK=true")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создаем CSV хранилище для сообщений
csv_storage = CSVMessageStore("message_mapping.csv")

# Создаем обработчик сообщений с CSV хранилищем
message_handler = MessageHandler(bot, CHANNEL_ID, csv_storage)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start
    
    Отправляет приветственное сообщение пользователю с инструкцией
    """
    await message.answer(
        "Привет! Я бот для пересылки сообщений. Ура!"
    )


@dp.message()
async def handle_message(message: Message):
    """
    Основной обработчик всех входящих сообщений
    
    Разделяет обработку по типу чата:
    - private: сообщения от пользователей -> пересылаем в канал
    - channel: ответы в канале -> пересылаем пользователям (с помощью CSV)
    - другие типы: игнорируем
    """
    try:
        if message.chat.type == "private":
            # Сообщение от пользователя - пересылаем в канал
            await message_handler.handle_user_message(message)
        elif message.chat.type == "channel":
            # Ответ в канале - пересылаем пользователю с помощью CSV
            await message_handler.handle_channel_reply(message)
        else:
            # Игнорируем сообщения из групп и супергрупп
            logger.info(f"Игнорируем сообщение из {message.chat.type}: {message.chat.id}")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        # Отправляем пользователю сообщение об ошибке только для приватных чатов
        if message.chat.type == "private":
            await message.answer("Произошла ошибка при обработке вашего сообщения.")


async def on_startup(app):
    """
    Функция, выполняемая при запуске приложения
    
    - Инициализирует CSV хранилище
    - Инициализирует webhook для получения обновлений от Telegram
    - Устанавливает URL для webhook
    """
    logger.info("Бот запускается...")
    
    # Инициализируем CSV хранилище
    await csv_storage.init()
    logger.info("CSV хранилище инициализировано")
    
    if USE_WEBHOOK:
        # Устанавливаем webhook для получения обновлений от Telegram
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True  # Игнорируем старые обновления
        )
        logger.info(f"Webhook установлен: {WEBHOOK_URL}")


async def on_shutdown(_):
    """
    Функция, выполняемая при остановке приложения
    
    - Закрывает CSV хранилище
    - Удаляет webhook
    - Закрывает сессию бота
    """
    logger.info("Бот останавливается...")
    
    # Закрываем CSV хранилище
    await csv_storage.close()
    logger.info("CSV хранилище закрыто")
    
    if USE_WEBHOOK:
        # Удаляем webhook
        await bot.delete_webhook()
    # Закрываем сессию бота
    await bot.session.close()


async def run_polling():
    """
    Запускает бота в режиме long polling без вебхука
    """
    logger.info("Запуск в режиме long polling...")
    await csv_storage.init()
    try:
        # На всякий случай удаляем вебхук, чтобы переключиться на polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await csv_storage.close()
        await bot.session.close()


def main():
    """
    Основная функция запуска бота
    
    Создает HTTP-сервер с webhook-обработчиком для Telegram API
    """
    if USE_WEBHOOK:
        # Создаем веб-приложение
        app = web.Application()
        
        # Создаем обработчик webhook для Telegram
        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        )
        # Регистрируем webhook на пути /webhook
        webhook_handler.register(app, path="/webhook")
        
        # Добавляем обработчики запуска и остановки
        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        # Запускаем HTTP-сервер
        web.run_app(
            app,
            host="0.0.0.0",  # Слушаем на всех интерфейсах
            port=8000         # Порт для webhook
        )
    else:
        asyncio.run(run_polling())


if __name__ == "__main__":
    main()
