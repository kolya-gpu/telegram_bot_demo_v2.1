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
from logging_config import setup_logging
import socket

# Загружаем переменные окружения из .env файла
load_dotenv()

# Инициализируем логирование
logger = setup_logging("main", "bot.log", 10*1024*1024)  # 10MB для основного лога

def is_port_available(host: str, port: int) -> bool:
    """
    Проверяет, доступен ли порт для привязки
    
    Args:
        host: Хост для проверки
        port: Порт для проверки
        
    Returns:
        bool: True если порт доступен, False в противном случае
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False

# Получаем обязательные переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")        # Токен бота от @BotFather
WEBHOOK_URL = os.getenv("WEBHOOK_URL")    # URL для webhook (должен быть HTTPS)
CHANNEL_ID = os.getenv("CHANNEL_ID")      # ID или username канала для пересылки
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "true").lower() == "true"  # Режим работы: webhook или long polling

# Настройки webhook сервера
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "127.0.0.1")  # Хост для webhook (по умолчанию localhost)
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8000"))   # Порт для webhook (по умолчанию 8000)

# Проверяем, что все обязательные переменные установлены
if not all([BOT_TOKEN, CHANNEL_ID]):
    raise ValueError("Не все обязательные переменные окружения установлены (нужны BOT_TOKEN и CHANNEL_ID)")

# Для режима webhook обязателен WEBHOOK_URL
if USE_WEBHOOK and not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL обязателен при USE_WEBHOOK=true")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создаем CSV хранилище для сообщений (используем директорию logs)
# Используем переменную окружения или fallback на относительный путь
csv_file_path = os.getenv("CSV_FILE_PATH", "logs/message_mapping.csv")
# Если путь не абсолютный, делаем его абсолютным относительно рабочей директории
if not os.path.isabs(csv_file_path):
    csv_file_path = os.path.join(os.getcwd(), csv_file_path)

# Создаем директорию для логов, если она не существует
os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

logger.info(f"Используем CSV файл: {csv_file_path}")
logger.info(f"Текущая рабочая директория: {os.getcwd()}")
logger.info(f"Абсолютный путь к CSV: {os.path.abspath(csv_file_path)}")

csv_storage = CSVMessageStore(csv_file_path)

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
    
    # Проверяем доступность файла перед инициализацией
    if not await csv_storage.check_file_accessibility():
        logger.error("Файл CSV недоступен! Проверьте права доступа и путь к файлу.")
        logger.error(f"Попытка использования файла: {csv_storage.filename}")
        return
    
    # Инициализируем CSV хранилище
    await csv_storage.init()
    logger.info("CSV хранилище инициализировано")
    
    # Отладочная информация о содержимом CSV
    csv_storage.debug_print_mappings()
    
    if USE_WEBHOOK:
        # Проверяем webhook URL
        if not WEBHOOK_URL:
            logger.error("WEBHOOK_URL не установлен!")
            return
        
        logger.info(f"Устанавливаем webhook на URL: {WEBHOOK_URL}")
        
        # Устанавливаем webhook для получения обновлений от Telegram
        try:
            await bot.set_webhook(
                url=WEBHOOK_URL,
                drop_pending_updates=True  # Игнорируем старые обновления
            )
            logger.info(f"Webhook успешно установлен: {WEBHOOK_URL}")
            
            # Получаем информацию о webhook для проверки
            webhook_info = await bot.get_webhook_info()
            logger.info(f"Информация о webhook: {webhook_info}")
            
        except Exception as e:
            logger.error(f"Ошибка при установке webhook: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    else:
        logger.info("Режим webhook отключен, будет использоваться long polling")


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
    
    # Проверяем доступность файла перед инициализацией
    if not await csv_storage.check_file_accessibility():
        logger.error("Файл CSV недоступен! Проверьте права доступа и путь к файлу.")
        logger.error(f"Попытка использования файла: {csv_storage.filename}")
        return
    
    await csv_storage.init()
    
    # Отладочная информация о содержимом CSV
    csv_storage.debug_print_mappings()
    
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
        # Проверяем доступность порта
        host = WEBHOOK_HOST
        port = WEBHOOK_PORT
        
        logger.info(f"Проверяем доступность порта {port} на {host}")
        
        if not is_port_available(host, port):
            logger.error(f"Порт {port} на {host} недоступен. Возможно, он уже занят другим процессом.")
            logger.info("Попробуйте использовать другой порт или остановить процесс, использующий порт {port}")
            logger.info("Также проверьте настройки файрвола и права доступа")
            return
        
        logger.info(f"Порт {port} на {host} доступен")
        
        # Создаем веб-приложение
        app = web.Application()
        
        # Middleware для логирования всех запросов
        @web.middleware
        async def log_requests(request, handler):
            # Логируем только запросы к webhook
            if request.path == "/webhook":
                logger.info(f"📨 Получен {request.method} запрос на /webhook")
                logger.info(f"   Заголовки: {dict(request.headers)}")
                
                # Логируем тело POST запросов
                if request.method == "POST":
                    try:
                        body = await request.text()
                        logger.info(f"   Тело запроса: {body}")
                    except Exception as e:
                        logger.error(f"   Ошибка чтения тела запроса: {e}")
            
            # Продолжаем обработку
            response = await handler(request)
            return response
        
        app.middlewares.append(log_requests)
        
        # Добавляем отладочные маршруты для проверки
        async def root_handler(request):
            return web.Response(text="Telegram Bot Webhook Server is running!")
        
        async def health_handler(request):
            return web.json_response({
                "status": "ok",
                "webhook_url": WEBHOOK_URL,
                "host": host,
                "port": port
            })
        
        # Регистрируем базовые маршруты
        app.router.add_get("/", root_handler)
        app.router.add_get("/health", health_handler)
        
        # Создаем обработчик webhook для Telegram
        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        )
        # Регистрируем webhook на пути /webhook
        webhook_handler.register(app, path="/webhook")
        
        logger.info(f"Webhook зарегистрирован на пути: /webhook")
        logger.info(f"Полный URL webhook: {WEBHOOK_URL}")
        logger.info(f"Сервер будет слушать на: {host}:{port}")
        
        # Добавляем обработчики запуска и остановки
        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        # Запускаем HTTP-сервер
        logger.info(f"Запускаем HTTP-сервер на {host}:{port}")
        web.run_app(
            app,
            host=host,
            port=port
        )
    else:
        asyncio.run(run_polling())


if __name__ == "__main__":
    main()
