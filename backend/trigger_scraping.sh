#!/bin/bash

# Configuration
API_URL="http://localhost:8000"
USERNAME="zchentou"
PASSWORD="asking9cliff-solace6mother"
FROM_DATE="2024-10-21"
TO_DATE="2024-10-27"
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

echo "🔄 Triggering scraping for ${SOURCE}..."
SCRAPING_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    "${API_URL}/api/analysis/trigger_scraping/?source=${SOURCE}&from_date=${FROM_DATE}&to_date=${TO_DATE}")

echo "📊 Scraping response:"
echo $SCRAPING_RESPONSE

# Check if response contains success message
if echo $SCRAPING_RESPONSE | grep -q "Scraping triggered successfully"; then
    echo "✅ Scraping job started successfully"
else
    echo "❌ Scraping may have failed. Please check the response above."
fi