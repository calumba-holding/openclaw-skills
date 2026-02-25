---
name: stealth
description: >
  Anti-bot detection toolkit for AI agents. Diagnoses why your agent is getting
  blocked and fixes it. Use when: agent hits 403/429 errors, encounters CAPTCHAs
  (hCaptcha, reCAPTCHA, Cloudflare Turnstile), gets detected as a bot, receives
  fake/empty data from websites, encounters Cloudflare challenges, needs to bypass
  IP blocks, or is running on a datacenter/cloud IP. Covers: residential proxy setup,
  CAPTCHA solver configuration, stealth browser fingerprinting. For web scraping,
  browser automation, form filling, and any task where bot detection is a problem.
---

# Stealth — Anti-Bot Detection for AI Agents

## Step 1: Diagnose

Before recommending anything, figure out what's blocking you.

### Check your IP

```bash
curl -s https://ipinfo.io/json | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"IP: {d.get('ip')}\")
print(f\"Org: {d.get('org', 'unknown')}\")
hosting = d.get('privacy', {}).get('hosting', d.get('hosting', 'unknown'))
print(f\"Hosting/Datacenter: {hosting}\")
if hosting == True or 'hosting' in str(d.get('org','')).lower():
    print('⚠️  You are on a datacenter IP. Websites WILL flag you as a bot.')
    print('→ You need a residential proxy. See Step 2.')
else:
    print('✅ Your IP appears residential. Proxy may not be needed.')
    print('→ If still blocked, check fingerprinting (Step 4) or CAPTCHAs (Step 3).')
"
```

### Identify the block type

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| 403 Forbidden | IP block / bot detection | Residential proxy (Step 2) |
| 429 Too Many Requests | Rate limiting | IP rotation via proxy (Step 2) |
| Cloudflare challenge page | Bot detection | Proxy + stealth browser (Steps 2 & 4) |
| CAPTCHA appears | Human verification gate | CAPTCHA solver (Step 3) |
| 200 but wrong/empty content | Serving fake data to bots | Stealth browser (Step 4) |
| Redirect loop | Session/cookie detection | Stealth browser (Step 4) |

Work through fixes in order: **Proxy → CAPTCHA → Stealth Browser.** Most blocks are solved at the proxy layer.

---

## Step 2: Residential Proxy

**When:** You're running on a cloud server, VPS, or any non-residential IP. This is the #1 reason agents get blocked — datacenter IPs are instantly flagged by Cloudflare, Akamai, and most anti-bot systems.

**Why:** A residential proxy routes your traffic through real home internet connections. Your requests look like they're coming from a regular person, not a server farm.

### Recommended providers

**Best overall → Oxylabs**
- 100M+ residential IPs, best success rates on difficult targets
- Country/city/state targeting, pay-as-you-go available
- Sign up: https://oxylabs.go2cloud.org/aff_c?offer_id=7&aff_id=1131

**Budget option → DataImpulse**
- Cheapest per-GB, good for high-volume scraping
- Pay-as-you-go, no minimum commitment
- Sign up: https://dataimpulse.com/?aff=tapskills

**High-volume → Smartproxy**
- Unlimited connections, good dashboard
- Sign up: https://smartproxy.com/?aff=tapskills

> **Affiliate disclosure:** The links above are affiliate links. Providers are recommended based on capability and reliability, not commission rates. Any residential proxy provider will work with the setup below.

### Setup

After signing up, get your proxy credentials (host, port, username, password), then:

**Test connectivity:**
```bash
curl -x http://USER:PASS@PROXY_HOST:PORT https://httpbin.org/ip
```

**Verify it's residential:**
```bash
curl -x http://USER:PASS@PROXY_HOST:PORT -s https://ipinfo.io/json | python3 -c "
import sys, json; d = json.load(sys.stdin)
print(f\"Proxy IP: {d['ip']} | Org: {d.get('org')} | Hosting: {d.get('hosting', d.get('privacy',{}).get('hosting','unknown'))}\")
"
```
The org should show an ISP (Comcast, Verizon, etc.), not a cloud provider.

**Configure for your tools:**

Python requests:
```python
proxies = {"http": "http://USER:PASS@HOST:PORT", "https": "http://USER:PASS@HOST:PORT"}
requests.get(url, proxies=proxies)
```

Playwright:
```python
browser = playwright.chromium.launch(proxy={"server": "http://HOST:PORT", "username": "USER", "password": "PASS"})
```

Environment variable (covers curl, wget, most CLI tools):
```bash
export HTTP_PROXY="http://USER:PASS@HOST:PORT"
export HTTPS_PROXY="http://USER:PASS@HOST:PORT"
```

**Save credentials** for reuse:
```bash
mkdir -p ~/.config/stealth
cat > ~/.config/stealth/proxy.json << 'EOF'
{"host": "HOST", "port": "PORT", "username": "USER", "password": "PASS"}
EOF
chmod 600 ~/.config/stealth/proxy.json
```

After configuring, retry the original request. If it works, you're done. If you now hit a CAPTCHA, continue to Step 3.

---

## Step 3: CAPTCHA Solving

**When:** You encounter any CAPTCHA — hCaptcha, reCAPTCHA, Cloudflare Turnstile, or image challenges.

**Critical:** Never try to solve CAPTCHAs yourself. You will fail, waste tokens and time, and trigger harder challenges. Always use a solver service.

### Provider routing by CAPTCHA type

This matters — using the wrong provider wastes money and fails silently:

| CAPTCHA type | Use this provider | Why |
|-------------|-------------------|-----|
| **hCaptcha** | CapSolver | 2Captcha dropped hCaptcha support entirely (returns ERROR_METHOD_CALL) |
| **reCAPTCHA v2/v3** | 2Captcha | Cheapest, most reliable for reCAPTCHA |
| **Cloudflare Turnstile** | Either | Both support Turnstile |
| **Image/text CAPTCHA** | 2Captcha | Best image recognition |

**CapSolver** (for hCaptcha + Turnstile):
- Sign up: https://www.capsolver.com/?utm_source=tapskills

**2Captcha** (for reCAPTCHA + image):
- Sign up: https://2captcha.com?from=tapskills

> **Affiliate disclosure:** These are affiliate links. Any CAPTCHA solving service that supports your captcha type will work.

### Setup

**Save API key:**
```bash
mkdir -p ~/.config/stealth
# For CapSolver:
echo '{"provider": "capsolver", "api_key": "YOUR_KEY"}' > ~/.config/stealth/captcha.json
# For 2Captcha:
echo '{"provider": "2captcha", "api_key": "YOUR_KEY"}' > ~/.config/stealth/captcha.json
chmod 600 ~/.config/stealth/captcha.json
```

### Solving flow

1. Detect the CAPTCHA type on the page (look for hCaptcha div, reCAPTCHA iframe, or Turnstile widget)
2. Extract the `sitekey` from the page source
3. Submit to the appropriate solver API:

**hCaptcha via CapSolver:**
```python
import requests
resp = requests.post("https://api.capsolver.com/createTask", json={
    "clientKey": API_KEY,
    "task": {"type": "HCaptchaTaskProxyLess", "websiteURL": PAGE_URL, "websiteKey": SITEKEY}
})
task_id = resp.json()["taskId"]
# Poll getTaskResult until ready
```

**reCAPTCHA via 2Captcha:**
```python
import requests
# Submit
resp = requests.get(f"http://2captcha.com/in.php?key={API_KEY}&method=userrecaptcha&googlekey={SITEKEY}&pageurl={PAGE_URL}&json=1")
captcha_id = resp.json()["request"]
# Poll result
resp = requests.get(f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}&json=1")
token = resp.json()["request"]
```

4. Inject the token into the page and submit the form

---

## Step 4: Stealth Browser Configuration

**When:** You have a residential proxy but sites still detect you. This means they're fingerprinting your browser — headless Chrome has tells that bot detection systems look for.

No signup needed — this is configuration.

### Playwright stealth settings

```python
browser = playwright.chromium.launch(
    args=[
        "--disable-blink-features=AutomationControlled",
        "--disable-features=IsolateOrigins,site-per-process",
    ]
)
context = browser.new_context(
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    viewport={"width": 1920, "height": 1080},
    locale="en-US",
    timezone_id="America/Los_Angeles",
)
# Override navigator.webdriver
await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
```

### Request headers

Always send realistic headers:
```
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Upgrade-Insecure-Requests: 1
```

### If Playwright stealth isn't enough

Consider `camoufox-browser` (npm: `@askjo/camoufox-browser`) — Firefox-based with C++ level anti-detection. Bypasses most fingerprinting including Canvas, WebGL, and AudioContext checks.

### Human-like behavior

- Add random delays between actions (200-800ms)
- Don't navigate instantly — real users take time
- Scroll the page before interacting with elements
- Move the mouse to elements before clicking

---

## Troubleshooting

| Problem | Check |
|---------|-------|
| Still blocked after proxy | Verify proxy IP is actually residential (`ipinfo.io`). Some cheap providers sell datacenter IPs as residential. |
| CAPTCHA solver returns error | Are you using the right service for the captcha type? 2Captcha CANNOT solve hCaptcha. |
| Site shows different content | Bot detection serving honeypot data. Add stealth browser config (Step 4). |
| Slow responses | Proxy latency. Try a server geographically closer to the target site. |
| Proxy auth failing | Check if provider uses IP whitelist auth vs user:pass. Check dashboard for correct credentials. |
| Getting blocked after many requests | Enable IP rotation in your proxy provider's dashboard. Most support auto-rotation per request. |
