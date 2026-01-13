# Deployment Configuration

**ADW ID:** dcb3fc76
**Date:** 2026-01-13
**Specification:** specs/issue-32-adw-dcb3fc76-sdlc_planner-deployment-config.md

## Overview

This chore finalizes the deployment configuration for the Finance Tracker application, preparing both the frontend (Vercel) and backend (Render) for production deployment. It includes comprehensive environment variable documentation, Render blueprint configuration, and a detailed deployment guide.

## What Was Built

- **Render Blueprint Configuration**: Production-ready `render.yaml` with service definition, health checks, and environment variable placeholders
- **Enhanced Environment Variable Documentation**: Comprehensive `.env.sample` files for both Client and Server with production examples
- **Deployment Guide**: Step-by-step deployment documentation covering Vercel, Render, and Supabase setup
- **CORS Configuration Documentation**: Clear guidance on JSON array format for CORS origins

## Technical Implementation

### Files Modified

- `apps/Client/.env.sample`: Enhanced with comprehensive documentation, section headers, and production URL placeholders
- `apps/Server/.env.sample`: Expanded with detailed comments, section headers, and examples for development and production configurations
- `apps/Server/render.yaml`: New file - Render blueprint configuration with service definition, build/start commands, health check path, and environment variables
- `apps/README.md`: New file - Comprehensive deployment guide with architecture overview, step-by-step instructions, and troubleshooting section

### Key Changes

- **Render Blueprint**: Defines a `finance-tracker-api` web service with Python 3.11.9 runtime, proper build/start commands, and health check at `/api/health`
- **Environment Variables**: Documented all required variables with clear examples for both development and production environments
- **CORS Format**: Explicitly documented JSON array format requirement (`["origin1","origin2"]`) for CORS_ORIGINS
- **Deployment Architecture**: Documented the three-tier architecture (Vercel → Render → Supabase) with visual diagram

## How to Use

1. **Database Setup (Supabase)**:
   - Create a Supabase project
   - Run schema migration from `Server/database/schema.sql`
   - Copy the connection string

2. **Backend Deployment (Render)**:
   - Connect GitHub repository
   - Set root directory to `apps/Server`
   - Configure environment variables (especially `PYTHON_VERSION=3.11.9`)
   - Deploy and note the backend URL

3. **Frontend Deployment (Vercel)**:
   - Connect GitHub repository
   - Set root directory to `apps/Client`
   - Set `VITE_API_URL` to the Render backend URL
   - Deploy and note the frontend URL

4. **Post-Deployment**:
   - Update `CORS_ORIGINS` in Render with the Vercel frontend URL
   - Verify health check and API documentation endpoints

## Configuration

### Frontend Environment Variables (Vercel)

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API base URL (e.g., `https://finance-tracker-api.onrender.com/api`) |
| `VITE_APP_NAME` | Application display name |

### Backend Environment Variables (Render)

| Variable | Description |
|----------|-------------|
| `PYTHON_VERSION` | Must be `3.11.9` (critical for compatibility) |
| `DATABASE_URL` | Supabase PostgreSQL connection string |
| `JWT_SECRET_KEY` | Secret for JWT signing (min 32 chars) |
| `JWT_ALGORITHM` | JWT algorithm (`HS256`) |
| `JWT_EXPIRE_MINUTES` | Token expiry in minutes |
| `CORS_ORIGINS` | JSON array of allowed origins |

## Testing

- Frontend build verification: `cd apps/Client && npm run build`
- Backend tests: `cd apps/Server && python -m pytest tests/ -v`
- Post-deployment: Verify `/api/health` endpoint and `/docs` API documentation

## Notes

- **Python Version**: Render must use `PYTHON_VERSION=3.11.9` for compatibility with project dependencies
- **CORS Format**: CORS_ORIGINS must be valid JSON array format - the backend's `settings.py` parses this correctly
- **Health Check**: Backend health endpoint at `/api/health` is used by Render for service monitoring
- **No Code Changes**: This chore only modifies configuration files and documentation; CORS handling was already correctly implemented
