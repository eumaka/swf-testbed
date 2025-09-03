#!/usr/bin/env python3
"""
Remote SSE Receiver: Connects to the monitor's SSE stream to receive workflow messages.

This script receives real-time workflow messages via Server-Sent Events (SSE)
from the swf-monitor running under production Apache. It connects to the SSE
endpoint and logs received messages.
"""

import os
import sys
import time
import json
import signal
from pathlib import Path

import requests

# Canonical production base URL (can be overridden by SWF_MONITOR_PROD_URL)
DEFAULT_MONITOR_BASE = "https://pandaserver02.sdcc.bnl.gov/swf-monitor"

def setup_environment() -> None:
    """Load environment variables from ~/.env file if present."""
    env_file = Path.home() / ".env"
    if env_file.exists():
        with env_file.open() as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                if line.startswith('export '):
                    line = line[7:]
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip("'\"")


class RemoteSSEReceiver:
    """Production-only SSE client for swf-monitor."""

    def __init__(self) -> None:
        setup_environment()

        # Production monitor base URL (env override, otherwise production default)
        env_url = os.getenv('SWF_MONITOR_PROD_URL')
        if env_url:
            self.monitor_base = env_url.rstrip('/')
        else:
            self.monitor_base = DEFAULT_MONITOR_BASE
            print(f"ℹ️  Using default production URL: {self.monitor_base} (override with SWF_MONITOR_PROD_URL)")

        self.api_token = os.getenv('SWF_API_TOKEN')
        if not self.api_token:
            print("❌ Error: SWF_API_TOKEN not set in environment")
            sys.exit(1)

        self.running = True

        # HTTP session: production defaults (verify=True, env proxies honored)
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {self.api_token}',
            'Cache-Control': 'no-cache',
            'Accept': 'text/event-stream',
            'Connection': 'keep-alive',
        })

        # Graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        print("🔧 Remote SSE Receiver initialized")
        print(f"   Monitor base: {self.monitor_base}")
        print(f"   Token prefix: {self.api_token[:12]}...")
        ca_bundle = os.getenv('REQUESTS_CA_BUNDLE')
        if ca_bundle:
            print(f"   CA bundle:   {ca_bundle}")

    def _signal_handler(self, signum, frame) -> None:
        print(f"\n📡 Received signal {signum} - shutting down gracefully...")
        self.running = False

    def connect_and_receive(self) -> None:
        """Connect to SSE stream and process messages in a loop."""
        stream_url = f"{self.monitor_base}/api/messages/stream/"
        status_url = f"{self.monitor_base}/api/messages/stream/status/"
        print(f"📡 Connecting to SSE stream: {stream_url}")

        while self.running:
            try:
                # Status precheck
                print("🔌 Testing SSE endpoint...")
                # Do not follow redirects; 302 likely indicates auth not reaching Django
                # The status endpoint is a regular DRF endpoint, not an SSE stream, so override Accept header
                status_resp = self.session.get(status_url, timeout=20, allow_redirects=False, headers={'Accept': 'application/json'})
                if status_resp.status_code != 200:
                    if status_resp.status_code in (401, 403):
                        print(f"❌ Auth failed (HTTP {status_resp.status_code}). Check SWF_API_TOKEN (token may be missing/invalid).")
                        www = status_resp.headers.get('WWW-Authenticate')
                        if www:
                            print(f"   WWW-Authenticate: {www}")
                        print("   If running via Apache, ensure 'WSGIPassAuthorization On' is enabled so the Authorization header reaches Django.")
                    elif 300 <= status_resp.status_code < 400:
                        loc = status_resp.headers.get('Location', 'unknown')
                        print(f"❌ Got redirect (HTTP {status_resp.status_code}) to {loc}. This usually means Authorization isn't being passed through.")
                        print("   Enable 'WSGIPassAuthorization On' in Apache for the /swf-monitor app and reload Apache.")
                    else:
                        print(f"❌ SSE endpoint not available: HTTP {status_resp.status_code}")
                    if self.running:
                        print("   Retrying in 15 seconds...")
                        time.sleep(15)
                    continue

                # Open the SSE stream (blocks quietly while waiting for events)
                # Do not follow redirects; treat as auth failure
                response = self.session.get(stream_url, stream=True, timeout=(10, 3600), allow_redirects=False)
                if response.status_code != 200:
                    if response.status_code in (401, 403):
                        print(f"❌ Auth failed opening stream (HTTP {response.status_code}). Check SWF_API_TOKEN.")
                        www = response.headers.get('WWW-Authenticate')
                        if www:
                            print(f"   WWW-Authenticate: {www}")
                        print("   If behind Apache, ensure 'WSGIPassAuthorization On' is configured.")
                    elif 300 <= response.status_code < 400:
                        loc = response.headers.get('Location', 'unknown')
                        print(f"❌ Redirect when opening stream (HTTP {response.status_code}) to {loc}. Authorization likely not forwarded by Apache.")
                        print("   Configure 'WSGIPassAuthorization On' and reload Apache.")
                    else:
                        print(f"❌ Failed to open stream: HTTP {response.status_code}")
                        print("   Response Headers:")
                        for key, value in response.headers.items():
                            print(f"     {key}: {value}")
                        print("   Response Body:")
                        print(f"     {response.text}")
                    if self.running:
                        print("   Retrying in 15 seconds...")
                        time.sleep(15)
                    continue

                print("✅ SSE stream opened - waiting for events... (Ctrl+C to exit)")
                print("-" * 60)
                # streaming until broken or stopped
                self._process_sse_stream(response)

            except requests.exceptions.ReadTimeout as e:
                print(f"⏱️  Read timeout while waiting for messages: {e}")
                if self.running:
                    print("   Reconnecting in 15 seconds...")
                    time.sleep(15)
            except requests.exceptions.RequestException as e:
                print(f"❌ Connection error: {e}")
                if self.running:
                    print("   Retrying in 15 seconds...")
                    time.sleep(15)
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                if self.running:
                    time.sleep(15)

        print("📡 SSE Receiver shutdown complete")

    def _process_sse_stream(self, response) -> None:
        event_buffer = []
        try:
            for line in response.iter_lines(decode_unicode=True, chunk_size=1):
                if not self.running:
                    break
                if line is None:
                    continue
                line = line.strip()
                if not line:
                    if event_buffer:
                        self._handle_sse_event(event_buffer)
                        event_buffer = []
                else:
                    event_buffer.append(line)
        except KeyboardInterrupt:
            print("\n📡 Received interrupt - closing connection...")
        except Exception as e:
            print(f"❌ Error processing stream: {e}")
        finally:
            try:
                response.close()
            except Exception:
                pass

    def _handle_sse_event(self, event_lines) -> None:
        event_type = "message"
        event_data = ""
        for line in event_lines:
            if line.startswith('event: '):
                event_type = line[7:]
            elif line.startswith('data: '):
                event_data = line[6:]

        timestamp = time.strftime("%H:%M:%S")
        if event_type == "connected":
            print(f"[{timestamp}] 🔗 Connected to SSE stream")
            try:
                data = json.loads(event_data)
                client_id = data.get('client_id', 'unknown')
                print(f"[{timestamp}] 📋 Client ID: {client_id}")
            except Exception:
                pass
        elif event_type == "heartbeat":
            # Stay quiet on heartbeats to avoid log spam
            return
        else:
            try:
                data = json.loads(event_data)
                msg_type = data.get('msg_type', 'unknown')
                processed_by = data.get('processed_by', 'unknown')
                run_id = data.get('run_id', 'N/A')
                print(f"[{timestamp}] 📨 Message received:")
                print(f"            Type: {msg_type}")
                print(f"            From: {processed_by}")
                print(f"            Run:  {run_id}")
                if 'message' in data:
                    print(f"            Text: {data['message']}")
                if 'filename' in data:
                    print(f"            File: {data['filename']}")
                print("-" * 60)
            except json.JSONDecodeError:
                print(f"[{timestamp}] 📨 Non-JSON message: {event_data}")
            except Exception as e:
                print(f"[{timestamp}] ❌ Error parsing message: {e}")


def main() -> None:
    try:
        receiver = RemoteSSEReceiver()
        receiver.connect_and_receive()
    except KeyboardInterrupt:
        print("\n📡 Received interrupt signal - exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()