Write-Host "🚀 Настройка Telegram Bot..." -ForegroundColor Green

try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker найден: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker не установлен. Установите Docker Desktop и попробуйте снова." -ForegroundColor Red
    exit 1
}

try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose найден: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова." -ForegroundColor Red
    exit 1
}

Write-Host "📁 Создание директорий..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "logs/nginx" | Out-Null
New-Item -ItemType Directory -Force -Path "nginx/ssl" | Out-Null

if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Файл .env не найден. Создаем из примера..." -ForegroundColor Yellow
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Host "📝 Файл .env создан. Отредактируйте его и добавьте необходимые переменные окружения." -ForegroundColor Cyan
        Write-Host "   - BOT_TOKEN: токен вашего бота от @BotFather" -ForegroundColor White
        Write-Host "   - WEBHOOK_URL: URL для webhook (например, https://your-domain.com/webhook)" -ForegroundColor White
        Write-Host "   - CHANNEL_ID: ID или username вашего канала" -ForegroundColor White
        Write-Host ""
        Write-Host "После настройки .env файла запустите скрипт снова." -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "❌ Файл env.example не найден. Создайте .env файл вручную." -ForegroundColor Red
        exit 1
    }
}

if (-not (Test-Path "nginx/ssl/cert.pem") -or -not (Test-Path "nginx/ssl/key.pem")) {
    Write-Host "⚠️  SSL сертификаты не найдены в nginx/ssl/" -ForegroundColor Yellow
    Write-Host "   Создайте самоподписанные сертификаты для тестирования:" -ForegroundColor White
    Write-Host ""
    Write-Host "   mkdir -p nginx/ssl" -ForegroundColor Gray
    Write-Host "   openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -days 365 -nodes" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   Или поместите ваши SSL сертификаты в папку nginx/ssl/" -ForegroundColor White
    Write-Host "   - cert.pem - сертификат" -ForegroundColor White
    Write-Host "   - key.pem - приватный ключ" -ForegroundColor White
    Write-Host ""
    Write-Host "После настройки SSL сертификатов запустите скрипт снова." -ForegroundColor Yellow
    exit 0
}

Write-Host "✅ SSL сертификаты найдены" -ForegroundColor Green

Write-Host "🔍 Проверка переменных окружения..." -ForegroundColor Yellow
Get-Content ".env" | ForEach-Object {
    if ($_ -match "^([^#][^=]+)=(.*)$") {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        
        if ($name -eq "BOT_TOKEN" -and ($value -eq "your_bot_token_here" -or $value -eq "")) {
            Write-Host "❌ BOT_TOKEN не настроен в .env файле" -ForegroundColor Red
            exit 1
        }
        
        if ($name -eq "WEBHOOK_URL" -and ($value -eq "https://your-domain.com/webhook" -or $value -eq "")) {
            Write-Host "❌ WEBHOOK_URL не настроен в .env файле" -ForegroundColor Red
            exit 1
        }
        
        if ($name -eq "CHANNEL_ID" -and ($value -eq "@your_channel_username" -or $value -eq "")) {
            Write-Host "❌ CHANNEL_ID не настроен в .env файле" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host "✅ Переменные окружения настроены корректно" -ForegroundColor Green

Write-Host "🛑 Остановка существующих контейнеров..." -ForegroundColor Yellow
docker-compose down

Write-Host "🔨 Сборка и запуск сервисов..." -ForegroundColor Yellow
docker-compose up -d --build

Write-Host "⏳ Ожидание запуска сервисов..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "📊 Статус сервисов:" -ForegroundColor Green
docker-compose ps

Write-Host ""
Write-Host "🎉 Telegram Bot успешно запущен!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Для проверки работы:" -ForegroundColor White
Write-Host "   1. Отправьте сообщение вашему боту" -ForegroundColor White
Write-Host "   2. Проверьте, что сообщение появилось в канале" -ForegroundColor White
Write-Host "   3. Ответьте на сообщение в канале" -ForegroundColor White
Write-Host "   4. Убедитесь, что ответ дошел пользователю" -ForegroundColor White
Write-Host ""
Write-Host "📋 Полезные команды:" -ForegroundColor White
Write-Host "   - Просмотр логов: docker-compose logs -f bot" -ForegroundColor Gray
Write-Host "   - Остановка: docker-compose down" -ForegroundColor Gray
Write-Host "   - Перезапуск: docker-compose restart bot" -ForegroundColor Gray
Write-Host ""
Write-Host "🔗 Webhook URL: $(Get-Content '.env' | Where-Object { $_ -match '^WEBHOOK_URL=' } | ForEach-Object { $_.Split('=')[1] })" -ForegroundColor Cyan
Write-Host "📢 Канал: $(Get-Content '.env' | Where-Object { $_ -match '^CHANNEL_ID=' } | ForEach-Object { $_.Split('=')[1] })" -ForegroundColor Cyan
