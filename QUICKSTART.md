# 🚀 Быстрый старт Telegram Bot (с CSV хранилищем)

## 📋 Что нужно для запуска

1. **Docker и Docker Compose** - установлены и работают
2. **Telegram Bot Token** - получить у @BotFather
3. **Канал в Telegram** - создать или использовать существующий
4. **Домен с SSL** - для webhook (можно использовать ngrok для тестирования). Либо используйте режим long polling без домена.

## ⚡ Быстрый запуск

### 1. Клонирование и настройка

```bash
git clone <repository-url>
cd telegram_bot_demo
```

### 2. Настройка переменных окружения

```bash
# Linux/Mac
cp env.example .env

# Windows PowerShell
Copy-Item env.example .env
```

Отредактируйте `.env` файл (выберите один из режимов работы):
```env
# Вариант A: Webhook (требуется домен и SSL)
USE_WEBHOOK=true
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
WEBHOOK_URL=https://your-domain.com/webhook
CHANNEL_ID=@your_channel_username

# Вариант B: Long polling (без домена/SSL)
# USE_WEBHOOK=false
# BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
# CHANNEL_ID=@your_channel_username
```

### 3. Генерация SSL сертификатов (для тестирования)

```bash
# Linux/Mac
chmod +x scripts/generate-ssl.sh
./scripts/generate-ssl.sh

# Windows PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\generate-ssl.ps1
```

### 4. Запуск сервисов (выберите режим)

```bash
# Режим webhook (Nginx + HTTPS)
docker-compose up -d --build

# Режим long polling (только бот)
docker-compose up -d --build bot
```

## 🔧 Ручной запуск (webhook)

Если скрипты не работают:

```bash
# Создание директорий
mkdir -p logs/nginx nginx/ssl

# Запуск сервисов
docker-compose up -d --build

# Проверка статуса
docker-compose ps
```

## 📱 Тестирование

1. **Отправьте сообщение боту** - любое текстовое сообщение
2. **Проверьте канал** - сообщение должно появиться с пометкой от пользователя
3. **Ответьте в канале** - используйте функцию "Ответить" на сообщение
4. **Проверьте бота** - ответ будет залогирован (без пересылки пользователю)

## ⚠️ Важные особенности

### Что работает:
- ✅ Пересылка сообщений от пользователей в канал
- ✅ Поддержка всех типов контента (текст, фото, видео, документы, аудио, голосовые)
- ✅ Webhook настройка
- ✅ Логирование всех операций
- ✅ **Пересылка ответов из канала пользователям** (с помощью CSV)
- ✅ **Хранение истории сообщений** (в CSV формате)

## 🚨 Частые проблемы

### Бот не отвечает
```bash
docker-compose logs bot
```

### Проблемы с SSL (только для webhook)
```bash
docker-compose logs nginx
```

## 🛠️ Полезные команды

```bash
# Просмотр логов в реальном времени
docker-compose logs -f bot

# Перезапуск бота
docker-compose restart bot

# Остановка всех сервисов
docker-compose down

# Обновление и пересборка
docker-compose up -d --build
```

## 📚 Дополнительная документация

- [Полная документация](README.md)
- [Конфигурация Nginx](nginx/nginx.conf)

## 📊 CSV хранилище

Бот использует CSV файл для хранения маппинга сообщений:

- **Файл**: `message_mapping.csv`
- **Структура**: user_id, user_message_id, channel_message_id, created_at, user_name
- **Автоматическое создание**: файл создается при первом запуске
- **Безопасность**: асинхронные операции с блокировками

### Просмотр данных:
```bash
# Просмотр содержимого CSV файла
cat message_mapping.csv

# Подсчет записей
wc -l message_mapping.csv
```

## 🆘 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs`
2. Убедитесь, что все переменные окружения настроены
3. Проверьте SSL сертификаты
4. Создайте Issue в репозитории
