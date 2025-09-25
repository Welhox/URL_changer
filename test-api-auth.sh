#!/bin/bash

# Test script to verify API key authentication
echo "🧪 Testing API Key Authentication"
echo "================================="

API_KEY="JCffTVvDzYiOUqTFrJmTNAMa9ql6kcvC"
BASE_URL="http://localhost:8000"

echo ""
echo "1. Testing health endpoint (no API key required):"
curl -s "$BASE_URL/api/health" | jq .

echo ""
echo "2. Testing shorten endpoint without API key (should work in dev mode):"
curl -s -X POST "$BASE_URL/api/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/test-no-key"}' | jq .

echo ""
echo "3. Testing shorten endpoint with API key:"
curl -s -X POST "$BASE_URL/api/shorten" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"url": "https://github.com/test-with-key"}' | jq .

echo ""
echo "4. Testing shorten endpoint with wrong API key:"
curl -s -X POST "$BASE_URL/api/shorten" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: wrong-key" \
  -d '{"url": "https://github.com/test-wrong-key"}' | jq .

echo ""
echo "✅ API Key authentication test completed!"