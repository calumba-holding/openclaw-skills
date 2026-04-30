#!/bin/bash
# CrawlHub Reseller Client - Request API Key
# Usage: ./request-api-key.sh <wallet> <signature> <message> <txHash>

WALLET="${1:-}"
SIGNATURE="${2:-}"
MESSAGE="${3:-}"
TX_HASH="${4:-}"

if [ -z "$WALLET" ] || [ -z "$SIGNATURE" ] || [ -z "$MESSAGE" ] || [ -z "$TX_HASH" ]; then
  echo "Usage: request-api-key.sh <wallet> <signature> <message> <txHash>"
  echo "Example: ./request-api-key.sh 0x742d... 0x1234... \"Request API Key...\" 0xabc..."
  exit 1
fi

curl -s -X POST http://localhost:3000/json-rpc \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"tasks/send\",
    \"params\": {
      \"message\": {
        \"role\": \"user\",
        \"parts\": [{
          \"type\": \"text\",
          \"text\": JSON.stringify({
            \"customerWallet\": \"$WALLET\",
            \"signature\": \"$SIGNATURE\",
            \"message\": \"$MESSAGE\",
            \"txHash\": \"$TX_HASH\"
          })
        }]
      }
    }
  }" | python3 -c "
import sys, json
d = json.load(sys.stdin)
result = d.get('result', {})
status = result.get('status', {})
if status.get('state') == 'completed':
    artifacts = result.get('artifacts', [])
    for a in artifacts:
        for p in a.get('parts', []):
            if p.get('type') == 'data':
                data = p.get('data', {})
                print('SUCCESS: API Key =', data.get('apiKey'))
                print('Expires:', data.get('expiresAt'))
else:
    msg = status.get('message', {})
    for p in msg.get('parts', []):
        print('ERROR:', p.get('text', 'Unknown error'))
"