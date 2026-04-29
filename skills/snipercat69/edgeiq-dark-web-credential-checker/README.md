# Dark Web Credential Checker — CLI Setup

Check if your email or username appears in known data breaches and dark web exposures.

## Installation

```bash
git clone https://github.com/snipercat69/edgeiq-credential-checker.git
cd edgeiq-credential-checker
```

## Quick Start

```bash
# Free: check up to 3 emails
python3 credential_checker.py --email "you@example.com"

# Pro: full breach report
EDGEIQ_EMAIL=your_email@gmail.com python3 credential_checker.py \
  --email "you@example.com" --username "yourhandle" --pro

# Bundle: unlimited + JSON export
EDGEIQ_EMAIL=your_email@gmail.com python3 credential_checker.py \
  --email "you@example.com" --bundle --output breach-report.json
```

## Features

- Email breach search across public databases
- Username lookup in breach compilations
- Breach source identification
- Exposed data classification
- Password hash detection
- JSON export for security audits

## Legal Notice

For personal use only. Do not use to search others without consent.

## Licensing

Free tier: 3 email checks.

Pro ($19/mo) or Bundle ($39/mo): [buy.stripe.com/aFa00l9i3bxrcUs18c7wA0k](https://buy.stripe.com/aFa00l9i3bxrcUs18c7wA0k)