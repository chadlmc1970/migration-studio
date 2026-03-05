#!/bin/bash
# Verify the frontend deployment is working

echo "🔍 Checking if deployment is complete..."
echo ""

# Check if the API URL is in the compiled JavaScript
echo "1️⃣ Checking compiled JavaScript for API URL..."
COMPILED=$(curl -s https://migration-studio-pqor.onrender.com/_next/static/chunks/app/app/page.js 2>/dev/null | grep -o 'migration-studio-api.onrender.com' | head -1)

if [ -n "$COMPILED" ]; then
    echo "   ✅ FIXED! Found correct API URL in compiled code"
else
    LOCALHOST=$(curl -s https://migration-studio-pqor.onrender.com/_next/static/chunks/app/app/page.js 2>/dev/null | grep -o 'localhost:8000' | head -1)
    if [ -n "$LOCALHOST" ]; then
        echo "   ⏳ Still using old build (localhost found)"
        echo "   💡 Wait for Render deployment to complete..."
    else
        echo "   ⚠️  Could not fetch compiled code - deployment may be in progress"
    fi
fi

echo ""
echo "2️⃣ Testing backend API..."
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://migration-studio-api.onrender.com/api/universes)
if [ "$API_STATUS" = "200" ]; then
    echo "   ✅ Backend API working (HTTP $API_STATUS)"
    UNIVERSE_COUNT=$(curl -s https://migration-studio-api.onrender.com/api/universes | jq '. | length')
    echo "   📊 Found $UNIVERSE_COUNT universes"
else
    echo "   ❌ Backend API error (HTTP $API_STATUS)"
fi

echo ""
echo "3️⃣ Testing frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://migration-studio-pqor.onrender.com)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "   ✅ Frontend responding (HTTP $FRONTEND_STATUS)"
else
    echo "   ❌ Frontend error (HTTP $FRONTEND_STATUS)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -n "$COMPILED" ] && [ "$API_STATUS" = "200" ] && [ "$FRONTEND_STATUS" = "200" ]; then
    echo "🎉 ALL SYSTEMS GO! Open the app:"
    echo "   https://migration-studio-pqor.onrender.com/app/universes"
else
    echo "⏳ Deployment still in progress..."
    echo "   Run this script again in 1-2 minutes"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
