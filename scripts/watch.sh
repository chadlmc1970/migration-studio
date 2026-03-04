#!/bin/bash
# Watch and auto-restart if webpack crashes

LOG_FILE="/tmp/migration_studio_frontend.log"
LAST_ERROR_TIME=0
ERROR_THRESHOLD=3

while true; do
    if grep -q "webpack_modules.*is not a function" "$LOG_FILE" 2>/dev/null; then
        CURRENT_TIME=$(date +%s)
        
        # Only restart if error is new (not same error repeated)
        if [ $((CURRENT_TIME - LAST_ERROR_TIME)) -gt 10 ]; then
            echo "⚠️  Webpack error detected! Auto-restarting..."
            LAST_ERROR_TIME=$CURRENT_TIME
            
            # Kill and clean restart
            lsof -ti:3001 | xargs kill -9 2>/dev/null
            cd /Users/I870089/migration_studio/frontend
            rm -rf .next node_modules/.cache
            npm run dev > "$LOG_FILE" 2>&1 &
            
            echo "✅ Frontend restarted"
        fi
    fi
    
    sleep 5
done
