#!/bin/bash

echo "🚀 Setting up DevDocs AI..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ Please edit .env file with your configuration values"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p frontend/components
mkdir -p backend/utils
mkdir -p supabase/migrations
mkdir -p kafka
mkdir -p spark

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Create Supabase storage bucket
echo "🗄️ Setting up Supabase storage..."
echo "Please create a storage bucket named 'api-docs' in your Supabase project"

# Run database migrations
echo "🗄️ Running database migrations..."
echo "Please run the SQL migrations in supabase/migrations/001_initial_schema.sql in your Supabase SQL editor"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Supabase and Hugging Face credentials"
echo "2. Create a storage bucket named 'api-docs' in Supabase"
echo "3. Run the database migrations in Supabase SQL editor"
echo "4. Start the application with: docker-compose up --build"
echo ""
echo "🌐 The application will be available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   Kafka: localhost:9092"
echo "" 