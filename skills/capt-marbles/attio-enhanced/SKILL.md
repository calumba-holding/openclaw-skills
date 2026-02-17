# Enhanced Attio Skill

An improved Attio CRM skill with batch operations, error handling, and validation.

## Features

- **Batch Operations**: Bulk create/update records with chunking
- **Retry Logic**: Exponential backoff for rate limits
- **Smart Field Mapping**: Auto-transforms fields to Attio format
- **Company & Person Support**: Create companies, people, deals

## Setup

```bash
# Set environment variables
export ATTIO_API_KEY=your_api_key
export ATTIO_WORKSPACE_ID=your_workspace
```

Get API key from: https://app.attio.com/settings/api

## Usage

### Create Companies

```python
from lib.attio_enhanced import AttioEnhancedClient

async with AttioEnhancedClient() as client:
    # Single company
    await client.batch_create_records('companies', [{'name': 'Gameye'}])
    
    # Batch
    await client.batch_create_records('companies', [
        {'name': 'Company A'},
        {'name': 'Company B'}
    ])
```

### Create People

```python
await client.batch_create_records('people', [
    {'name': ['John Doe'], 'email_addresses': ['john@example.com']}
])
```

### Create Deals

```python
# Deals require owner (workspace member) - use Attio UI for now
```

## Field Mapping

The skill auto-transforms common fields:
- `first_name` + `last_name` → Attio name format
- `email` → email_addresses
- Org → companies

## CLI

```bash
# Test connection
python -c "from lib.attio_enhanced import AttioEnhancedClient; print('OK')"
```
