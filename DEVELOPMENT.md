# Development Guide

## Starting the Dev Environment

**Always use the dev script to avoid webpack cache corruption:**

```bash
cd ~/migration_studio
./scripts/dev.sh
```

This script automatically:
- Kills old processes on ports 8000/3000/3001
- Clears Next.js build caches (`.next` and `node_modules/.cache`)
- Starts backend on port 8000
- Starts frontend on port 3001
- Provides log file locations

## Why This Matters

**Problem**: Next.js webpack cache can become corrupted during development, causing errors like:
- `TypeError: __webpack_modules__[moduleId] is not a function`
- Clicking buttons does nothing
- Pages freeze or spin indefinitely

**Solution**: The dev script clears caches before every start, preventing corruption.

## Manual Commands (if needed)

```bash
# Stop servers
lsof -ti:8000 | xargs kill
lsof -ti:3001 | xargs kill

# Clear caches manually
cd ~/migration_studio/frontend
rm -rf .next node_modules/.cache

# Start backend
cd ~/migration_studio/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend
cd ~/migration_studio/frontend
npm run dev
```

## Configuration Changes

**next.config.js** now disables webpack caching in dev mode:
```javascript
webpack: (config, { dev }) => {
  if (dev) {
    config.cache = false  // Prevents corruption
  }
  return config
}
```

This trades slightly slower hot reloads for stability.

## Logs

- Backend: `tail -f /tmp/migration_studio_backend.log`
- Frontend: `tail -f /tmp/migration_studio_frontend.log`

## URLs

- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
