#!/bin/bash

# DevDocs AI Docker Setup Script
echo "🚀 Setting up DevDocs AI with Docker..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy env.example to .env and fill in your configuration:"
    echo "cp env.example .env"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed!"
    echo "Please install Docker Compose and try again."
    exit 1
fi

echo "✅ Environment check passed"

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down

# Remove old images (optional)
read -p "Do you want to rebuild all images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing old images..."
    docker-compose down --rmi all
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 Spark UI: http://localhost:8080"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose logs -f [service_name]"
echo "  Stop services: docker-compose down"
echo "  Restart services: docker-compose restart"
echo "  Rebuild and restart: docker-compose up --build -d"
echo ""
echo "🔍 To view logs for a specific service:"
echo "  Frontend: docker-compose logs -f frontend"
echo "  Backend: docker-compose logs -f backend"
echo "  Kafka: docker-compose logs -f kafka" 