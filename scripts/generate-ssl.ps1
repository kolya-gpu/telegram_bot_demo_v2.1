Write-Host "🔐 Генерация самоподписанных SSL-сертификатов..." -ForegroundColor Green

New-Item -ItemType Directory -Force -Path "nginx/ssl" | Out-Null

try {
    $opensslVersion = openssl version
    Write-Host "✅ OpenSSL найден: $opensslVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ OpenSSL не найден. Установите OpenSSL или используйте готовые сертификаты." -ForegroundColor Red
    Write-Host "   Скачать можно с: https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor Yellow
    exit 1
}

Write-Host "🔨 Генерация сертификата..." -ForegroundColor Yellow
openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -days 365 -nodes -subj "/C=RU/ST=State/L=City/O=Organization/CN=localhost"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSL сертификаты созданы:" -ForegroundColor Green
    Write-Host "   - Сертификат: nginx/ssl/cert.pem" -ForegroundColor White
    Write-Host "   - Приватный ключ: nginx/ssl/key.pem" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  ВНИМАНИЕ: Это самоподписанные сертификаты для тестирования!" -ForegroundColor Yellow
    Write-Host "   Для продакшена используйте настоящие SSL сертификаты от Let's Encrypt или другого CA." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔒 Сертификаты готовы к использованию!" -ForegroundColor Green
} else {
    Write-Host "❌ Ошибка при генерации сертификатов" -ForegroundColor Red
    exit 1
}
