# Тестирование Webhook Endpoints

## 🚀 Быстрый старт

### 1. Запустите бота
```bash
cd bot
python main.py
```

### 2. В другом терминале запустите тесты
```bash
cd bot
python test_webhook.py
```

## 🔍 Доступные Endpoints

### ✅ Корневой endpoint
- **Путь:** `/`
- **Метод:** GET
- **Ожидаемый ответ:** `200 OK` с текстом "Telegram Bot Webhook Server is running!"

### ✅ Health endpoint
- **Путь:** `/health`
- **Метод:** GET
- **Ожидаемый ответ:** `200 OK` с JSON информацией о webhook

### ✅ Webhook endpoint
- **Путь:** `/webhook`
- **Метод:** POST (только от Telegram)
- **Ожидаемый ответ:** `200 OK` для валидных webhook запросов

## 🧪 Тестирование вручную

### С помощью curl

```bash
# Тест корневого endpoint
curl http://localhost:8000/

# Тест health endpoint
curl http://localhost:8000/health

# Тест webhook endpoint (GET - должен вернуть 405)
curl http://localhost:8000/webhook

# Тест webhook endpoint (POST)
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### С помощью браузера

Откройте в браузере:
- `http://localhost:8000/` - корневой endpoint
- `http://localhost:8000/health` - health endpoint

## 📊 Ожидаемые результаты тестов

| Endpoint | Метод | Ожидаемый статус | Описание |
|----------|-------|------------------|----------|
| `/` | GET | 200 OK | Сервер работает |
| `/health` | GET | 200 OK | JSON с настройками |
| `/webhook` | GET | 405 Method Not Allowed | GET не поддерживается |
| `/webhook` | POST | 200 OK | Webhook от Telegram |
| `/webhook` | PUT | 405 Method Not Allowed | PUT не поддерживается |

## 🔧 Отладка

### Логирование

Все запросы к `/webhook` автоматически логируются:

```bash
# Следите за логами в реальном времени
tail -f logs/bot.log

# Фильтруйте логи webhook
grep "webhook" logs/bot.log
grep "📨 Получен" logs/bot.log
```

### Проверка статуса webhook

В логах при запуске вы увидите:

```
INFO - Устанавливаем webhook на URL: https://yourdomain.com/webhook
INFO - Webhook успешно установлен: https://yourdomain.com/webhook
INFO - Информация о webhook: {...}
```

## 🚨 Устранение неполадок

### Ошибка "Port already in use"

```bash
# Найдите процесс, использующий порт 8000
netstat -tlnp | grep :8000

# Остановите процесс
kill -9 <PID>
```

### Ошибка "Method Not Allowed"

Это нормально для GET/PUT запросов к `/webhook`. Telegram использует только POST.

### Endpoint не отвечает

1. Проверьте, что бот запущен
2. Проверьте логи на ошибки
3. Убедитесь, что порт 8000 доступен

## 📝 Примеры ответов

### Health endpoint
```json
{
  "status": "ok",
  "webhook_url": "https://yourdomain.com/webhook",
  "host": "127.0.0.1",
  "port": 8000
}
```

### Webhook endpoint (POST)
```json
{
  "status": "received",
  "data": {
    "test": "data",
    "message": "Это тестовый webhook запрос"
  }
}
```

## 🎯 Цель тестирования

Тесты проверяют:

1. **Сервер запущен** - endpoint `/` отвечает
2. **Настройки корректны** - endpoint `/health` показывает правильные параметры
3. **Webhook работает** - endpoint `/webhook` принимает POST запросы
4. **Безопасность** - неподдерживаемые методы отклоняются

## 🔄 Автоматическое тестирование

Для CI/CD добавьте в ваш pipeline:

```bash
# Установите зависимости
pip install aiohttp

# Запустите тесты
python test_webhook.py

# Проверьте exit code
echo $?
```
