# Настройка Webhook для Telegram бота

## Проблема

Ошибка `OSError: could not bind on any address out of [('185.250.61.34', 8000)]` означает, что бот не может привязаться к указанному IP-адресу.

## Решения

### 1. Локальное тестирование (localhost)

Используйте `127.0.0.1` для локального тестирования:

```python
web.run_app(
    app,
    host="127.0.0.1",  # localhost
    port=8000
)
```

**Преимущества:**
- Работает на локальной машине
- Безопасно для тестирования
- Не требует настройки файрвола

**Недостатки:**
- Telegram не сможет отправить webhook на localhost
- Подходит только для разработки

### 2. Продакшен (все интерфейсы)

Используйте `0.0.0.0` для продакшена:

```python
web.run_app(
    app,
    host="0.0.0.0",  # все интерфейсы
    port=8000
)
```

**Преимущества:**
- Telegram может отправить webhook на ваш сервер
- Работает в продакшене

**Недостатки:**
- Требует настройки файрвола
- Менее безопасно

### 3. Конкретный IP-адрес

Используйте конкретный IP-адрес вашего сервера:

```python
web.run_app(
    app,
    host="185.250.61.34",  # ваш IP
    port=8000
)
```

**Важно:** IP-адрес должен быть доступен на вашем сервере!

## Проверка доступности порта

Бот автоматически проверяет доступность порта перед запуском:

```python
def is_port_available(host: str, port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False
```

## Настройка для разных окружений

### Разработка (Development)

```python
# В .env файле
USE_WEBHOOK=false  # Используем long polling
```

```python
# В main.py
if USE_WEBHOOK:
    # webhook код
else:
    asyncio.run(run_polling())  # long polling
```

### Продакшен (Production)

```python
# В .env файле
USE_WEBHOOK=true
WEBHOOK_URL=https://yourdomain.com/webhook
```

```python
# В main.py
web.run_app(
    app,
    host="0.0.0.0",  # все интерфейсы
    port=8000
)
```

## Настройка файрвола

### Ubuntu/Debian (ufw)

```bash
# Разрешить порт 8000
sudo ufw allow 8000

# Проверить статус
sudo ufw status
```

### CentOS/RHEL (firewalld)

```bash
# Разрешить порт 8000
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# Проверить статус
sudo firewall-cmd --list-ports
```

### Windows

1. Откройте "Брандмауэр Windows Defender"
2. Нажмите "Дополнительные параметры"
3. Выберите "Правила для входящих подключений"
4. Создайте новое правило для порта 8000

## Проверка доступности

### Локально

```bash
# Проверить, что порт слушается
netstat -tlnp | grep :8000

# Или
ss -tlnp | grep :8000
```

### Извне

```bash
# С другого сервера
telnet 185.250.61.34 8000

# Или
nc -zv 185.250.61.34 8000
```

## Альтернативные порты

Если порт 8000 занят, используйте другой:

```python
# В .env файле
WEBHOOK_PORT=8001

# В main.py
port = int(os.getenv("WEBHOOK_PORT", 8000))
```

## Nginx как прокси

Используйте nginx для проксирования webhook:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location /webhook {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Отладка

### Логи

Проверьте логи бота:
```bash
tail -f logs/bot.log
```

### Статус webhook

```python
# Проверить статус webhook
webhook_info = await bot.get_webhook_info()
print(webhook_info)
```

### Тест webhook

```bash
# Отправить тестовый запрос
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## Рекомендации

1. **Для разработки**: используйте long polling (`USE_WEBHOOK=false`)
2. **Для тестирования webhook**: используйте `127.0.0.1`
3. **Для продакшена**: используйте `0.0.0.0` с настройкой файрвола
4. **Всегда проверяйте**: доступность порта перед запуском
5. **Используйте nginx**: для проксирования в продакшене
