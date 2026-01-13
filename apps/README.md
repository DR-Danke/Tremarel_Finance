# Finance Tracker Deployment Guide

This guide covers deploying the Finance Tracker application to production using Vercel (frontend), Render (backend), and Supabase (database).

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Vercel      │────▶│     Render      │────▶│    Supabase     │
│   (Frontend)    │     │    (Backend)    │     │   (PostgreSQL)  │
│                 │     │                 │     │                 │
│  React + Vite   │     │  FastAPI + JWT  │     │   Direct Conn   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Prerequisites

Before deploying, ensure you have accounts on:
- [Vercel](https://vercel.com) - Frontend hosting
- [Render](https://render.com) - Backend hosting
- [Supabase](https://supabase.com) - PostgreSQL database

## 1. Database Setup (Supabase)

### Create Project

1. Log in to [Supabase Dashboard](https://app.supabase.com)
2. Click "New Project"
3. Enter project details:
   - Name: `finance-tracker`
   - Database Password: Generate a strong password (save it!)
   - Region: Choose closest to your users
4. Wait for project to initialize

### Get Connection String

1. Go to Project Settings > Database
2. Under "Connection string", select "URI"
3. Copy the connection string
4. Replace `[YOUR-PASSWORD]` with your database password

Example:
```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

### Run Schema Migration

1. Go to SQL Editor in Supabase
2. Run the schema from `Server/database/schema.sql`

## 2. Backend Deployment (Render)

### Create Web Service

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click "New" > "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `finance-tracker-api`
   - **Root Directory**: `apps/Server`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Starter (or higher)

### Configure Environment Variables

Add the following environment variables in Render:

| Variable | Value | Notes |
|----------|-------|-------|
| `PYTHON_VERSION` | `3.11.9` | CRITICAL for compatibility |
| `DATABASE_URL` | `postgresql://...` | From Supabase |
| `JWT_SECRET_KEY` | (auto-generate) | Use Render's generate feature |
| `JWT_ALGORITHM` | `HS256` | |
| `JWT_EXPIRE_MINUTES` | `1440` | 24 hours |
| `CORS_ORIGINS` | `["https://your-app.vercel.app"]` | Update after Vercel deploy |
| `APP_NAME` | `Finance Tracker API` | |
| `DEBUG` | `false` | |

### Deploy

1. Click "Create Web Service"
2. Wait for deployment to complete
3. Note your backend URL: `https://finance-tracker-api.onrender.com`
4. Verify health check: `https://finance-tracker-api.onrender.com/api/health`

## 3. Frontend Deployment (Vercel)

### Import Project

1. Log in to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" > "Project"
3. Import your GitHub repository

### Configure Build Settings

1. **Root Directory**: `apps/Client`
2. **Framework Preset**: Vite
3. **Build Command**: `npm run build`
4. **Output Directory**: `dist`

### Configure Environment Variables

Add the following environment variable:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://finance-tracker-api.onrender.com/api` |
| `VITE_APP_NAME` | `Finance Tracker` |

### Deploy

1. Click "Deploy"
2. Wait for build to complete
3. Note your frontend URL: `https://your-app.vercel.app`

## 4. Post-Deployment Configuration

### Update Backend CORS

After deploying the frontend, update the backend CORS setting:

1. Go to Render Dashboard > Your Service > Environment
2. Update `CORS_ORIGINS`:
   ```
   ["https://your-app.vercel.app"]
   ```
3. Save and redeploy

### Verify Deployment

Run through this checklist:

- [ ] Frontend loads at Vercel URL
- [ ] Backend health check responds: `/api/health`
- [ ] API documentation accessible: `/docs`
- [ ] User registration works
- [ ] User login returns JWT token
- [ ] Protected routes require authentication
- [ ] CORS allows frontend-backend communication

## Environment Variables Reference

### Frontend (Vercel)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes | Backend API base URL |
| `VITE_APP_NAME` | No | Application display name |

### Backend (Render)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `JWT_SECRET_KEY` | Yes | Secret for JWT signing (min 32 chars) |
| `JWT_ALGORITHM` | No | JWT algorithm (default: HS256) |
| `JWT_EXPIRE_MINUTES` | No | Token expiry (default: 1440) |
| `CORS_ORIGINS` | Yes | JSON array of allowed origins |
| `PYTHON_VERSION` | Yes | Must be 3.11.9 for Render |
| `APP_NAME` | No | API display name |
| `DEBUG` | No | Debug mode (default: false) |

## Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:
1. Verify `CORS_ORIGINS` is a valid JSON array
2. Ensure the frontend URL matches exactly (including https://)
3. Redeploy the backend after updating CORS

### Database Connection Errors

If the backend can't connect to the database:
1. Verify the `DATABASE_URL` format is correct
2. Check if Supabase project is active
3. Ensure the password doesn't contain special characters that need URL encoding

### Build Failures on Render

If the backend build fails:
1. Ensure `PYTHON_VERSION=3.11.9` is set
2. Check `requirements.txt` for missing dependencies
3. Review build logs for specific errors

### Frontend API Errors

If the frontend can't reach the backend:
1. Check browser console for the actual error
2. Verify `VITE_API_URL` points to the correct backend URL
3. Ensure the URL ends with `/api` (not a trailing slash)

## Local Development

For local development, copy the sample environment files:

```bash
# Frontend
cp apps/Client/.env.sample apps/Client/.env

# Backend
cp apps/Server/.env.sample apps/Server/.env
```

Update the values as needed for your local environment.
