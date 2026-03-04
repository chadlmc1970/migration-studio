# Migration to Production: Render + Neon

**Project**: Universe Migration Studio
**Goal**: Deploy to Render (hosting) + Neon (PostgreSQL database)
**Pattern**: Follow the same deployment strategy as CatchWeight project

---

## Current State

**Working locally at:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

**Tech Stack:**
- Frontend: Next.js 14, React, Tailwind CSS, TypeScript
- Backend: FastAPI, Python
- Current Storage: Filesystem (JSON files + logs)

**What Works:**
- ✅ Landing page with hero and features
- ✅ Dashboard with KPIs and event feed
- ✅ Analytics page with charts
- ✅ Universes list and detail pages
- ✅ File uploads and downloads
- ✅ Backend API fully functional

---

## Migration Plan

### Phase 1: Database Migration (Neon PostgreSQL)

**Current filesystem storage:**
- `~/pipeline/state/pipeline_state.json` → **universes** table
- `~/pipeline/events/events.log` → **events** table
- Run metadata → **runs** table
- Validation reports → **validation_reports** table
- Artifact tracking → **artifacts** table

**Schema created:** See `backend/schema.sql`

**Tasks:**
1. Create Neon database at https://neon.tech
2. Run schema.sql to create tables
3. Update backend to use SQLAlchemy ORM
4. Add database dependencies to requirements.txt:
   ```
   sqlalchemy
   psycopg2-binary
   alembic
   ```
5. Create database models in `backend/app/models/database.py`
6. Update all routes to query database instead of reading JSON files
7. Keep file upload/download functionality (still uses filesystem)

### Phase 2: Prepare for Deployment

**Add configuration files:**

1. **backend/.env.example**
   ```
   DATABASE_URL=postgresql://user:pass@host/dbname
   FRONTEND_URL=http://localhost:3000
   ENVIRONMENT=development
   ```

2. **backend/render.yaml** (Render blueprint)
   ```yaml
   services:
     - type: web
       name: migration-studio-api
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: DATABASE_URL
           sync: false
         - key: FRONTEND_URL
           sync: false
   ```

3. **.gitignore** updates
   ```
   .env
   venv/
   __pycache__/
   .next/
   node_modules/
   *.pyc
   .DS_Store
   ```

### Phase 3: GitHub Setup

1. Create repo: `github.com/chadlmc1970/migration-studio`
2. Initialize git:
   ```bash
   cd ~/migration_studio
   git init
   git add .
   git commit -m "Initial commit: Universe Migration Studio"
   git branch -M main
   git remote add origin https://github.com/chadlmc1970/migration-studio.git
   git push -u origin main
   ```

### Phase 4: Render Deployment

**Backend Service:**
1. Go to https://dashboard.render.com
2. New → Web Service
3. Connect GitHub repo
4. Settings:
   - Name: `migration-studio-api`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Instance Type: Free tier
5. Add environment variables:
   - `DATABASE_URL` → Neon connection string
   - `FRONTEND_URL` → (will be Render frontend URL)

**Frontend Service:**
1. New → Static Site
2. Connect same GitHub repo
3. Settings:
   - Name: `migration-studio`
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/out`
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` → Backend Render URL

### Phase 5: Post-Deployment

1. Update backend CORS to allow Render frontend URL
2. Test all endpoints
3. Verify file uploads work on Render
4. Check database connections
5. Monitor logs

---

## File Changes Required

### Backend Changes

**1. Add to requirements.txt:**
```
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.0
python-dotenv==1.0.0
```

**2. Create `backend/app/database.py`:**
- Database connection setup
- Session management
- SQLAlchemy Base

**3. Create `backend/app/models/database.py`:**
- Universe model
- Event model
- Run model
- ValidationReport model
- Artifact model

**4. Update `backend/app/api/routes.py`:**
- Replace file reads with database queries
- Keep file upload/download endpoints
- Add database session dependency

**5. Update `backend/app/main.py`:**
- Add database connection on startup
- Update CORS to use environment variable

### Frontend Changes

**1. Update `frontend/src/lib/api.ts`:**
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
```

**2. Add `frontend/next.config.js` output:**
```javascript
output: 'export', // For static export to Render
```

---

## Critical Notes

1. **Keep filesystem for uploaded files** - Don't move .unv/.unx files to database
2. **Pipeline engines stay local** - Parser, transform, validation engines run locally only
3. **CORS configuration** - Must allow both localhost and Render URLs
4. **Database migrations** - Use Alembic for schema changes
5. **Environment variables** - Never commit .env files

---

## Deployment Checklist

- [ ] Schema created in Neon
- [ ] Database dependencies added
- [ ] SQLAlchemy models created
- [ ] Routes updated to use database
- [ ] .env.example created
- [ ] .gitignore updated
- [ ] GitHub repo created and pushed
- [ ] Render backend service created
- [ ] Render frontend service created
- [ ] Environment variables configured
- [ ] CORS updated for production
- [ ] All endpoints tested
- [ ] Production URLs documented

---

## Production URLs (After Deployment)

- Frontend: `https://migration-studio.onrender.com`
- Backend: `https://migration-studio-api.onrender.com`
- Database: Neon connection string (in Render env vars)

---

## Reference: CatchWeight Deployment

Follow the same pattern as CatchWeight project:
- Remote: `github` → https://github.com/chadlmc1970/CatchWeight.git
- Frontend: https://catchweight-dashboard.onrender.com
- Backend: https://catchweight-api.onrender.com
- Database: Neon PostgreSQL

**Deployment command:**
```bash
git commit -m "description"
git push github main
# Render auto-deploys from main branch
```
