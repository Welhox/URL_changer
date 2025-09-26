# 🚀 Coventure.es URL Shortener

> **A professional, production-ready URL shortening service built with FastAPI, React, and PostgreSQL**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)](https://nginx.org/)

---

## 🌟 Overview

**Coventure.es URL Shortener** is a comprehensive, enterprise-grade URL shortening service designed for production deployment. Built with modern technologies and security best practices, it provides reliable URL shortening with analytics, rate limiting, and comprehensive monitoring.

### 🎯 Key Features

- **🔒 Production Security**: API authentication, rate limiting, input validation
- **📊 Analytics**: Click tracking and usage statistics
- **⚡ High Performance**: FastAPI backend with async support
- **🌐 Modern Frontend**: React with TypeScript and Tailwind CSS
- **🐳 Docker Ready**: Complete containerization with docker-compose
- **📈 Monitoring**: Health checks, metrics, and error tracking
- **🔐 SSL/TLS**: Full HTTPS support with Let's Encrypt integration

---

## � Domain Configuration

The URL shortener is designed to work with any domain. Key configuration is managed through environment variables:

- **`DOMAIN`**: Your domain name (e.g., `example.com`)
- **`BASE_URL`**: Full URL including protocol (e.g., `https://example.com`)
- **`ALLOWED_ORIGINS`**: CORS origins for your domain

### Quick Domain Setup

```bash
# Set up everything for your domain automatically
./scripts/setup-domain.sh your-domain.com
```

This script will:
- ✅ Update all configuration files with your domain
- ✅ Configure backend environment variables
- ✅ Update frontend production settings
- ✅ Modify nginx configuration
- ✅ Set up SSL certificate paths

---

## �🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React         │    │   Nginx         │    │   FastAPI       │
│   Frontend      │───▶│   Reverse       │───▶│   Backend       │
│                 │    │   Proxy         │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   SSL/TLS       │    │   PostgreSQL    │
                       │   Termination   │    │   Database      │
                       └─────────────────┘    └─────────────────┘
```

---

## 🚀 Quick Start

### Development Environment

```bash
# Clone repository
git clone https://github.com/your-username/url-changer.git
cd url-changer

# Backend setup with Makefile
cd backend
make setup          # Create venv and install dependencies
make dev             # Start development server

# Frontend setup (in new terminal)
cd frontend
npm install
npm run dev
```

### 🛠️ Backend Makefile Commands

The backend includes a comprehensive Makefile for streamlined development workflows:

#### 📋 **Available Commands**
```bash
make help           # Show all available commands with descriptions
```

#### 🔧 **Setup & Installation**
```bash
make setup          # Create virtual environment and install dev dependencies
make install        # Install/update development dependencies (assumes venv exists)
make install-prod   # Install production dependencies (includes PostgreSQL support)
make update-deps    # Update all dependencies to latest versions
make reset          # Clean everything and setup fresh environment
```

#### 🚀 **Development Server**
```bash
make dev            # Run development server with auto-reload (foreground)
make dev-bg         # Run development server in background
make debug          # Run server with debug logging enabled
make stop           # Stop background development server
make prod           # Run production server (4 workers)
```

#### 🧪 **Testing & Validation**
```bash
make test           # Basic API health check
make test-api       # Comprehensive API tests (shorten, custom codes, etc.)
make test-redirect  # Test URL redirect functionality with sample data
make quick-test     # Full test cycle: start server → test → stop server
```

#### 📊 **Monitoring & Status**
```bash
make status         # Show server status, database info, and running processes
make logs           # View server logs (tail -f server.log)
```

#### 🗄️ **Database Management**
```bash
make clean          # Clean database and temporary files (removes SQLite DB)
make backup         # Create timestamped database backup
make restore BACKUP=filename  # Restore database from backup file
```

#### 🔍 **Code Quality**
```bash
make lint           # Check code style with flake8 (auto-installs if missing)
make format         # Format code with black (auto-installs if missing)  
make check          # Run all code quality checks
make requirements   # Generate/update requirements.txt from current environment
```

#### 🐳 **Docker Operations**
```bash
make docker-build   # Build Docker image for the backend
make docker-run     # Run Docker container (port 8000)
make docker-stop    # Stop and remove Docker container
```

#### 💡 **Usage Examples**

**Complete Development Setup:**
```bash
cd backend
make setup          # One-time setup
make dev-bg         # Start server in background
make test-api       # Verify everything works
make logs           # Monitor server activity
```

**Quick Development Workflow:**
```bash
make dev            # Start development server (Ctrl+C to stop)
# Edit code - server auto-reloads
# Test API in another terminal
```

**Testing Workflow:**
```bash
make quick-test     # Automated: start → test → stop
# or manually:
make dev-bg && sleep 2 && make test-api && make stop
```

**Production Deployment Prep:**
```bash
make install-prod   # Install with PostgreSQL support
make lint          # Check code quality
make backup        # Backup current data
make prod          # Start production server
```

### 🌐 Production Deployment

**Recommended**: Use Google Cloud Run with GitHub integration

```bash
# 1. Create your .env files manually
cp .env.example .env
cp .env.example .env.production

# 2. Connect GitHub to Google Cloud Console
# 3. Set up secrets in Google Secret Manager  
# 4. Deploy directly from GitHub

# That's it! Auto-deploy on every push.
```

**📖 Simple deployment guide**: [SIMPLE-DEPLOY.md](SIMPLE-DEPLOY.md)

---

## � Project Structure

```
```
url-changer/
├── backend/                    # FastAPI Backend
│   ├── main.py                # FastAPI application entry point
│   ├── database.py            # Database models and configuration
│   ├── requirements.txt       # Production dependencies
│   ├── Dockerfile            # Production container configuration
│   └── venv/                 # Python virtual environment
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── App.tsx           # Main React application
│   │   ├── URLShortener.tsx  # URL shortening interface
│   │   └── AuthForm.tsx      # Authentication form
│   ├── Dockerfile            # Production container configuration
│   └── package.json          # Node.js dependencies and scripts
│
├── .env.example              # Environment variables template
├── docker-compose.yml        # Development Docker setup
├── SIMPLE-DEPLOY.md         # � Simple deployment guide
└── README.md                # 📋 This documentation
```

Key Files:
• SIMPLE-DEPLOY.md - Simple Google Cloud deployment guide
• .env.example - Environment variables template
• Dockerfile (backend & frontend) - Production containers
```

---

## �🔧 Configuration

### Environment Variables

```bash
# Production Configuration
ENVIRONMENT=production
DOMAIN=your-domain.com                                    # Your domain name
BASE_URL=https://your-domain.com                          # Full URL with protocol  
DATABASE_URL=postgresql://user:pass@localhost/url_shortener

# Security
SECRET_KEY=your-super-secret-key
API_KEY=your-api-key

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### DNS Requirements

```
A     coventure.es         → YOUR_SERVER_IP
A     www.coventure.es     → YOUR_SERVER_IP
```

---

## �‍💻 Development Workflow

### First Time Setup
```bash
cd backend
make help           # See all available commands
make setup          # Create virtual environment and install dependencies
```

### Daily Development
```bash
# Option 1: Foreground (recommended for active development)
make dev            # Start server with auto-reload, Ctrl+C to stop

# Option 2: Background (for testing while doing other work)
make dev-bg         # Start in background
# ... do other work ...
make logs          # Check server activity
make stop          # Stop when done
```

### Testing Your Changes
```bash
# Quick health check
make test

# Comprehensive API testing
make test-api       # Tests URL creation, custom codes, etc.

# Test redirect functionality
make test-redirect  # Creates test URL and verifies redirect

# Full automated test cycle
make quick-test     # Starts server → runs tests → stops server
```

### Before Committing Code
```bash
make lint          # Check code style
make format        # Auto-format code
make backup        # Backup current database
```

### Database Management
```bash
# Clean slate for testing
make clean         # Removes database and temp files
make dev          # Creates fresh database on startup

# Backup important data
make backup       # Creates timestamped backup
make restore BACKUP=url_shortener.db.backup.20241225_143022  # Restore from backup
```

### Troubleshooting
```bash
make status       # Shows server status, database info, running processes
make logs         # View server logs
make stop         # Stop any running background servers
make reset        # Nuclear option: clean everything and start fresh
```

### Production Preparation
```bash
make install-prod # Install production dependencies (includes PostgreSQL)
make prod        # Test production server locally
```

---

## �📋 API Reference

### Authentication
All API endpoints require the `X-API-Key` header in production.

### Endpoints

#### `POST /api/shorten`
Create a shortened URL.

**Request:**
```json
{
  "url": "https://example.com/very/long/url",
  "custom_code": "my-link",
  "expires_at": "2024-12-31T23:59:59"
}
```

**Response:**
```json
{
  "id": 1,
  "original_url": "https://example.com/very/long/url",
  "short_code": "my-link",
  "short_url": "https://coventure.es/my-link",
  "created_at": "2024-01-01T12:00:00",
  "click_count": 0,
  "expires_at": "2024-12-31T23:59:59"
}
```

#### `GET /{short_code}`
Redirect to original URL and increment click count.

#### `GET /api/stats/{short_code}`
Get statistics for a shortened URL (requires API key).

#### `GET /api/health`
Health check endpoint for monitoring.

#### `GET /api/metrics`
System metrics and usage statistics (requires API key).

---

## 🛡️ Security Features

### Production Security
- **🔐 HTTPS Only**: SSL/TLS encryption for all communications
- **🔑 API Authentication**: Secure API key-based authentication
- **🚦 Rate Limiting**: Configurable rate limits per IP address
- **🛡️ Input Validation**: Comprehensive validation of all inputs
- **🚫 CORS Protection**: Strict cross-origin resource sharing policies
- **🔒 Security Headers**: Complete security header implementation

### Content Security
- **🚫 Malicious URL Detection**: Blocks known malicious domains
- **🔍 URL Validation**: Prevents internal network access in production
- **⏰ Expiration Support**: Time-limited short URLs
- **📊 Analytics**: Click tracking without user identification

---

## 📊 Monitoring & Observability

### Health Monitoring
```bash
# Basic health check
GET /api/health

# Detailed metrics (requires API key)
GET /api/metrics
```

### Logging
- **📝 Structured Logging**: JSON-formatted logs for easy parsing
- **🚨 Error Tracking**: Integration with Sentry for error monitoring
- **📈 Performance Metrics**: Request timing and database performance
- **🔍 Audit Logging**: All API operations logged for security

### Metrics Available
- Total URLs created
- Total clicks/redirects
- Recent activity (24h)
- Database performance
- API response times

---

## 🐳 Docker Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Services
- **app**: FastAPI backend application
- **postgres**: PostgreSQL database with connection pooling
- **redis**: Redis for rate limiting and caching
- **nginx**: Reverse proxy with SSL termination

---

## 🔄 Maintenance

### Database Backup
```bash
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U urluser url_shortener > backup_$(date +%Y%m%d).sql
```

### Updates
```bash
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### SSL Certificate Renewal
```bash
# Automatic renewal via cron (configured during setup)
certbot renew --quiet
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Testing
```bash
# Test URL shortening
curl -X POST "https://coventure.es/api/shorten" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"url": "https://example.com"}'

# Test redirect
curl -I https://coventure.es/SHORTENED_CODE
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support & Documentation

- **📖 Deployment Guide**: [SIMPLE-DEPLOY.md](SIMPLE-DEPLOY.md)
- **🚨 Issues**: [GitHub Issues](https://github.com/your-username/url-shortener/issues)
- **📧 Contact**: admin@coventure.es

---

*Built with ❤️ for production reliability and security*