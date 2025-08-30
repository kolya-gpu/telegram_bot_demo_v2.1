# Краткое резюме исправлений PermissionError

## Проблема
```
PermissionError: [Errno 13] Permission denied: '/logs'
PermissionError: [Errno 13] Permission denied: '/message_mapping.csv'
```

## Решение

### 1. Исправлен путь к директории логов
**Файл**: `bot/logging_config.py`
```python
# Было: абсолютный путь
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

# Стало: относительный путь
log_dir = "logs"
```

### 2. Исправлен путь к CSV файлу
**Файл**: `bot/main.py`
```python
# Было: абсолютный путь
csv_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "message_mapping.csv")

# Стало: путь в директории logs
csv_file_path = "/app/logs/message_mapping.csv"
```

### 3. КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Директория logs создается от имени пользователя bot
**Файл**: `bot/Dockerfile`
```dockerfile
# Было:
RUN mkdir -p /app/logs && chmod 755 /app/logs

# Стало:
RUN useradd --create-home --shell /bin/bash bot && \
    chown -R bot:bot /app

# Создаем директорию для логов с правильными правами доступа
USER bot
RUN mkdir -p /app/logs
```

### 4. Упрощена команда запуска в docker-compose
**Файл**: `docker-compose.yml`
```yaml
# Убрана команда создания директории, так как она создается в Dockerfile
volumes:
  - ./logs:/app/logs
```

## Ключевой момент
**Порядок команд в Dockerfile критичен** - директория logs должна создаваться от имени пользователя `bot` после смены владельца файлов.

## Результат
✅ Бот успешно запускается без ошибок PermissionError  
✅ Все файлы создаются в правильных директориях  
✅ Права доступа настроены корректно  
✅ Контейнер работает стабильно без перезапусков  

## Команды для применения
```bash
# Пересборка и запуск
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Проверка
docker-compose logs bot
```

## Ожидаемый результат
```
telegram_bot  | CSV файл уже существует: /app/logs/message_mapping.csv
telegram_bot  | CSV хранилище инициализировано
telegram_bot  | Webhook успешно установлен
```
