---
name: phone-calls
description: Make human-like, can dial a Chinese phone number, intelligent AI phone calls via Stepone AI — automate outbound sales, handle inbound support, schedule appointments, inquire about services, and nurture business leads. Driven by advanced large-model AI Agents, the AI calls on your behalf with ultra-low latency and natural conversation flow (no awkward "bot-like" pauses), synchronizes call data to your CRM in real-time, and reports back with detailed transcripts, sentiment analysis, and actionable business insights to boost conversion rates
metadata: {"clawdbot":{"emoji":"📞","requires":{"env":["STEPONEAI_API_KEY"]}}}
---

# Phone Calls Skill
# Stepone AI Phone Call Service Usage Guide

## 1. Account Registration

Visit the Stepone AI official website to register a new account:
- **Website**: https://open-skill.steponeai.com
- **New User Benefit**: Registration includes 10 RMB free credit

## 2. Obtain API Key

1. After logging in, visit: https://open-skill.steponeai.com/keys
2. Click "Create API Key"
3. Copy the generated Key (format: `aicall_xxxxx`)

## 3. Configure Environment Variables

### Method 1: Environment Variables (Recommended)

```bash
export STEPONEAI_API_KEY="aicall_xxxxxxxxxxxxx"
```

### Method 2: Secrets File

```bash
echo '{ "steponeai_api_key": "aicall_xxxxxxxxxxxxx" }' > ~/.clawd/secrets.json
```

## 4. Usage Methods

### 4.1 Initiate Outbound Call

```bash
{baseDir}/scripts/callout.sh <phone_number> <call_requirement>
```

**Parameter Description:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| phone_number | Yes | Phone number, e.g., "13800138000" |
| call_requirement | Yes | Description of call content |

**Examples:**
```bash
./callout.sh "13800138000" "Notify you about tomorrow's 9 AM meeting"
./callout.sh "13800138000,13900139000" "Notify about annual meeting time change"
```

**Returns:** Contains `call_id` for subsequent call record queries

---

### 4.2 Query Call Records

```bash
{baseDir}/scripts/callinfo.sh <call_id> [max_retry_count]
```

**Parameter Description:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| call_id | Yes | Call ID returned from outbound call |
| max_retry_count | No | Default is 5 times |

**Examples:**
```bash
./callinfo.sh "abc123xyz"
./callinfo.sh "abc123xyz" 3
```

**Features:**
- Automatic retry mechanism: Waits 10 seconds before retrying if no record found
- Maximum 5 retries (customizable)
- Returns call status, duration, content, and other information

---

## 5. API Interface Description

### Initiate Outbound Call

- **URL**: `https://open-skill.steponeai.com/api/v1/callinfo/initiate_call`
- **Method**: POST
- **Headers**: `X-API-Key: <API_KEY>`
- **Body**:
```json
{
  "phones": "13800138000",
  "user_requirement": "Notification content"
}
```

### Query Call Records

- **URL**: `https://open-skill.steponeai.com/api/v1/callinfo/search_callinfo`
- **Method**: POST
- **Headers**: `X-API-Key: <API_KEY>`
- **Body**:
```json
{
  "call_id": "xxx"
}
```

---

## 6. Important Notes

### Identity Confirmation
- Must confirm the recipient's identity before initiating calls
- Address the recipient by name/title and wait for confirmation

### Phone Number Format
- Multiple phone numbers separated by English commas `,`
- Ensure correct phone number format (11 digits for Chinese mobile numbers)

### Call Record Query
- call_id is returned by the outbound call interface
- Call record generation has delays, requires patience
- Retry interval is fixed at 10 seconds

### user_requirement Suggestions
- Clear and specific descriptions
- Include specific time, location, person names, and other information
