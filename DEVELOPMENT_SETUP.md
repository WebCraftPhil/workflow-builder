# Local Development Setup Guide

This guide provides step-by-step instructions for setting up a complete local development environment for the n8n Visual Workflow Builder.

## 🚀 Quick Start

If you're in a hurry, copy and run these commands:

```bash
# 1. Prerequisites
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18 && nvm use 18

# 2. Clone and setup
git clone <your-repo-url>
cd workflow-builder

# 3. Frontend setup
npm install
npm run dev

# 4. Backend setup (new terminal)
cd workflow-builder-server
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python main.py

# 5. Services (new terminal)
docker-compose up -d postgres redis

# 6. Access the app
open http://localhost:3000
```

## 📋 Prerequisites

### Required Tools & Versions

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **Node.js** | 18.17.0+ | JavaScript runtime | [nvm](https://github.com/nvm-sh/nvm) recommended |
| **npm** | 8.15.0+ | Package manager | Comes with Node.js |
| **Python** | 3.11+ | Backend services | [pyenv](https://github.com/pyenv/pyenv) recommended |
| **Docker** | 20.10+ | Database & cache | [Docker Desktop](https://www.docker.com/products/docker-desktop) |
| **Docker Compose** | 2.0+ | Service orchestration | Comes with Docker Desktop |
| **Git** | 2.30+ | Version control | [Git Downloads](https://git-scm.com/downloads) |

### Optional but Recommended

| Tool | Purpose | Installation |
|------|---------|--------------|
| **Visual Studio Code** | IDE | [VS Code](https://code.visualstudio.com/) |
| **Postman** | API testing | [Postman](https://www.postman.com/downloads/) |
| **Redis Desktop Manager** | Redis GUI | [Redis Desktop Manager](https://redisdesktop.com/) |

## 🔧 Detailed Setup Instructions

### 1. Environment Setup

#### Install Node.js (using nvm)

```bash
# Install nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload your shell or run:
source ~/.bashrc  # or ~/.zshrc

# Install and use Node.js 18
nvm install 18
nvm use 18
nvm alias default 18

# Verify installation
node --version  # Should show v18.x.x
npm --version   # Should show 8.x.x
```

#### Install Python (using pyenv)

```bash
# Install pyenv
curl https://pyenv.run | bash

# Add to your shell profile
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# Install Python 3.11
pyenv install 3.11.0
pyenv global 3.11.0

# Verify installation
python --version  # Should show Python 3.11.x
pip --version     # Should show pip 22.x.x
```

### 2. Project Structure Setup

```bash
# Clone the repository
git clone <your-repository-url>
cd workflow-builder

# The project should have this structure:
# workflow-builder/
# ├── src/                 # Frontend React app
# ├── workflow-builder-server/  # Backend Python services (create this)
# ├── docker-compose.yml   # Database services (create this)
# └── docs/                # Documentation
```

### 3. Frontend Setup (React + TypeScript)

```bash
# Navigate to frontend directory
cd workflow-builder

# Install dependencies
npm install

# Verify dependencies are installed
npm list --depth=0

# Start development server
npm run dev

# The app should now be running at http://localhost:3000
```

**Available Scripts:**
```bash
npm run dev        # Start development server
npm run build      # Build for production
npm run preview    # Preview production build
npm run lint       # Run ESLint
npm run type-check # Run TypeScript type checking
```

### 4. Backend Setup (Python Services)

```bash
# Create backend directory
mkdir workflow-builder-server
cd workflow-builder-server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\\Scripts\\activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install fastapi uvicorn sqlalchemy alembic redis
pip install python-dotenv pydantic python-multipart
pip install aiofiles python-jose[cryptography] passlib[bcrypt]
pip install requests httpx websockets

# Create requirements.txt
pip freeze > requirements.txt

# Create main.py
cat > main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="n8n Workflow Builder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "n8n Workflow Builder API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
EOF

# Start the backend server
python main.py

# Backend should now be running at http://localhost:8000
```

### 5. Database & Services Setup

```bash
# Create docker-compose.yml in the root directory
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: workflow_builder
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dev_user -d workflow_builder"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  minio:
    image: minio/minio:latest
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/ready"]
      interval: 30s
      timeout: 20s
      retries: 3

volumes:
  postgres_data:
  redis_data:
  minio_data:
EOF

# Start the services
docker-compose up -d

# Verify services are running
docker-compose ps

# Test database connection
docker-compose exec postgres psql -U dev_user -d workflow_builder -c "SELECT 1;"
```

### 6. Environment Configuration

#### Frontend Environment Variables

```bash
# Create .env file in frontend directory
cat > .env << 'EOF'
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# n8n Integration
VITE_N8N_API_URL=http://localhost:5678
VITE_N8N_WEBHOOK_BASE_URL=http://localhost:3000

# Feature Flags
VITE_ENABLE_AI_ASSISTANCE=true
VITE_ENABLE_COLLABORATION=true
VITE_ENABLE_DEBUG_MODE=true

# Analytics (optional)
VITE_ANALYTICS_ID=your-analytics-id
EOF
```

#### Backend Environment Variables

```bash
# Create .env file in backend directory
cat > workflow-builder-server/.env << 'EOF'
# Database
DATABASE_URL=postgresql://dev_user:dev_password@localhost:5432/workflow_builder

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# n8n Configuration
N8N_API_URL=http://localhost:5678
N8N_WEBHOOK_SECRET=your-webhook-secret

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# File Storage
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false

# AI Services (optional)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
EOF
```

#### Docker Environment Variables

```bash
# Create .env file for docker-compose
cat > .env.docker << 'EOF'
# PostgreSQL
POSTGRES_DB=workflow_builder
POSTGRES_USER=dev_user
POSTGRES_PASSWORD=dev_password

# Redis
REDIS_PASSWORD=

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
EOF
```

## 🚀 Running the Complete System

### Development Mode (All Services)

```bash
# Terminal 1: Start databases and storage
docker-compose up -d

# Terminal 2: Start backend API
cd workflow-builder-server
source venv/bin/activate
python main.py

# Terminal 3: Start frontend
cd workflow-builder
npm run dev

# Terminal 4: Start n8n (if running locally)
# n8n start

# Access points:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Database: localhost:5432
# - Redis: localhost:6379
# - MinIO: http://localhost:9000 (console: http://localhost:9001)
```

### Production-like Development

```bash
# Build frontend for production
npm run build

# Start backend with production settings
cd workflow-builder-server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Use production docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## 🔍 Verification and Testing

### Check All Services

```bash
# Test frontend
curl http://localhost:3000

# Test backend API
curl http://localhost:8000/health

# Test database
docker-compose exec postgres psql -U dev_user -d workflow_builder -c "SELECT version();"

# Test Redis
docker-compose exec redis redis-cli ping

# Test MinIO
curl http://localhost:9000/minio/health/ready
```

### Database Setup (First Time)

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U dev_user -d workflow_builder

# Create initial tables (run this in psql)
CREATE TABLE IF NOT EXISTS workflows (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Exit psql
\q
```

## 🛠️ Development Workflow

### Making Changes

```bash
# Frontend changes
# Edit files in src/ directory
# Changes are hot-reloaded automatically

# Backend changes
# Edit files in workflow-builder-server/
# Server restarts automatically with reload=True

# Database changes
# Update schema in workflow-builder-server/app/database/
# Run: alembic upgrade head
```

### Debugging

```bash
# Frontend debugging
# Open http://localhost:3000
# Use browser DevTools

# Backend debugging
# Add breakpoints in VS Code
# Or use print statements with LOG_LEVEL=DEBUG

# Database debugging
# Use psql or a GUI tool like pgAdmin
```

### Adding New Dependencies

```bash
# Frontend
npm install package-name
npm install --save-dev package-name  # For dev dependencies

# Backend
source venv/bin/activate
pip install package-name
pip freeze > requirements.txt

# Update Docker services if needed
docker-compose down
docker-compose up -d --build
```

## 🚨 Troubleshooting

### Common Issues

**Frontend not loading:**
```bash
# Check if dev server is running
lsof -i :3000

# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Backend connection errors:**
```bash
# Check if backend is running
lsof -i :8000

# Verify environment variables
cd workflow-builder-server
python -c "import os; print(os.getenv('DATABASE_URL'))"
```

**Database connection issues:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Test connection manually
psql -h localhost -U dev_user -d workflow_builder
```

**Redis connection issues:**
```bash
# Check if Redis is running
docker-compose ps redis

# Test connection
redis-cli ping
```

### Logs and Monitoring

```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f postgres
docker-compose logs -f backend

# View frontend logs (check terminal where npm run dev is running)

# Database logs
docker-compose exec postgres tail -f /var/log/postgresql/postgresql-15-main.log
```

## 🎯 Next Steps

1. **Complete the agent system** - Implement the WorkflowExecutionAgent, NodeValidationAgent, etc.
2. **Add authentication** - Implement user registration, login, and JWT handling
3. **Connect to n8n** - Implement the n8n API integration for workflow execution
4. **Add real-time features** - Implement WebSocket connections for collaboration
5. **Create tests** - Add unit and integration tests for all components

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs using the commands provided
3. Check if all prerequisites are installed correctly
4. Verify all services are running with `docker-compose ps`

For additional help, refer to:
- [React Documentation](https://react.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

Happy coding! 🚀
