# Исправление ошибки 404: Not Found для Webhook

## 🔍 Описание проблемы

Ошибка "404: Not Found" возникает, когда Telegram пытается отправить webhook на ваш сервер, но не может найти указанный путь.

## 🚨 Причины ошибки 404

### 1. **Несоответствие путей**
- Webhook зарегистрирован на `/webhook`
- Но Telegram пытается отправить на другой путь

### 2. **Неправильный WEBHOOK_URL**
- URL в настройках не соответствует реальному пути сервера
- Отсутствует путь `/webhook` в URL

### 3. **Сервер не запущен**
- HTTP-сервер не запущен или упал
- Порт недоступен

### 4. **Проблемы с маршрутизацией**
- Webhook не зарегистрирован правильно
- Конфликт маршрутов

## 🛠️ Пошаговое исправление

### Шаг 1: Проверьте настройки .env файла

```bash
# .env файл должен содержать:
USE_WEBHOOK=true
WEBHOOK_URL=https://yourdomain.com/webhook  # ОБЯЗАТЕЛЬНО с /webhook в конце!
WEBHOOK_HOST=0.0.0.0  # или 127.0.0.1 для локального тестирования
WEBHOOK_PORT=8000
```

**Важно:** URL должен заканчиваться на `/webhook`!

### Шаг 2: Проверьте соответствие путей

В `main.py` webhook регистрируется на пути `/webhook`:

```python
# Регистрируем webhook на пути /webhook
webhook_handler.register(app, path="/webhook")
```

Это означает, что ваш `WEBHOOK_URL` должен быть:
- ✅ `https://yourdomain.com/webhook`
- ❌ `https://yourdomain.com`
- ❌ `https://yourdomain.com/bot`

### Шаг 3: Проверьте доступность сервера

#### Локальное тестирование:
```bash
# Проверьте, что сервер запущен
curl http://localhost:8000/
# Должен вернуть: "Telegram Bot Webhook Server is running!"

# Проверьте health endpoint
curl http://localhost:8000/health
# Должен вернуть JSON с информацией о webhook

# Проверьте webhook endpoint
curl http://localhost:8000/webhook
# Должен вернуть ответ (возможно, ошибку метода, но не 404)
```

#### Продакшен:
```bash
# Замените yourdomain.com на ваш домен
curl https://yourdomain.com/
curl https://yourdomain.com/health
curl https://yourdomain.com/webhook
```

### Шаг 4: Используйте тестовый скрипт

Запустите тестовый скрипт для проверки всех endpoints:

```bash
cd bot
python test_webhook.py
```

Этот скрипт проверит:
- ✅ Корневой endpoint (`/`)
- ✅ Health endpoint (`/health`)
- ✅ Webhook endpoint (`/webhook`) - все HTTP методы

### Шаг 5: Проверьте логи бота

```bash
# Основные логи
tail -f logs/bot.log

# Логи webhook
grep "webhook" logs/bot.log
grep "Webhook" logs/bot.log
```

### Шаг 6: Проверьте статус webhook

Бот автоматически логирует информацию о webhook при запуске:

```
INFO - Устанавливаем webhook на URL: https://yourdomain.com/webhook
INFO - Webhook успешно установлен: https://yourdomain.com/webhook
INFO - Информация о webhook: {...}
```

## 🔧 Конкретные исправления

### Исправление 1: Правильный WEBHOOK_URL

```bash
# В .env файле
WEBHOOK_URL=https://yourdomain.com/webhook  # Добавьте /webhook!
```

### Исправление 2: Проверка домена

Убедитесь, что ваш домен:
1. **Указывает на правильный сервер**
2. **Имеет SSL сертификат** (HTTPS обязателен для Telegram)
3. **Порт 443 открыт** (если используете стандартный HTTPS)

### Исправление 3: Настройка nginx (если используется)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        return 200 "Bot server is running";
    }
    
    location /webhook {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Исправление 4: Проверка файрвола

```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 80
sudo ufw allow 443

# CentOS/RHEL
sudo firewall-cmd --list-ports
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

## 🧪 Тестирование исправления

### 1. Перезапустите бота
```bash
# Остановите бота
Ctrl+C

# Запустите заново
python main.py
```

### 2. Проверьте логи
```bash
tail -f logs/bot.log
```

### 3. Проверьте endpoints
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/webhook
```

### 4. Запустите тестовый скрипт
```bash
python test_webhook.py
```

### 5. Отправьте тестовое сообщение боту

## 📋 Чек-лист исправления

- [ ] WEBHOOK_URL заканчивается на `/webhook`
- [ ] Сервер запущен и доступен
- [ ] Путь `/webhook` отвечает (не 404)
- [ ] Домен имеет SSL сертификат
- [ ] Файрвол разрешает порты 80/443
- [ ] nginx настроен правильно (если используется)
- [ ] Логи показывают успешную установку webhook
- [ ] Тестовый скрипт проходит все проверки

## 🆘 Если ничего не помогает

### Временное решение: используйте long polling

```bash
# В .env файле
USE_WEBHOOK=false
```

### Отладка с помощью curl

```bash
# Тест webhook endpoint
curl -X POST https://yourdomain.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Проверка заголовков
curl -I https://yourdomain.com/webhook
```

### Проверка DNS

```bash
nslookup yourdomain.com
dig yourdomain.com
```

## 🔍 Новые debug endpoints

Бот теперь имеет дополнительные endpoints для отладки:

- **`/`** - показывает, что сервер работает
- **`/health`** - показывает текущие настройки webhook
- **`/webhook`** - обрабатывает все HTTP методы для отладки

Все запросы к этим endpoints логируются для лучшей отладки.

## 📞 Получение помощи

1. **Проверьте логи** - они содержат детальную информацию
2. **Используйте health endpoint** - `/health` покажет текущие настройки
3. **Запустите тестовый скрипт** - `python test_webhook.py`
4. **Проверьте соответствие путей** - webhook должен быть на `/webhook`
5. **Убедитесь в SSL** - Telegram требует HTTPS
