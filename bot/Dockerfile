FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создаем пользователя bot с правильными правами
RUN useradd --create-home --shell /bin/bash bot && \
    chown -R bot:bot /app

# Создаем директорию для логов с правильными правами доступа
RUN mkdir -p /app/logs && \
    chown -R bot:bot /app/logs && \
    chmod 755 /app/logs

USER bot

EXPOSE 8000

CMD ["python", "main.py"]
