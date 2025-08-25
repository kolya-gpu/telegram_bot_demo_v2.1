# Telegram Bot - Пересылка сообщений (с CSV хранилищем)

Telegram-бот на Python (aiogram) для перенаправления сообщений от пользователей в канал. Поддерживает два режима приёма обновлений: webhook (через Nginx + HTTPS) и long polling (без домена и SSL). **Версия 2.1** - с CSV хранилищем для отслеживания сообщений.

## 🚀 Основной функционал

- ✅ Приём сообщений от пользователя (текст, фото, видео, документы, аудио, голосовые)
- ✅ Пересылка сообщений в указанный канал
- ✅ Поддержка всех типов контента Telegram
- ✅ Webhook или Long polling для получения обновлений
- ✅ Логирование всех операций

## ✅ Возможности текущей версии

- ✅ **Пересылка сообщений от пользователей в канал**
- ✅ **Пересылка ответов из канала пользователям** (с помощью CSV)
- ✅ **Хранение истории сообщений** (в CSV формате)
- ✅ **Отслеживание соответствий** user_id ↔ сообщение в канале
- ✅ **Поддержка всех типов контента** Telegram
- ✅ **Webhook для получения обновлений**
- ✅ **Логирование всех операций**

## 🏗️ Архитектура

- **Сервис bot** (Python 3.11 + aiogram) — принимает обновления (webhook или polling)
- **Nginx** — только для режима webhook: принимает HTTPS, проксирует на бота
- **Docker Compose** — для локального запуска и тестов

## 📋 Требования

- Docker и Docker Compose
- Telegram Bot Token (получить у @BotFather)
- Домен с SSL-сертификатом (для webhook)
- Канал в Telegram

## 🛠️ Установка и настройка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd telegram_bot_demo
```

### 2. Настройка переменных окружения

Скопируйте файл `env.example` в `.env` и заполните необходимые значения:

```bash
cp env.example .env
```

Отредактируйте `.env` файл (выберите режим):

```env
# Webhook
USE_WEBHOOK=true
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
WEBHOOK_URL=https://your-domain.com/webhook
CHANNEL_ID=@your_channel_username

# Long polling
# USE_WEBHOOK=false
# BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
# CHANNEL_ID=@your_channel_username
```

### 3. Настройка SSL-сертификатов (только для webhook)

Создайте папку `nginx/ssl/` и поместите туда ваши SSL-сертификаты:

```bash
mkdir -p nginx/ssl
# Скопируйте cert.pem и key.pem в nginx/ssl/
```

### 4. Запуск сервисов (выберите режим)

```bash
# Webhook: Nginx + бот
docker-compose up -d

# Long polling: только бот
docker-compose up -d bot
```

### 5. Проверка работы

```bash
# Проверка статуса сервисов
docker-compose ps

# Просмотр логов бота
docker-compose logs bot

# Webhook: проверка
curl -k https://your-domain.com/health

# Long polling: смотрите логи бота
docker-compose logs -f bot
```

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|---------|
| `BOT_TOKEN` | Токен бота от @BotFather | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `USE_WEBHOOK` | Вкл/выкл webhook. Если false — используется long polling | `true`/`false` |
| `WEBHOOK_URL` | URL для webhook (только при USE_WEBHOOK=true) | `https://your-domain.com/webhook` |
| `CHANNEL_ID` | ID или username канала | `@your_channel` или `-1001234567890` |

## 📱 Использование

### 1. Отправка сообщения боту

Пользователь отправляет любое сообщение боту:
- Текст
- Фото
- Видео
- Документы
- Аудио
- Голосовые сообщения

### 2. Пересылка в канал

Бот автоматически пересылает сообщение в указанный канал с пометкой от какого пользователя оно пришло.

### 3. Ответ администратора

Администратор в канале отвечает на сообщение (используя функцию "Ответить").

### 4. Сохранение в CSV

Бот сохраняет маппинг сообщения в CSV файл:
- user_id: ID пользователя
- user_message_id: ID сообщения пользователя
- channel_message_id: ID сообщения в канале
- created_at: время создания записи
- user_name: имя пользователя

### 5. Ответ администратора

Администратор в канале отвечает на сообщение (использует функцию "Ответить").

### 6. Пересылка ответа пользователю

Бот автоматически определяет, кому принадлежит исходное сообщение, и пересылает ответ из канала этому пользователю.

## 🔍 Логирование

Логи сохраняются в папку `logs/`:

- `logs/` - логи бота
- `logs/nginx/` - логи Nginx

## 🐳 Docker команды

```bash
# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down

# Перезапуск конкретного сервиса
docker-compose restart bot

# Просмотр логов
docker-compose logs -f bot

# Обновление и пересборка
docker-compose up -d --build
```

## 🚨 Устранение неполадок

### Бот не отвечает

1. Проверьте токен бота в `.env`
2. Убедитесь, что webhook установлен корректно
3. Проверьте логи: `docker-compose logs bot`

### Проблемы с SSL

1. Убедитесь, что сертификаты находятся в `nginx/ssl/`
2. Проверьте права доступа к файлам сертификатов
3. Проверьте логи Nginx: `docker-compose logs nginx`

## 📚 API Endpoints

В режиме webhook:
- `POST /webhook` — вход для Telegram API
- `GET /health` — проверка статуса через Nginx

В режиме long polling:
- HTTP эндпоинты не поднимаются; обмен идёт через polling.

## 📊 CSV хранилище

Бот использует CSV файл для хранения маппинга сообщений:

### Структура данных:
```csv
user_id,user_message_id,channel_message_id,created_at,user_name
12345,67890,11111,2024-01-01T12:00:00,John
```

### Особенности:
- **Автоматическое создание**: файл создается при первом запуске
- **Безопасность**: асинхронные операции с блокировками
- **Простота**: легко просматривать и анализировать данные
- **Переносимость**: можно открыть в Excel, Google Sheets и т.д.

### Управление данными:
```bash
# Просмотр содержимого
cat message_mapping.csv

# Подсчет записей
wc -l message_mapping.csv

# Резервное копирование
cp message_mapping.csv backup_$(date +%Y%m%d).csv
```

## 🔒 Безопасность

- Бот работает только через HTTPS
- Используется безопасная конфигурация SSL
- Бот работает под непривилегированным пользователем
- CSV файл содержит только ID сообщений (без личной информации)

## 🔄 Миграция данных

### Из CSV в базу данных

Если в будущем вы захотите перейти на PostgreSQL:

1. **Экспорт данных** из CSV:
```python
import csv
import asyncpg

async def migrate_csv_to_postgres():
    # Читаем CSV
    with open('message_mapping.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    # Подключаемся к PostgreSQL
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Создаем таблицу
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS message_mapping (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            user_message_id BIGINT NOT NULL,
            channel_message_id BIGINT NOT NULL,
            created_at TIMESTAMP,
            user_name TEXT
        )
    ''')
    
    # Вставляем данные
    for row in data:
        await conn.execute('''
            INSERT INTO message_mapping 
            (user_id, user_message_id, channel_message_id, created_at, user_name)
            VALUES ($1, $2, $3, $4, $5)
        ''', int(row['user_id']), int(row['user_message_id']), 
             int(row['channel_message_id']), row['created_at'], row['user_name'])
    
    await conn.close()
```

2. **Обновите код** для работы с PostgreSQL
3. **Добавьте** `DATABASE_URL` в `.env`
4. **Обновите** `requirements.txt` (добавьте `asyncpg`)

### Преимущества CSV:
- ✅ Простота настройки
- ✅ Легкость просмотра данных
- ✅ Отсутствие зависимостей от БД
- ✅ Переносимость данных

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License

## 📞 Поддержка

При возникновении проблем создайте Issue в репозитории проекта.
