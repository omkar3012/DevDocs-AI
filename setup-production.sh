#!/bin/bash

# DevDocs AI Production Setup Script
# This script helps set up the project for production deployment

set -e

echo "🚀 DevDocs AI Production Setup"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_error "Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

print_success "Prerequisites check passed!"

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
    print_status "Initializing Git repository..."
    git init
    print_success "Git repository initialized"
else
    print_status "Git repository already exists"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    print_error ".gitignore file not found. Please ensure it exists."
    exit 1
fi

# Setup frontend
print_status "Setting up frontend..."
cd frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install
    print_success "Frontend dependencies installed"
else
    print_status "Frontend dependencies already installed"
fi

# Create environment file if it doesn't exist
if [ ! -f ".env.local" ]; then
    print_status "Creating frontend environment file..."
    cp env.example .env.local
    print_warning "Please edit frontend/.env.local with your Supabase and OpenAI credentials"
else
    print_status "Frontend environment file already exists"
fi

cd ..

# Setup backend
print_status "Setting up backend..."
cd backend

# Install dependencies
if [ ! -d "__pycache__" ] && [ ! -f "requirements.txt" ]; then
    print_error "Backend requirements.txt not found"
    exit 1
fi

print_status "Installing backend dependencies..."
pip install -r requirements.txt
print_success "Backend dependencies installed"

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating backend environment file..."
    cp env.example .env
    print_warning "Please edit backend/.env with your API keys"
else
    print_status "Backend environment file already exists"
fi

cd ..

# Setup pre-commit hooks
print_status "Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    print_success "Pre-commit hooks installed"
else
    print_warning "pre-commit not installed. Install with: pip install pre-commit"
fi

# Create initial commit
if ! git log --oneline -1 &> /dev/null; then
    print_status "Creating initial commit..."
    git add .
    git commit -m "feat: initial commit - DevDocs AI project setup"
    print_success "Initial commit created"
else
    print_status "Git repository already has commits"
fi

# Display next steps
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo ""
echo "1. 📝 Configure Environment Variables:"
echo "   - Edit frontend/.env.local with your Supabase and OpenAI credentials"
echo "   - Edit backend/.env with your API keys"
echo ""
echo "2. 🗄️  Set up Supabase Database:"
echo "   - Create a project at https://supabase.com"
echo "   - Run migrations: psql -h your-host -U postgres -d postgres -f supabase/migrations/*.sql"
echo "   - Enable vector extension: CREATE EXTENSION IF NOT EXISTS vector;"
echo ""
echo "3. 🚀 Deploy to Vercel:"
echo "   - Push to GitHub: git push origin main"
echo "   - Deploy via Vercel dashboard or CLI"
echo "   - Configure environment variables in Vercel"
echo ""
echo "4. 📚 Read Documentation:"
echo "   - DEPLOYMENT.md for detailed deployment instructions"
echo "   - CONTRIBUTING.md for development guidelines"
echo ""
echo "5. 🧪 Test Your Setup:"
echo "   - Frontend: cd frontend && npm run dev"
echo "   - Backend: cd backend && uvicorn api:app --reload"
echo ""
echo "Need help? Check the documentation or create an issue on GitHub!"
echo ""
print_success "Setup script completed successfully!" 