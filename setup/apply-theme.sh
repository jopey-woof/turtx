#!/bin/bash
# Auto-apply turtle theme via HA API

echo "🎨 Auto-applying turtle_dark theme..."

# Get auth token from env
if [ -z "$KIOSK_TOKEN" ]; then
    echo "❌ KIOSK_TOKEN not found in environment"
    exit 1
fi

# Apply theme via API
curl -X POST \
  -H "Authorization: Bearer $KIOSK_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"theme\": \"turtle_dark\"}" \
  http://127.0.0.1:8123/api/services/frontend/set_theme

echo "✅ Turtle theme applied!"
