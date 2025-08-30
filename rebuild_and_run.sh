#!/bin/bash
# Bash скрипт для пересборки и запуска Docker контейнера

echo "Останавливаем и удаляем существующие контейнеры..."
docker-compose down

echo "Удаляем старые образы..."
docker-compose rm -f

echo "Пересобираем образы..."
docker-compose build --no-cache

echo "Создаем директорию logs если её нет..."
mkdir -p logs

echo "Запускаем контейнеры..."
docker-compose up -d

echo "Проверяем статус контейнеров..."
docker-compose ps

echo "Показываем логи бота..."
docker-compose logs bot
