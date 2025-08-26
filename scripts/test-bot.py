#!/usr/bin/env python3
"""
Скрипт для быстрой проверки конфигурации Telegram-бота (с CSV хранилищем).

Что делает скрипт:
- Проверяет наличие обязательных переменных окружения (.env)
- Валидирует формат `WEBHOOK_URL` и `CHANNEL_ID`
- Проверяет валидность `BOT_TOKEN` через запрос `getMe`
- Тестирует CSV хранилище для маппинга сообщений
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from aiogram import Bot

# Добавляем путь к модулям бота
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bot'))

try:
    from csv_storage import CSVMessageStore
except ImportError:
    print("Не удалось импортировать модуль csv_storage")
    print("Убедитесь, что вы находитесь в корневой папке проекта")
    sys.exit(1)

# Загружаем переменные окружения из .env
load_dotenv()


async def test_environment() -> bool:
    """
    Проверка обязательных переменных окружения и их базовой валидности.

    Returns:
        bool: True, если все переменные корректны; иначе False.
    """
    print("Проверка переменных окружения...")

    required_vars = [
        "BOT_TOKEN",
        "WEBHOOK_URL",
        "CHANNEL_ID",
    ]

    all_good = True

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            print(f"{var}: не настроен")
            all_good = False
        else:
            print(f"{var}: настроен")

    # Дополнительные проверки форматов
    webhook_url = os.getenv("WEBHOOK_URL", "")
    if not webhook_url.startswith("https://"):
        print("WEBHOOK_URL должен начинаться с https://")
        all_good = False

    channel_id = os.getenv("CHANNEL_ID", "")
    if not (channel_id.startswith("@") or channel_id.startswith("-100")):
        print("CHANNEL_ID должен начинаться с '@' (username канала) или '-100' (ID канала)")
        all_good = False

    return all_good


async def test_bot_token() -> bool:
    """
    Проверяет валидность токена бота через вызов getMe.

    Returns:
        bool: True, если токен валиден; иначе False.
    """
    print("Проверка токена бота (getMe)...")
    bot_token = os.getenv("BOT_TOKEN", "")

    try:
        bot = Bot(token=bot_token)
        me = await bot.get_me()
        print(f"Токен валиден. Бот: @{me.username} (id={me.id})")
        await bot.session.close()
        return True
    except Exception as e:
        print(f"Ошибка проверки токена: {e}")
        try:
            # Попытка корректно закрыть сессию, если она была создана
            await bot.session.close()  # type: ignore[name-defined]
        except Exception:
            pass
        return False


async def test_csv_storage() -> bool:
    """
    Тестирует CSV хранилище для маппинга сообщений.

    Returns:
        bool: True, если CSV хранилище работает корректно; иначе False.
    """
    print("Тестирование CSV хранилища...")
    
    try:
        # Создаем временный CSV файл для тестирования
        test_filename = "test_mapping.csv"
        
        # Инициализируем хранилище
        storage = CSVMessageStore(test_filename)
        await storage.init()
        print("CSV хранилище инициализировано")
        
        # Тестируем сохранение маппинга
        test_user_id = 12345
        test_user_message_id = 67890
        test_channel_message_id = 11111
        test_user_name = "TestUser"
        
        success = await storage.save_message_mapping(
            user_id=test_user_id,
            user_message_id=test_user_message_id,
            channel_message_id=test_channel_message_id,
            user_name=test_user_name
        )
        
        if success:
            print("Маппинг сообщения сохранен")
        else:
            print("Ошибка сохранения маппинга")
            return False
        
        # Тестируем поиск пользователя по ID сообщения в канале
        found_user_id = await storage.get_user_by_channel_message(test_channel_message_id)
        if found_user_id == test_user_id:
            print("Поиск пользователя по ID сообщения в канале работает")
        else:
            print(f"Ошибка поиска пользователя: ожидалось {test_user_id}, получено {found_user_id}")
            return False
        
        # Тестируем получение количества записей
        count = storage.get_mappings_count()
        if count == 1:
            print("Подсчет записей работает корректно")
        else:
            print(f"Ошибка подсчета записей: ожидалось 1, получено {count}")
            return False
        
        # Тестируем получение всех маппингов
        mappings = await storage.get_all_mappings()
        if len(mappings) == 1 and mappings[0]['user_id'] == str(test_user_id):
            print("Получение всех маппингов работает корректно")
        else:
            print("Ошибка получения всех маппингов")
            return False
        
        # Закрываем хранилище
        await storage.close()
        
        # Удаляем временный файл
        if os.path.exists(test_filename):
            os.remove(test_filename)
            print("Временный файл удален")
        
        return True
        
    except Exception as e:
        print(f"Ошибка при тестировании CSV хранилища: {e}")
        return False


async def main() -> None:
    """
    Точка входа: выполняет проверки окружения, токена и CSV хранилища.
    """
    print("Тестирование Telegram Bot (с CSV хранилищем)...")
    print("=" * 50)

    env_ok = await test_environment()
    print()

    if not env_ok:
        print("Некоторые переменные окружения не настроены или заданы неверно")
        print("Отредактируйте .env файл и запустите тест снова")
        return

    token_ok = await test_bot_token()
    print()

    if not token_ok:
        print("Токен бота невалиден")
        print("Проверьте значение BOT_TOKEN и сетевое подключение")
        return

    csv_ok = await test_csv_storage()
    print()

    if csv_ok:
        print("Все тесты пройдены успешно!")
        print("Бот готов к работе с CSV хранилищем")
    else:
        print("Некоторые тесты не пройдены")
        print("Проверьте логи и настройки CSV хранилища")


if __name__ == "__main__":
    asyncio.run(asyncio.sleep(0))  # гарантируем наличие цикла событий на некоторых платформах
    asyncio.run(main())
