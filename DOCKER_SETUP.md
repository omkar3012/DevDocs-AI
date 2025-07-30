# Docker Setup Guide for DevDocs AI

This guide will help you run the entire DevDocs AI application using Docker containers.

## Prerequisites

1. **Docker Desktop** installed and running
   - Download from: https://www.docker.com/products/docker-desktop/
   - Make sure Docker Desktop is running before proceeding

2. **Docker Compose** (usually included with Docker Desktop)
   - Verify installation: `docker-compose --version`

3. **Environment Configuration**
   - Copy `env.example` to `.env`
   - Fill in your API keys and configuration

## Quick Start (Windows)

1. **Open PowerShell** in the project root directory

2. **Run the setup script:**
   ```powershell
   .\setup-docker.ps1
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Spark UI: http://localhost:8080

## Quick Start (Linux/Mac)

1. **Open terminal** in the project root directory

2. **Make the script executable and run:**
   ```bash
   chmod +x setup-docker.sh
   ./setup-docker.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Spark UI: http://localhost:8080

## Manual Setup

If you prefer to run commands manually:

### 1. Environment Setup
```bash
# Copy environment template
cp env.example .env

# Edit .env file with your configuration
# Required variables:
# - NEXT_PUBLIC_SUPABASE_URL
# - NEXT_PUBLIC_SUPABASE_ANON_KEY
# - SUPABASE_URL
# - SUPABASE_SERVICE_ROLE_KEY
# - OPENAI_API_KEY
```

### 2. Build and Start Services
```bash
# Stop any existing containers
docker-compose down

# Build and start all services
docker-compose up --build -d

#Build specific services
docker-compose build backend
docker-compose build frontend

# Check service status
docker-compose ps
```

### 3. Verify Services
```bash
# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f kafka
```

## Service Architecture

The application consists of the following services:

- **Frontend** (Next.js): `http://localhost:3000`
- **Backend** (FastAPI): `http://localhost:8000`
- **Kafka**: Message broker for async processing
- **Zookeeper**: Required for Kafka
- **Embedding Worker**: Processes document embeddings
- **Spark** (Optional): Analytics processing

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   netstat -ano | findstr :3000
   netstat -ano | findstr :8000
   
   # Stop the process or change ports in docker-compose.yml
   ```

2. **Frontend Can't Connect to Backend**
   - Ensure backend service is running: `docker-compose logs backend`
   - Check environment variables: `docker-compose exec frontend env | grep BACKEND`

3. **Kafka Connection Issues**
   ```bash
   # Check Kafka logs
   docker-compose logs kafka
   
   # Restart Kafka
   docker-compose restart kafka
   ```

4. **Permission Issues (Linux/Mac)**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

### Useful Commands

```bash
# View all running containers
docker-compose ps

# View logs for a specific service
docker-compose logs -f [service_name]

# Restart a specific service
docker-compose restart [service_name]

# Stop all services
docker-compose down

# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Rebuild and restart all services
docker-compose up --build -d

# Access a running container
docker-compose exec [service_name] bash

# View resource usage
docker stats
```

### Environment Variables

Make sure your `.env` file contains all required variables:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# MCP Configuration (Optional)
MCP_SERVER_URL=your_mcp_server_url_here

# Backend Configuration
BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Frontend Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Optional: Spark Configuration
SPARK_MASTER_URL=spark://spark-master:7077
```

## Development Workflow

### Making Changes

1. **Code changes** are automatically reflected due to volume mounts
2. **Frontend** will hot-reload automatically
3. **Backend** will restart automatically with `--reload` flag

### Adding Dependencies

1. **Frontend dependencies:**
   ```bash
   # Add to package.json, then rebuild
   docker-compose up --build frontend
   ```

2. **Backend dependencies:**
   ```bash
   # Add to requirements.txt, then rebuild
   docker-compose up --build backend
   ```

### Database Migrations

If you need to run Supabase migrations:

```bash
# Access the backend container
docker-compose exec backend bash

# Run migrations (if you have a migration script)
python -m your_migration_script
```

## Production Deployment

For production deployment, consider:

1. **Remove development volumes** and use production builds
2. **Set up proper logging** and monitoring
3. **Configure SSL/TLS** certificates
4. **Set up proper backup** strategies for Kafka and databases
5. **Use environment-specific** configuration files

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify environment variables are set correctly
3. Ensure all required services are running
4. Check Docker Desktop is running and has sufficient resources 