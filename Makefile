.PHONY: help build up down restart logs clean test ssl

COMPOSE_FILE = docker-compose.yml
BOT_SERVICE = bot
DB_SERVICE = postgres
NGINX_SERVICE = nginx

GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m

help:
	@echo "$(GREEN)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

build:
	@echo "$(GREEN)Сборка Docker образов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build

up:
	@echo "$(GREEN)Запуск сервисов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d

up-bot:
	@echo "$(GREEN)Запуск только бота (polling)...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d $(BOT_SERVICE)

down:
	@echo "$(YELLOW)Остановка сервисов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down

restart:
	@echo "$(YELLOW)Перезапуск сервисов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) restart

logs:
	@echo "$(GREEN)Логи сервисов:$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs

logs-bot:
	@echo "$(GREEN)Логи бота:$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs -f $(BOT_SERVICE)

logs-db:
	@echo "$(GREEN)Логи базы данных:$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs -f $(DB_SERVICE)

logs-nginx:
	@echo "$(GREEN)Логи Nginx:$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs -f $(NGINX_SERVICE)

status:
	@echo "$(GREEN)Статус сервисов:$(NC)"
	docker-compose -f $(COMPOSE_FILE) ps

clean:
	@echo "$(RED)Очистка Docker...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all
	docker system prune -f

ssl:
	@echo "$(GREEN)Создание SSL сертификатов...$(NC)"
	@if [ -f "scripts/generate-ssl.sh" ]; then \
		chmod +x scripts/generate-ssl.sh && ./scripts/generate-ssl.sh; \
	else \
		echo "$(YELLOW)Скрипт generate-ssl.sh не найден$(NC)"; \
	fi

test:
	@echo "$(GREEN)Запуск тестов...$(NC)"
	@if [ -f "scripts/test-bot.py" ]; then \
		python3 scripts/test-bot.py; \
	else \
		echo "$(YELLOW)Скрипт test-bot.py не найден$(NC)"; \
	fi

setup:
	@echo "$(GREEN)Полная настройка проекта...$(NC)"
	@if [ -f "scripts/setup.sh" ]; then \
		chmod +x scripts/setup.sh && ./scripts/setup.sh; \
	else \
		echo "$(YELLOW)Скрипт setup.sh не найден$(NC)"; \
	fi

dev:
	@echo "$(GREEN)Запуск в режиме разработки...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up

dev-build:
	@echo "$(GREEN)Сборка и запуск в режиме разработки...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up --build

prod:
	@echo "$(GREEN)Запуск в продакшен режиме...$(NC)"
	docker-compose -f $(COMPOSE_FILE) -f docker-compose.prod.yml up -d

prod-down:
	@echo "$(YELLOW)Остановка продакшен режима...$(NC)"
	docker-compose -f $(COMPOSE_FILE) -f docker-compose.prod.yml down

monitor:
	@echo "$(GREEN)Мониторинг ресурсов:$(NC)"
	docker stats --no-stream

backup:
	@echo "$(GREEN)Создание резервной копии базы данных...$(NC)"
	@mkdir -p backups
	docker-compose -f $(COMPOSE_FILE) exec -T $(DB_SERVICE) pg_dump -U bot_user telegram_bot > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql

restore:
	@echo "$(YELLOW)Восстановление базы данных...$(NC)"
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Укажите файл для восстановления: make restore FILE=backups/backup_YYYYMMDD_HHMMSS.sql$(NC)"; \
		exit 1; \
	fi
	docker-compose -f $(COMPOSE_FILE) exec -T $(DB_SERVICE) psql -U bot_user -d telegram_bot < $(FILE)

update:
	@echo "$(GREEN)Обновление проекта...$(NC)"
	git pull origin main
	docker-compose -f $(COMPOSE_FILE) down
	docker-compose -f $(COMPOSE_FILE) up -d --build

shell:
	@echo "$(GREEN)Вход в контейнер бота...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec $(BOT_SERVICE) /bin/bash

db-shell:
	@echo "$(GREEN)Вход в контейнер базы данных...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec $(DB_SERVICE) psql -U bot_user -d telegram_bot

health:
	@echo "$(GREEN)Проверка здоровья сервисов...$(NC)"
	@echo "Проверка бота..."
	@curl -s -o /dev/null -w "%{http_code}" https://localhost/health || echo "недоступен"
	@echo "Проверка базы данных..."
	@docker-compose -f $(COMPOSE_FILE) exec -T $(DB_SERVICE) pg_isready -U bot_user || echo "недоступна"

logrotate:
	@echo "$(GREEN)Ротация логов...$(NC)"
	@if [ -d "logs" ]; then \
		tar -czf logs/logs_$(shell date +%Y%m%d_%H%M%S).tar.gz logs/*.log 2>/dev/null || true; \
		find logs -name "*.log" -size +10M -exec truncate -s 0 {} \; 2>/dev/null || true; \
		echo "Логи обработаны"; \
	else \
		echo "Папка logs не найдена"; \
	fi
