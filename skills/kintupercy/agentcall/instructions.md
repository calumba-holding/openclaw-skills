# AgentCall — Phone Numbers for AI Agents

You have access to the AgentCall API for phone numbers, SMS, voice calls, and AI voice calls. Inbound and outbound calls can both be answered or initiated by an OpenAI Realtime voice agent.

## Authentication

All authenticated requests require: `Authorization: Bearer <AGENTCALL_API_KEY>`

The API key is available in the `AGENTCALL_API_KEY` environment variable.

## Base URL

`https://api.agentcall.co`

For a complete plain-text API reference: `GET https://api.agentcall.co/llms.txt` (no auth required).

## Phone Numbers

**Provision a number:**
```
POST /v1/numbers/provision
Body: { "type": "local", "country": "US", "label": "my-agent" }
Types: local ($2/mo), tollfree ($2.50/mo), mobile ($2/mo), sim ($8/mo, Pro only)
Response: { "id": "num_xxx", "number": "+12125551234", "type": "local", ... }
```

**List numbers:**
```
GET /v1/numbers
Query: ?limit=20&country=US&type=local
```

**Get number details:**
```
GET /v1/numbers/:id
```

**Release a number (irreversible):**
```
DELETE /v1/numbers/:id
```

## Inbound AI Voice (Pro plan, $0.40/min, US and Canada numbers only)

Configure a phone number so incoming calls are answered autonomously by an OpenAI Realtime voice agent. The AI follows the system prompt you set.

**Configure inbound AI on a number:**
```
POST /v1/numbers/:numberId/inbound-config
Body: {
  "mode": "ai",
  "systemPrompt": "You are the front desk for Acme Plumbing. Greet the caller warmly, take their name and a brief description of the issue, then say someone will call back within 24 hours.",
  "voice": "shimmer",
  "firstMessage": "Hi, thanks for calling Acme Plumbing. How can I help?",
  "maxDurationSecs": 300
}
```

**Get current inbound config:**
```
GET /v1/numbers/:numberId/inbound-config
```

**Disable inbound AI (calls hang up at carrier):**
```
DELETE /v1/numbers/:numberId/inbound-config
```

## Browse Voices and Prompt Templates (no auth)

Both endpoints are public — call them before configuring AI voice to avoid hallucinated business details and to pick a voice that fits the use case.

**List the 8 voices with samples:**
```
GET /v1/calls/voices
Returns: { voices: [{ id, name, trait, description, bestFor, sampleUrl }, ...], defaultVoice: "shimmer" }
```

**List ready-made prompt templates:**
```
GET /v1/calls/prompt-templates
Returns 5 templates with [BRACKETED] placeholders to fill in:
- receptionist (Front Desk) — recommends shimmer voice
- lead-qualifier (Sales, BANT-style) — coral
- appointment-booker — sage
- customer-support (FAQ Deflection) — ash
- call-screener (Anti-Spam) — verse
Each entry includes: id, title, description, recommendedVoice, maxDurationSecs, firstMessage, systemPrompt.
```

For a comprehensive prompt-writing guide: https://agentcall.co/docs/voice-prompts

## SMS

**Send SMS:**
```
POST /v1/sms/send
Body: { "from": "num_xxx", "to": "+14155551234", "body": "Hello!" }
"from" can be a number ID or E.164 phone string
```

**Get inbox:**
```
GET /v1/sms/inbox/:numberId
Query: ?limit=20&otpOnly=true
```

**Get a specific message:**
```
GET /v1/sms/:messageId
```

**Wait for OTP code (long-polls up to 60 seconds):**
```
GET /v1/sms/otp/:numberId
Query: ?timeout=60000
Response: { "otp": "482913", "message": { ... } }
```

## Outbound Voice Calls

**Start a standard outbound call:**
```
POST /v1/calls/initiate
Body: { "from": "num_xxx", "to": "+14155551234", "record": false }
```

**Start an outbound AI voice call (Pro plan, $0.40/min):**
The AI handles the entire conversation autonomously based on your systemPrompt.
```
POST /v1/calls/ai
Body: {
  "from": "num_xxx",
  "to": "+14155551234",
  "systemPrompt": "You are calling to schedule a dentist appointment for Tuesday afternoon.",
  "voice": "shimmer",
  "firstMessage": "Hi, I'd like to schedule an appointment please.",
  "maxDurationSecs": 600
}
```

Voices (default: shimmer; preview each via GET /v1/calls/voices):
- shimmer: bright, energetic — recommended starting point (default)
- sage: calm, authoritative, confident — healthcare, finance, advisory
- ash: warm, conversational — customer service, support lines
- ballad: expressive, melodic — engaging, narrative conversations
- coral: clear, professional — B2B calls, sales
- echo: resonant, deep — formal inquiries, executive comms
- verse: smooth, articulate — premium/luxury, executive communication
- alloy: neutral, balanced — generic notifications, IVR-style flows

**List call history:**
```
GET /v1/calls
Query: ?limit=20
```

**Get call details:**
```
GET /v1/calls/:callId
```

**Get AI call transcript:**
```
GET /v1/calls/:callId/transcript
Response: { "entries": [{ "role": "ai" | "human", "text": "...", "timestamp": "..." }], "summary": "...", "duration": 111 }
```

**Hang up an active call:**
```
POST /v1/calls/:callId/hangup
```

## Webhooks

**Register a webhook:**
```
POST /v1/webhooks
Body: { "url": "https://example.com/hook", "events": ["sms.inbound", "sms.otp", "call.status"] }
Events: sms.inbound, sms.otp, call.inbound, call.ringing, call.status, call.recording, call.transcript, number.released
```

**List webhooks:**
```
GET /v1/webhooks
```

**Rotate webhook secret:**
```
POST /v1/webhooks/:id/rotate
```

**Delete a webhook:**
```
DELETE /v1/webhooks/:id
```

## Usage & Billing

**Get usage breakdown:**
```
GET /v1/usage
Query: ?period=2026-04
```

Pricing (per use, Pro plan):
- SMS outbound: $0.015/msg
- SMS inbound: $0.008/msg
- Voice (standard outbound): $0.035/min
- Voice (standard inbound): $0.015/min
- AI voice (outbound): $0.40/min
- AI voice (inbound): $0.40/min
- Call recording: $0.01/min

## Phone Number Format

All phone numbers must be E.164: `+{country code}{number}`, e.g. `+14155551234`

## Common Workflows

### Set up an AI receptionist on a phone number
1. `POST /v1/numbers/provision` with `{ "type": "local" }` — get a number
2. `GET /v1/calls/prompt-templates` — pick a template (e.g. "receptionist")
3. Replace `[BRACKETED]` placeholders with the customer's real business details
4. `POST /v1/numbers/:numberId/inbound-config` with `{ "mode": "ai", "systemPrompt": "...", "voice": "shimmer", "firstMessage": "..." }`
5. Anyone who calls the number is now answered by the AI agent
6. `GET /v1/calls` to see incoming call history; `GET /v1/calls/:callId/transcript` for transcripts

### Test your app's SMS verification (QA)
1. `POST /v1/numbers/provision` with `{ "type": "local" }` — get a test number
2. Enter the number into your staging app's verification form
3. `GET /v1/sms/otp/:numberId?timeout=60000` — wait for the verification code
4. Assert the code arrives and your app accepts it
5. `DELETE /v1/numbers/:id` — release the test number

### Make an outbound AI voice call
1. `POST /v1/numbers/provision` with `{ "type": "local" }` — get a number (if you don't have one)
2. `POST /v1/calls/ai` with `{ "from": "num_xxx", "to": "+1...", "systemPrompt": "..." }` — start the call
3. Wait for the call to complete
4. `GET /v1/calls/:callId/transcript` — get the full conversation transcript

## Error Codes
- **401**: Invalid or missing API key
- **402 payment_method_required**: Add a card before configuring billable features (returns `setupUrl` to Stripe Checkout)
- **403 plan_limit_voice_ai**: Inbound/outbound AI voice requires Pro plan ($19.99/mo)
- **403 plan_limit_***: Other plan limits — upgrade at agentcall.co/dashboard
- **400 carrier_not_supported**: Inbound AI voice is only supported on US and Canada numbers
- **404**: Resource not found
- **422**: Validation error (check request body)
- **429**: Rate limit exceeded (100 req/min global; per-route limits on expensive endpoints)
- **503 voice_ai_unavailable**: Server-side OpenAI key issue — retry later
