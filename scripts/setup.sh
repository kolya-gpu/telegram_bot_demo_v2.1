#!/bin/bash

set -e

echo "🚀 Настройка Telegram Bot..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

echo "✅ Docker и Docker Compose найдены"

echo "📁 Создание директорий..."
mkdir -p logs/nginx
mkdir -p nginx/ssl

if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден. Создаем из примера..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "📝 Файл .env создан. Отредактируйте его и добавьте необходимые переменные окружения."
        echo "   - BOT_TOKEN: токен вашего бота от @BotFather"
        echo "   - WEBHOOK_URL: URL для webhook (например, https://your-domain.com/webhook)"
        echo "   - CHANNEL_ID: ID или username вашего канала"
        echo ""
        echo "После настройки .env файла запустите скрипт снова."
        exit 0
    else
        echo "❌ Файл env.example не найден. Создайте .env файл вручную."
        exit 1
    fi
fi

if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
    echo "⚠️  SSL сертификаты не найдены в nginx/ssl/"
    echo "   Создайте самоподписанные сертификаты для тестирования:"
    echo ""
    echo "   mkdir -p nginx/ssl"
    echo "   openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -days 365 -nodes"
    echo ""
    echo "   Или поместите ваши SSL сертификаты в папку nginx/ssl/"
    echo "   - cert.pem - сертификат"
    echo "   - key.pem - приватный ключ"
    echo ""
    echo "После настройки SSL сертификатов запустите скрипт снова."
    exit 0
fi

echo "✅ SSL сертификаты найдены"

echo "🔍 Проверка переменных окружения..."
source .env

if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your_bot_token_here" ]; then
    echo "❌ BOT_TOKEN не настроен в .env файле"
    exit 1
fi

if [ -z "$WEBHOOK_URL" ] || [ "$WEBHOOK_URL" = "https://your-domain.com/webhook" ]; then
    echo "❌ WEBHOOK_URL не настроен в .env файле"
    exit 1
fi

if [ -z "$CHANNEL_ID" ] || [ "$CHANNEL_ID" = "@your_channel_username" ]; then
    echo "❌ CHANNEL_ID не настроен в .env файле"
    exit 1
fi

echo "✅ Переменные окружения настроены корректно"

echo "🛑 Остановка существующих контейнеров..."
docker-compose down

echo "🔨 Сборка и запуск сервисов..."
docker-compose up -d --build

echo "⏳ Ожидание запуска сервисов..."
sleep 10

echo "📊 Статус сервисов:"
docker-compose ps

echo ""
echo "🎉 Telegram Bot успешно запущен!"
echo ""
echo "📱 Для проверки работы:"
echo "   1. Отправьте сообщение вашему боту"
echo "   2. Проверьте, что сообщение появилось в канале"
echo "   3. Ответьте на сообщение в канале"
echo "   4. Убедитесь, что ответ дошел пользователю"
echo ""
echo "📋 Полезные команды:"
echo "   - Просмотр логов: docker-compose logs -f bot"
echo "   - Остановка: docker-compose down"
echo "   - Перезапуск: docker-compose restart bot"
echo ""
echo "🔗 Webhook URL: $WEBHOOK_URL"
echo "📢 Канал: $CHANNEL_ID"
