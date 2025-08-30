# PowerShell скрипт для пересборки и запуска Docker контейнера
Write-Host "Останавливаем и удаляем существующие контейнеры..." -ForegroundColor Yellow
docker-compose down

Write-Host "Удаляем старые образы..." -ForegroundColor Yellow
docker-compose rm -f

Write-Host "Пересобираем образы..." -ForegroundColor Yellow
docker-compose build --no-cache

Write-Host "Создаем директорию logs если её нет..." -ForegroundColor Yellow
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force
}

Write-Host "Запускаем контейнеры..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "Проверяем статус контейнеров..." -ForegroundColor Yellow
docker-compose ps

Write-Host "Показываем логи бота..." -ForegroundColor Yellow
docker-compose logs bot
