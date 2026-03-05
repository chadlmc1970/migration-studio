#!/bin/bash
# Deploy Migration Studio to Render with Neon Database

echo "🚀 Deploying Migration Studio to Render"
echo "========================================="

cd ~/migration_studio || exit 1

# Check git status
echo "📊 Checking git status..."
git status

# Add all changes
echo "📦 Staging changes..."
git add .

# Commit changes
echo "💾 Committing fixes..."
git commit -m "Fix: Update API endpoint and Neon database connection

- Frontend now points to correct API: migration-studio-api.onrender.com
- Backend configured with Neon PostgreSQL connection
- CORS updated for production domain
- Added ANTHROPIC_API_KEY support for AI enhancements
- Fixed 'Failed to fetch' error

Resolves deployment issues and ensures stable production operation."

# Push to GitHub (Render watches this repo)
echo "🚢 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "📋 Next steps:"
echo "1. Go to Render Dashboard: https://dashboard.render.com"
echo "2. Find 'migration-studio-api' service"
echo "3. Verify DATABASE_URL is set to your Neon connection string"
echo "4. Optionally set ANTHROPIC_API_KEY for AI enhancements"
echo "5. Wait for build to complete (~3-5 minutes)"
echo "6. Check https://migration-studio-pqor.onrender.com"
echo ""
echo "🔗 Your Neon Database:"
echo "   Host: ep-dark-hill-aiwdm4cf-pooler.c-4.us-east-1.aws.neon.tech"
echo "   Database: neondb"
echo ""
