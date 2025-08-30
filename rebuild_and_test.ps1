# PowerShell script to rebuild and test the bot
Write-Host "Rebuilding and testing the Telegram bot..." -ForegroundColor Green

# Stop existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose down

# Remove old containers and images
Write-Host "Removing old containers and images..." -ForegroundColor Yellow
docker-compose rm -f
docker rmi telegram_bot_demo_bot 2>$null

# Rebuild the bot
Write-Host "Rebuilding the bot..." -ForegroundColor Yellow
docker-compose build --no-cache bot

# Start the services
Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose up -d

# Wait a moment for services to start
Start-Sleep -Seconds 5

# Check container status
Write-Host "Checking container status..." -ForegroundColor Yellow
docker-compose ps

# Check bot logs
Write-Host "Checking bot logs..." -ForegroundColor Yellow
docker-compose logs bot

# Test CSV file access
Write-Host "Testing CSV file access..." -ForegroundColor Yellow
docker exec telegram_bot python test_csv_access.py

Write-Host "Rebuild and test completed!" -ForegroundColor Green
Write-Host "Check the logs above for any errors." -ForegroundColor Cyan
