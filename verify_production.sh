#!/bin/bash
# Verify Migration Studio Production Deployment

echo "🔍 Verifying Migration Studio Production Deployment"
echo "=================================================="
echo ""

# Check API health
echo "1️⃣  Testing API Health..."
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://migration-studio-api.onrender.com/health)
if [ "$API_RESPONSE" = "200" ]; then
    echo "   ✅ API is healthy (HTTP $API_RESPONSE)"
else
    echo "   ⚠️  API returned HTTP $API_RESPONSE (may still be deploying)"
fi
echo ""

# Check API root
echo "2️⃣  Testing API Root..."
API_ROOT=$(curl -s https://migration-studio-api.onrender.com/ | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
if [ "$API_ROOT" = "running" ]; then
    echo "   ✅ API service is running"
else
    echo "   ⚠️  API status: $API_ROOT"
fi
echo ""

# Check Frontend
echo "3️⃣  Testing Frontend..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://migration-studio-pqor.onrender.com)
if [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo "   ✅ Frontend is accessible (HTTP $FRONTEND_RESPONSE)"
else
    echo "   ⚠️  Frontend returned HTTP $FRONTEND_RESPONSE"
fi
echo ""

# Check API from Frontend perspective
echo "4️⃣  Testing API Endpoint from Frontend..."
UNIVERSES_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://migration-studio-api.onrender.com/api/universes)
if [ "$UNIVERSES_RESPONSE" = "200" ]; then
    echo "   ✅ Universes endpoint responding (HTTP $UNIVERSES_RESPONSE)"
else
    echo "   ⚠️  Universes endpoint returned HTTP $UNIVERSES_RESPONSE"
fi
echo ""

echo "=================================================="
echo "📋 Deployment Summary"
echo "=================================================="
echo ""
echo "🌐 Production URLs:"
echo "   Frontend: https://migration-studio-pqor.onrender.com"
echo "   Backend:  https://migration-studio-api.onrender.com"
echo "   Health:   https://migration-studio-api.onrender.com/health"
echo ""
echo "📊 Status:"
if [ "$API_RESPONSE" = "200" ] && [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo "   ✅ ALL SYSTEMS OPERATIONAL"
    echo ""
    echo "🎉 Your Migration Studio is live and working!"
else
    echo "   ⏳ Deployment in progress or issues detected"
    echo ""
    echo "💡 If services aren't responding:"
    echo "   1. Wait 2-3 minutes for Render to finish building"
    echo "   2. Check Render dashboard: https://dashboard.render.com"
    echo "   3. Ensure DATABASE_URL has your Neon password set"
    echo "   4. Check logs: migration-studio-api → Logs"
fi
echo ""
echo "🔗 Quick Links:"
echo "   Render Dashboard: https://dashboard.render.com"
echo "   GitHub Repo: https://github.com/chadlmc1970/migration-studio"
echo "   Neon Console: https://console.neon.tech"
echo ""
