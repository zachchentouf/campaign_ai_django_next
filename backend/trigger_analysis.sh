#!/bin/bash

# Configuration
API_URL="http://localhost:8000"
USERNAME="zchentou"
PASSWORD="asking9cliff-solace6mother"
FROM_DATE="2024-10-21"
SOURCE="newsapi"

echo "🔑 Getting authentication token..."
TOKEN_RESPONSE=$(curl -s -X POST "${API_URL}/api/token/" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"${USERNAME}\", \"password\": \"${PASSWORD}\"}")

# Extract access token using grep and cut (more portable than jq)
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Failed to get access token. Response was:"
    echo $TOKEN_RESPONSE
    exit 1
fi

echo "✅ Successfully obtained access token"

echo "🔄 Triggering analysis for ${SOURCE}..."
ANALYSIS_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    "${API_URL}/api/analysis/trigger_analysis/?source=${SOURCE}&week_start=${FROM_DATE}")

echo "📊 Analysis response:"
echo $ANALYSIS_RESPONSE

# Check if response contains success message
if echo $ANALYSIS_RESPONSE | grep -q "Analysis triggered successfully"; then
    echo "✅ Analysis job started successfully"
else
    echo "❌ Analysis may have failed. Please check the response above."
fi