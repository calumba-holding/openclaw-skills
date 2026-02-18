#!/bin/bash

# Openclaw Skill: Discogs Price Search
# Based on Anthropic agent skill standard

# Check if DISCOGS_TOKEN is set
if [ -z "$DISCOGS_TOKEN" ]; then
    echo '{"error": "DISCOGS_TOKEN environment variable is not set. Please set it to use this skill."}'
    exit 1
fi

# Read input from stdin
read -r INPUT_JSON

# Extract query from JSON input
QUERY=$(echo "$INPUT_JSON" | jq -r '.query // empty')

if [ -z "$QUERY" ]; then
    echo '{"error": "Query parameter is missing in input JSON. Please provide a query string."}'
    exit 1
fi

# URL encode the query using jq
ENCODED_QUERY=$(echo "$QUERY" | jq -R -r @uri)

# Step 1: Search for the release
# We search specifically for Vinyl format releases
SEARCH_URL="https://api.discogs.com/database/search?q=${ENCODED_QUERY}&type=release&format=Vinyl"

# Perform search with User-Agent and Authorization headers
SEARCH_RESULT=$(curl -s -H "User-Agent: OpenclawSkill/1.0" -H "Authorization: Discogs token=${DISCOGS_TOKEN}" "$SEARCH_URL")

# Extract the first release ID and details
RELEASE_ID=$(echo "$SEARCH_RESULT" | jq -r '.results[0].id // empty')
RELEASE_TITLE=$(echo "$SEARCH_RESULT" | jq -r '.results[0].title // "Unknown Title"')
RELEASE_YEAR=$(echo "$SEARCH_RESULT" | jq -r '.results[0].year // "Unknown Year"')

if [ -z "$RELEASE_ID" ]; then
    echo "{\"error\": \"No vinyl release found for query: '$QUERY'. Please try a more specific search term.\"}"
    exit 0
fi

# Step 2: Get Price Suggestions
# This endpoint provides suggested prices based on condition
PRICE_URL="https://api.discogs.com/marketplace/price_suggestions/${RELEASE_ID}"
PRICE_RESULT=$(curl -s -H "User-Agent: OpenclawSkill/1.0" -H "Authorization: Discogs token=${DISCOGS_TOKEN}" "$PRICE_URL")

# Extract Prices mapping conditions to Low, Median, High
# Low -> Good (G) or Good Plus (G+)
# Median -> Very Good Plus (VG+)
# High -> Mint (M) or Near Mint (NM or M-)

LOW=$(echo "$PRICE_RESULT" | jq -r '."Good (G)".value // ."Good Plus (G+)".value // "N/A"')
MEDIAN=$(echo "$PRICE_RESULT" | jq -r '."Very Good Plus (VG+)".value // ."Very Good (VG)".value // "N/A"')
HIGH=$(echo "$PRICE_RESULT" | jq -r '."Mint (M)".value // ."Near Mint (NM or M-)".value // "N/A"')
CURRENCY=$(echo "$PRICE_RESULT" | jq -r '."Very Good Plus (VG+)".currency // "USD"')

# Construct JSON Output
# Using jq -n to create JSON object safely
jq -n \
    --arg release_id "$RELEASE_ID" \
    --arg title "$RELEASE_TITLE" \
    --arg year "$RELEASE_YEAR" \
    --arg low "$LOW" \
    --arg median "$MEDIAN" \
    --arg high "$HIGH" \
    --arg currency "$CURRENCY" \
    '{
        release_id: $release_id,
        title: $title,
        year: $year,
        prices: {
            low: $low,
            median: $median,
            high: $high,
            currency: $currency
        }
    }'

