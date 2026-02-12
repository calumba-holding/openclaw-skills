#!/usr/bin/env node
/**
 * RentAPerson Webhook Bridge - SIMPLIFIED
 * 
 * What it does:
 * 1. Receives webhook from RentAPerson
 * 2. Adds API key to the message
 * 3. Forwards to OpenClaw
 * 4. Returns OpenClaw's response
 * 
 * That's it. No complex session management.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

// Load credentials
const credPath = path.join(__dirname, '..', 'rentaperson-agent.json');
let credentials = {};

if (fs.existsSync(credPath)) {
  try {
    credentials = JSON.parse(fs.readFileSync(credPath, 'utf8'));
  } catch (e) {
    console.error('[bridge] Failed to load credentials:', e.message);
    process.exit(1);
  }
}

const API_KEY = credentials.apiKey || process.env.RENTAPERSON_API_KEY;
const AGENT_ID = credentials.agentId || process.env.RENTAPERSON_AGENT_ID;
const AGENT_NAME = credentials.agentName || process.env.RENTAPERSON_AGENT_NAME;
// Prefer apiBase from webhook payload (so dev.rentaperson.ai sends correct origin); fallback to credentials/env
const DEFAULT_API_BASE = credentials.apiBase || process.env.RENTAPERSON_API_BASE || 'https://rentaperson.ai';
const OPENCLAW_URL = process.env.OPENCLAW_URL || 'http://127.0.0.1:18789';
const OPENCLAW_TOKEN = credentials.openclawToken || process.env.OPENCLAW_TOKEN || '';
const BRIDGE_PORT = parseInt(process.env.BRIDGE_PORT || '3001', 10);

if (!API_KEY) {
  console.error('[bridge] ERROR: RENTAPERSON_API_KEY required');
  console.error('[bridge] Set it in rentaperson-agent.json or environment variable');
  process.exit(1);
}

console.log(`[bridge] Starting...`);
console.log(`[bridge] Default API Base: ${DEFAULT_API_BASE}`);
console.log(`[bridge] OpenClaw: ${OPENCLAW_URL}`);
console.log(`[bridge] Agent: ${AGENT_NAME || AGENT_ID || 'unknown'}`);

function buildMessage(payload) {
  const event = payload.event;
  const apiBase = payload.apiBase && payload.apiBase.startsWith('http') ? payload.apiBase.replace(/\/+$/, '') : DEFAULT_API_BASE;
  const skillUrl = `${apiBase}/skill.md`;
  
  let task;
  if (event === 'message.received') {
    const convId = payload.conversationId || '';
    const userId = payload.humanId || 'user';
    const content = payload.contentPreview || '';
    task = `New message from ${userId}: "${content}"

Reply via: POST ${apiBase}/api/conversations/${convId}/messages
View thread: GET ${apiBase}/api/conversations/${convId}/messages?limit=100`;
  } else if (event === 'application.received') {
    const bountyId = payload.bountyId || '';
    const appId = payload.applicationId || '';
    const title = payload.bountyTitle || 'Bounty';
    const name = payload.humanName || 'Someone';
    task = `New application to "${title}" from ${name}

View: GET ${apiBase}/api/bounties/${bountyId}/applications
Accept/reject: PATCH ${apiBase}/api/bounties/${bountyId}/applications/${appId}`;
  } else {
    task = `Webhook event: ${event}\n\nPayload: ${JSON.stringify(payload, null, 2)}`;
  }
  
  // CRITICAL: Inject API key directly in message so agent can use it
  const apiKeyNote = `\n\n🔑 API KEY: ${API_KEY}\nUse this header: X-API-Key: ${API_KEY}`;
  
  return `[RentAPerson agent. API docs: ${skillUrl}]

${task}${apiKeyNote}`;
}

function forwardToOpenClaw(payload, callback) {
  const message = buildMessage(payload);
  
  // Use persistent session key to reuse the same session
  const sessionKey = credentials.sessionKey || 'agent:main:rentaperson';
  
  const body = {
    message,
    name: 'RentAPerson',
    sessionKey: sessionKey, // CRITICAL: Reuse persistent session
    wakeMode: 'now',
    deliver: false, // Don't send to messaging channels
  };
  
  // Use mapped hook to avoid "untrusted source" notice (requires hooks.mappings.rentaperson in openclaw.json)
  const url = new URL(`${OPENCLAW_URL}/hooks/rentaperson`);
  const options = {
    method: 'POST',
    hostname: url.hostname,
    port: url.port || (url.protocol === 'https:' ? 443 : 80),
    path: url.pathname,
    headers: {
      'Content-Type': 'application/json',
      ...(OPENCLAW_TOKEN && { 'Authorization': `Bearer ${OPENCLAW_TOKEN}` }),
    },
  };
  
  const client = url.protocol === 'https:' ? require('https') : http;
  
  console.log(`[bridge] Forwarding to: ${OPENCLAW_URL}/hooks/rentaperson`);
  console.log(`[bridge] Using sessionKey: "${sessionKey}"`);
  console.log(`[bridge] Payload:`, JSON.stringify({ ...body, message: body.message.substring(0, 100) + '...' }, null, 2));
  
  const req = client.request(options, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
      console.log(`[bridge] OpenClaw → ${res.statusCode}`);
      if (data) console.log(`[bridge] Response:`, data.substring(0, 200));
      callback(null, { statusCode: res.statusCode, body: data });
    });
  });
  
  req.on('error', (err) => {
    console.error(`[bridge] OpenClaw request failed:`, err.message);
    console.error(`[bridge] Check if OpenClaw is running on ${OPENCLAW_URL}`);
    callback(err);
  });
  
  req.write(JSON.stringify(body));
  req.end();
}

const server = http.createServer((req, res) => {
  if (req.method === 'OPTIONS') {
    res.writeHead(200, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST',
      'Access-Control-Allow-Headers': 'Content-Type',
    });
    res.end();
    return;
  }
  
  if (req.method !== 'POST') {
    res.writeHead(405, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Method not allowed' }));
    return;
  }
  
  let body = '';
  req.on('data', chunk => body += chunk);
  req.on('end', () => {
    try {
      const payload = JSON.parse(body);
      console.log(`[bridge] ← RentAPerson: ${payload.event || 'unknown event'}`);
      
      forwardToOpenClaw(payload, (err, result) => {
        if (err) {
          console.error('[bridge] Error:', err);
          res.writeHead(502, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Failed to forward', message: err.message }));
          return;
        }
        
        res.writeHead(result.statusCode, { 'Content-Type': 'application/json' });
        res.end(result.body);
      });
    } catch (e) {
      console.error('[bridge] Parse error:', e);
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid JSON', message: e.message }));
    }
  });
});

server.listen(BRIDGE_PORT, () => {
  console.log(`[bridge] ✅ Listening on http://127.0.0.1:${BRIDGE_PORT}`);
  console.log(`[bridge] Ready to receive webhooks from RentAPerson`);
});

process.on('SIGTERM', () => {
  console.log('[bridge] Shutting down...');
  server.close(() => process.exit(0));
});

process.on('SIGINT', () => {
  console.log('[bridge] Shutting down...');
  server.close(() => process.exit(0));
});
