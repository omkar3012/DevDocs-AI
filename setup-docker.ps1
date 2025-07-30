# DevDocs AI Docker Setup Script for Windows
Write-Host "🚀 Setting up DevDocs AI with Docker..." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy env.example to .env and fill in your configuration:" -ForegroundColor Yellow
    Write-Host "Copy-Item env.example .env" -ForegroundColor Cyan
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Error: Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

# Check if Docker Compose is available
try {
    docker-compose --version | Out-Null
} catch {
    Write-Host "❌ Error: docker-compose is not installed!" -ForegroundColor Red
    Write-Host "Please install Docker Compose and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Environment check passed" -ForegroundColor Green

# Stop any existing containers
Write-Host "🛑 Stopping any existing containers..." -ForegroundColor Yellow
docker-compose down

# Remove old images (optional)
$rebuild = Read-Host "Do you want to rebuild all images? (y/N)"
if ($rebuild -eq "y" -or $rebuild -eq "Y") {
    Write-Host "🗑️  Removing old images..." -ForegroundColor Yellow
    docker-compose down --rmi all
}

# Build and start services
Write-Host "🔨 Building and starting services..." -ForegroundColor Yellow
docker-compose up --build -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host "📊 Service Status:" -ForegroundColor Green
docker-compose ps

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📊 Spark UI: http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs: docker-compose logs -f [service_name]" -ForegroundColor White
Write-Host "  Stop services: docker-compose down" -ForegroundColor White
Write-Host "  Restart services: docker-compose restart" -ForegroundColor White
Write-Host "  Rebuild and restart: docker-compose up --build -d" -ForegroundColor White
Write-Host ""
Write-Host "🔍 To view logs for a specific service:" -ForegroundColor Yellow
Write-Host "  Frontend: docker-compose logs -f frontend" -ForegroundColor White
Write-Host "  Backend: docker-compose logs -f backend" -ForegroundColor White
Write-Host "  Kafka: docker-compose logs -f kafka" -ForegroundColor White