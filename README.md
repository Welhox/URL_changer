# URL Changer - Professional Link Management Service

<img width="1658" height="869" alt="URL Changer Interface" src="https://github.com/user-attachments/assets/3c175799-5d1e-40aa-8c62-acc7411d8ea0" />

> **A production-ready URL shortening service with Slack integration, analytics, and enterprise-grade security**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

---

## What is URL Changer?

URL Changer is a full-stack link management platform I built to explore production-ready backend architecture and DevOps practices. While URL shorteners are a solved problem, building one from scratch let me work with interesting challenges: designing secure APIs, implementing rate limiting, deploying with Docker, and integrating with Slack's API.

---

## Why I Built This

I wanted hands-on experience with backend architecture, API security, database design, Slack integration, and DevOps workflows. This project demonstrates my ability to build production-grade services with proper error handling, monitoring, and deployment automation.

---

## Key Features

**Core Functionality**
- Custom short codes for memorable links
- Click analytics and usage tracking
- Expiration support for time-limited URLs
- Malicious URL detection

**Slack Bot Integration**
- User-specific URL collections (each Slack user maintains their own library)
- Slash commands: `/transmute`, `/urlstats`, `/urlremove`
- Rich formatted responses with click stats
- Proper signature verification and security

**Production Security**
- API key authentication
- Rate limiting (per-IP throttling)
- Input validation with Pydantic
- HTTPS with Let's Encrypt support
- Security headers (CORS, CSP)

**Developer Experience**
- Comprehensive Makefile with 25+ commands
- Automated testing and validation
- Database backup and restore
- Code quality tools

---

## Technical Stack

**Backend:** FastAPI, PostgreSQL, SQLAlchemy, Pydantic, Python 3.11+

**Frontend:** React, TypeScript, Tailwind CSS, Vite

**Infrastructure:** Docker, Nginx, Redis, Google Cloud Run ready

**Integrations:** Slack API, Let's Encrypt

---

## Architecture

The system consists of four main components:

**Frontend (React + TypeScript)** serves the user interface and handles form validation.

**Backend (FastAPI)** processes requests, manages the database, enforces rate limits, and handles Slack webhooks with comprehensive error handling and logging.

**Database (PostgreSQL)** stores URL mappings and analytics with proper indexing and connection pooling.

**Nginx** handles SSL termination, serves static files, and routes requests as a reverse proxy.

All services are containerized with Docker for consistent deployment.

---

## Developer Tooling

The Makefile provides organized commands for streamlined development:

**Setup & Installation**

- `make setup` - Initial environment setup
- `make install` - Install dependencies
- `make install-prod` - Production dependencies with PostgreSQL
- `make reset` - Clean slate

**Development**

- `make dev` - Start dev server with auto-reload
- `make dev-bg` - Run in background
- `make logs` - View server logs
- `make stop` - Stop background servers

**Testing**

- `make test` - Quick health check
- `make test-api` - Comprehensive API tests
- `make quick-test` - Automated test cycle

**Database**

- `make backup` - Create timestamped backup
- `make restore` - Restore from backup
- `make clean` - Remove database and temp files

**Code Quality**

- `make lint` - Check code style
- `make format` - Auto-format code
- `make check` - Run all quality checks

---

## Slack Bot

The Slack integration handles user-specific URL collections using Slack user IDs for isolation. Each workspace gets rate limiting to prevent abuse. Slash commands provide full URL management directly from Slack with rich formatted responses using Block Kit.

**Commands:**
- `/transmute <url> [custom_code]` - Create shortened URLs
- `/urlstats [short_code|all]` - View statistics
- `/urlremove <short_code>` - Delete URLs

---

## What I Learned

**API Design:** Structuring FastAPI applications with proper dependency injection, middleware, and error handling patterns.

**Database Optimization:** PostgreSQL indexing strategies, connection pooling, and query optimization.

**Security:** Multiple layers from input validation to rate limiting to API authentication. Understanding common vulnerabilities and prevention.

**Slack Integration:** Working with webhooks, slash commands, and OAuth flows with proper error handling.

**DevOps:** Creating reproducible deployment processes with Docker, configuring nginx, and automating tasks with Make.

---

## API Overview

- **POST /api/shorten** - Create shortened URLs with optional custom codes and expiration
- **GET /{short_code}** - Redirect to original URL and increment counter
- **GET /api/stats/{short_code}** - Retrieve analytics (authenticated)
- **POST /api/slack/events** - Slack webhook for slash commands
- **GET /api/health** - Health check for monitoring
- **GET /api/metrics** - System metrics (authenticated)

---

## Project Structure

The project is organized into backend and frontend components:

**Backend** contains the FastAPI application (main.py), database models (database.py), Slack integration (slack_bot.py), development tooling (Makefile), and container configuration (Dockerfile).

**Frontend** includes the React application with TypeScript, the main App component, URL shortener UI, and its own container setup.

**Root level** has docker-compose for multi-service orchestration and environment configuration template.

---

## About Me

I'm **Casimir Lundberg**, a full-stack developer with a background in aviation, based in Finland. I work with C/C++, TypeScript, React, Python, and modern web technologies. Currently seeking developer opportunities.

- Portfolio: [casimirlundberg.fi](https://casimirlundberg.fi)
- LinkedIn: [linkedin.com/in/caslun](https://linkedin.com/in/caslun)
- Email: mail@casimirlundberg.fi
- GitHub: [@Welhox](https://github.com/Welhox)

---

<div align="center">

**Built by 8**

*FastAPI • React • PostgreSQL • Docker • Slack API*

</div>
