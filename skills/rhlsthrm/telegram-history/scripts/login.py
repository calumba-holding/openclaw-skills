#!/usr/bin/env python3
"""Simple login script - pass phone and code as args."""
import asyncio
import json
import os
import sys

from telethon import TelegramClient

SESSION_PATH = os.path.expanduser("~/.openclaw/workspace/skills/telegram-history/session/user")
CREDS_PATH = os.path.expanduser("~/.openclaw/workspace/skills/telegram-history/api_credentials.json")

async def main():
    with open(CREDS_PATH) as f:
        creds = json.load(f)
    
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
    client = TelegramClient(SESSION_PATH, int(creds["api_id"]), creds["api_hash"])
    
    if len(sys.argv) == 2 and sys.argv[1] == "check":
        await client.connect()
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"Already logged in as {me.first_name} ({me.phone})")
        else:
            print("Not logged in. Sending code...")
            await client.send_code_request("+16508238624")
            print("Code sent! Run: python3 login.py verify <code> <phone_code_hash>")
        await client.disconnect()
        return
    
    if len(sys.argv) == 2 and sys.argv[1] == "send":
        await client.connect()
        result = await client.send_code_request("+16508238624")
        print(f"Code sent! phone_code_hash: {result.phone_code_hash}")
        print(f"Run: python3 login.py verify <code> {result.phone_code_hash}")
        await client.disconnect()
        return
    
    if len(sys.argv) >= 4 and sys.argv[1] == "verify":
        code = sys.argv[2]
        phone_code_hash = sys.argv[3]
        password = sys.argv[4] if len(sys.argv) > 4 else None
        await client.connect()
        try:
            await client.sign_in("+16508238624", code, phone_code_hash=phone_code_hash)
        except Exception as e:
            if "Two-steps" in str(e) and password:
                await client.sign_in(password=password)
            elif "Two-steps" in str(e):
                print("2FA required. Run: python3 login.py verify <code> <hash> <2fa_password>")
                await client.disconnect()
                return
            else:
                print(f"Error: {e}")
                await client.disconnect()
                return
        me = await client.get_me()
        print(f"Logged in as {me.first_name} ({me.phone})")
        await client.disconnect()
        return
    
    print("Usage:")
    print("  python3 login.py check   - Check if logged in")
    print("  python3 login.py send    - Send verification code")
    print("  python3 login.py verify <code> <hash>  - Complete login")

asyncio.run(main())
