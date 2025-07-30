# DevDocs AI Production Setup Script (PowerShell)
# This script helps set up the project for production deployment

param(
    [switch]$SkipChecks
)

Write-Host "🚀 DevDocs AI Production Setup" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check prerequisites
if (-not $SkipChecks) {
    Write-Status "Checking prerequisites..."
    
    # Check if git is installed
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Error "Git is not installed. Please install Git first."
        exit 1
    }
    
    # Check if Node.js is installed
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    }
    
    # Check Node.js version
    $nodeVersion = (node -v) -replace 'v', ''
    $majorVersion = [int]($nodeVersion.Split('.')[0])
    if ($majorVersion -lt 18) {
        Write-Error "Node.js version 18+ is required. Current version: $(node -v)"
        exit 1
    }
    
    # Check if Python is installed
    if (-not (Get-Command python -ErrorAction SilentlyContinue) -and -not (Get-Command python3 -ErrorAction SilentlyContinue)) {
        Write-Error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    }
    
    Write-Success "Prerequisites check passed!"
}

# Initialize git repository if not already done
if (-not (Test-Path ".git")) {
    Write-Status "Initializing Git repository..."
    git init
    Write-Success "Git repository initialized"
} else {
    Write-Status "Git repository already exists"
}

# Create .gitignore if it doesn't exist
if (-not (Test-Path ".gitignore")) {
    Write-Error ".gitignore file not found. Please ensure it exists."
    exit 1
}

# Setup frontend
Write-Status "Setting up frontend..."
Set-Location frontend

# Install dependencies
if (-not (Test-Path "node_modules")) {
    Write-Status "Installing frontend dependencies..."
    npm install
    Write-Success "Frontend dependencies installed"
} else {
    Write-Status "Frontend dependencies already installed"
}

# Create environment file if it doesn't exist
if (-not (Test-Path ".env.local")) {
    Write-Status "Creating frontend environment file..."
    Copy-Item env.example .env.local
    Write-Warning "Please edit frontend/.env.local with your Supabase and OpenAI credentials"
} else {
    Write-Status "Frontend environment file already exists"
}

Set-Location ..

# Setup backend
Write-Status "Setting up backend..."
Set-Location backend

# Install dependencies
if (-not (Test-Path "requirements.txt")) {
    Write-Error "Backend requirements.txt not found"
    exit 1
}

Write-Status "Installing backend dependencies..."
if (Get-Command python -ErrorAction SilentlyContinue) {
    python -m pip install -r requirements.txt
} else {
    python3 -m pip install -r requirements.txt
}
Write-Success "Backend dependencies installed"

# Create environment file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Status "Creating backend environment file..."
    Copy-Item env.example .env
    Write-Warning "Please edit backend/.env with your API keys"
} else {
    Write-Status "Backend environment file already exists"
}

Set-Location ..

# Setup pre-commit hooks
Write-Status "Setting up pre-commit hooks..."
if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
    pre-commit install
    Write-Success "Pre-commit hooks installed"
} else {
    Write-Warning "pre-commit not installed. Install with: pip install pre-commit"
}

# Create initial commit
try {
    $lastCommit = git log --oneline -1 2>$null
    if (-not $lastCommit) {
        Write-Status "Creating initial commit..."
        git add .
        git commit -m "feat: initial commit - DevDocs AI project setup"
        Write-Success "Initial commit created"
    } else {
        Write-Status "Git repository already has commits"
    }
} catch {
    Write-Warning "Could not create initial commit: $($_.Exception.Message)"
}

# Display next steps
Write-Host ""
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 📝 Configure Environment Variables:" -ForegroundColor White
Write-Host "   - Edit frontend/.env.local with your Supabase and OpenAI credentials" -ForegroundColor Gray
Write-Host "   - Edit backend/.env with your API keys" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 🗄️  Set up Supabase Database:" -ForegroundColor White
Write-Host "   - Create a project at https://supabase.com" -ForegroundColor Gray
Write-Host "   - Run migrations: psql -h your-host -U postgres -d postgres -f supabase/migrations/*.sql" -ForegroundColor Gray
Write-Host "   - Enable vector extension: CREATE EXTENSION IF NOT EXISTS vector;" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 🚀 Deploy to Vercel:" -ForegroundColor White
Write-Host "   - Push to GitHub: git push origin main" -ForegroundColor Gray
Write-Host "   - Deploy via Vercel dashboard or CLI" -ForegroundColor Gray
Write-Host "   - Configure environment variables in Vercel" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 📚 Read Documentation:" -ForegroundColor White
Write-Host "   - DEPLOYMENT.md for detailed deployment instructions" -ForegroundColor Gray
Write-Host "   - CONTRIBUTING.md for development guidelines" -ForegroundColor Gray
Write-Host ""
Write-Host "5. 🧪 Test Your Setup:" -ForegroundColor White
Write-Host "   - Frontend: cd frontend && npm run dev" -ForegroundColor Gray
Write-Host "   - Backend: cd backend && uvicorn api:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "Need help? Check the documentation or create an issue on GitHub!" -ForegroundColor Yellow
Write-Host ""
Write-Success "Setup script completed successfully!" 