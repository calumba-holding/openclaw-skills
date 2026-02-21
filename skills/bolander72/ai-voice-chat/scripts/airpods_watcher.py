#!/usr/bin/env python3
"""
Bluetooth Headset Watcher — auto-starts voice loop when headset connects.

Polls audio devices every N seconds. When a matching Bluetooth device appears
as an input device, starts the voice loop. When it disconnects, stops it.

Config via environment variables:
  VL_HEADSET_NAME  — substring to match (default: "AirPods")
  VL_POLL_INTERVAL — seconds between polls (default: 5)
"""

import subprocess
import time
import signal
import sys
import os

HEADSET_NAME = os.environ.get("VL_HEADSET_NAME", "AirPods")
POLL_INTERVAL = int(os.environ.get("VL_POLL_INTERVAL", "5"))

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOICE_LOOP_SCRIPT = os.path.join(SCRIPT_DIR, "voice_loop.py")
VENV_PYTHON = os.path.join(SCRIPT_DIR, "..", ".venv", "bin", "python")

running = True
voice_loop_proc = None


def signal_handler(sig, frame):
    global running
    print("\n🛑 Watcher shutting down...")
    running = False
    stop_voice_loop()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def headset_connected() -> bool:
    """Check if the headset is available as an input device."""
    try:
        result = subprocess.run(
            [VENV_PYTHON, "-c", f"""
import sounddevice as sd
devices = sd.query_devices()
for d in devices:
    if d['max_input_channels'] > 0 and '{HEADSET_NAME}' in d['name']:
        print('FOUND')
        break
"""],
            capture_output=True, text=True, timeout=5
        )
        return "FOUND" in result.stdout
    except Exception:
        return False


def start_voice_loop():
    global voice_loop_proc
    if voice_loop_proc and voice_loop_proc.poll() is None:
        return

    print(f"🎧 {HEADSET_NAME} detected — starting voice loop...", flush=True)
    # Only pass through voice-loop env vars + essential PATH
    safe_env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
    for key in os.environ:
        if key.startswith("VL_"):
            safe_env[key] = os.environ[key]
    # HOME needed for Keychain access and model cache
    if "HOME" in os.environ:
        safe_env["HOME"] = os.environ["HOME"]

    voice_loop_proc = subprocess.Popen(
        [VENV_PYTHON, VOICE_LOOP_SCRIPT],
        cwd=os.path.dirname(VOICE_LOOP_SCRIPT),
        env=safe_env,
    )
    print(f"   Voice loop started (pid {voice_loop_proc.pid})", flush=True)


def stop_voice_loop():
    global voice_loop_proc
    if voice_loop_proc and voice_loop_proc.poll() is None:
        print(f"🔇 {HEADSET_NAME} disconnected — stopping voice loop...", flush=True)
        voice_loop_proc.terminate()
        try:
            voice_loop_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            voice_loop_proc.kill()
        print("   Voice loop stopped.", flush=True)
    voice_loop_proc = None


def main():
    print("=" * 50)
    print("👂 Headset Watcher")
    print("=" * 50)
    print(f"Watching for: {HEADSET_NAME}")
    print(f"Poll interval: {POLL_INTERVAL}s")
    print(f"Voice loop: {VOICE_LOOP_SCRIPT}")
    print(f"Python: {VENV_PYTHON}")
    print("Press Ctrl+C to stop\n")

    was_connected = False

    while running:
        connected = headset_connected()

        if connected and not was_connected:
            start_voice_loop()
            was_connected = True
        elif not connected and was_connected:
            stop_voice_loop()
            was_connected = False

        # Restart if voice loop crashed while headset still connected
        if was_connected and voice_loop_proc and voice_loop_proc.poll() is not None:
            print("⚠️  Voice loop crashed, restarting...", flush=True)
            start_voice_loop()

        time.sleep(POLL_INTERVAL)

    stop_voice_loop()
    print("👋 Watcher ended.")


if __name__ == "__main__":
    main()
