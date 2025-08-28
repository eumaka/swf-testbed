#!/usr/bin/env python3
"""
Remote SSE Receiver: Connects to the monitor's SSE stream to receive workflow messages.

This script demonstrates receiving real-time workflow messages via Server-Sent Events
from the swf-monitor. It connects to the SSE endpoint and logs received messages,
then waits for more messages in a continuous loop.
"""

import requests
import json
import time
import sys
import os
from pathlib import Path
import signal
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def setup_environment():
    """Load environment variables from ~/.env file."""
    env_file = Path.home() / ".env"
    if env_file.exists():
        print("🔧 Loading environment variables from ~/.env...")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]  # Remove 'export '
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('\"\'')

class RemoteSSEReceiver:
    """
    Example client that connects to the monitor's SSE stream and logs received messages.
    Demonstrates how external clients can receive real-time workflow events.
    """

    def __init__(self):
        setup_environment()
        
        # Get configuration from environment
        self.monitor_url = 'https://127.0.0.1:8443'
        self.api_token = os.getenv('SWF_API_TOKEN')
        self.running = True
        
        if not self.api_token:
            print("❌ Error: SWF_API_TOKEN not set in environment")
            print("   Please ensure ~/.env contains: export SWF_API_TOKEN=your_token_here")
            sys.exit(1)
        
        # Set up HTTP session with authentication
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Token {self.api_token}'})
        self.session.headers.update({'Cache-Control': 'no-cache'})
        self.session.headers.update({'Accept': 'text/event-stream'})
        self.session.verify = False  # Accept self-signed certificates for development
        self.session.proxies = {}    # Bypass proxy for localhost
        self.session.trust_env = False
        
        # Set up signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("🔧 Remote SSE Receiver initialized")
        print(f"   Monitor URL: {self.monitor_url}")
        print(f"   Using token: {self.api_token[:12]}...")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\n📡 Received signal {signum} - shutting down gracefully...")
        self.running = False

    def connect_and_receive(self):
        """Connect to SSE stream and process messages in a loop."""
        # Build SSE stream URL with optional filters
        stream_url = f"{self.monitor_url}/api/messages/stream/"
        
        # Example: filter for specific message types and agents
        # Uncomment and modify as needed:
        # stream_url += "?msg_types=sse_test,data_ready,processing_complete&agents=remote-sse-sender"
        
        print(f"📡 Connecting to SSE stream: {stream_url}")
        
        retry_count = 0
        max_retries = 5
        
        while self.running and retry_count < max_retries:
            try:
                # Test connection first with status endpoint - use shorter timeout
                status_url = stream_url.replace('/stream/', '/stream/status/')
                print("🔌 Testing SSE endpoint...")
                status_resp = self.session.get(status_url, timeout=5)
                
                if status_resp.status_code != 200:
                    print(f"❌ SSE endpoint not available: HTTP {status_resp.status_code}")
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"   Retrying in 5 seconds... ({retry_count}/{max_retries})")
                        time.sleep(5)
                    continue
                
                print("✅ SSE endpoint is available!")
                print("📡 Opening SSE stream...")
                
                # Now connect to streaming endpoint
                response = self.session.get(stream_url, stream=True, timeout=(10, 3600))
                
                if response.status_code != 200:
                    print(f"❌ Failed to open stream: HTTP {response.status_code}")
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"   Retrying in 5 seconds... ({retry_count}/{max_retries})")
                        time.sleep(5)
                    continue
                
                print("✅ SSE stream opened - waiting for events... (Ctrl+C to exit)")
                print("-" * 60)
                
                retry_count = 0  # Reset retry counter on successful connection
                
                # Process SSE events
                self._process_sse_stream(response)
                
            except requests.exceptions.ReadTimeout as e:
                print(f"⏱️  Read timeout while waiting for messages: {e}")
                print("   This usually means no messages were received within the timeout period")
                retry_count += 1
                if retry_count < max_retries and self.running:
                    print(f"   Reconnecting in 5 seconds... ({retry_count}/{max_retries})")
                    time.sleep(5)
            except requests.exceptions.RequestException as e:
                print(f"❌ Connection error: {e}")
                retry_count += 1
                if retry_count < max_retries and self.running:
                    print(f"   Retrying in 5 seconds... ({retry_count}/{max_retries})")
                    time.sleep(5)
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                retry_count += 1
                if retry_count < max_retries and self.running:
                    time.sleep(5)
        
        if retry_count >= max_retries:
            print(f"❌ Max retries ({max_retries}) exceeded - giving up")
        
        print("📡 SSE Receiver shutdown complete")

    def _process_sse_stream(self, response):
        """Process incoming SSE events."""
        event_buffer = []
        
        try:
            for line in response.iter_lines(decode_unicode=True, chunk_size=1):
                if not self.running:
                    break
                    
                if line is None:
                    continue
                    
                line = line.strip()
                
                if not line:
                    # Empty line indicates end of an event
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
            except:
                pass

    def _handle_sse_event(self, event_lines):
        """Handle a complete SSE event."""
        event_type = "message"  # default
        event_data = ""
        
        # Parse SSE event format
        for line in event_lines:
            if line.startswith('event: '):
                event_type = line[7:]
            elif line.startswith('data: '):
                event_data = line[6:]
        
        timestamp = time.strftime("%H:%M:%S")
        
        # Handle different event types
        if event_type == "connected":
            print(f"[{timestamp}] 🔗 Connected to SSE stream")
            try:
                data = json.loads(event_data)
                client_id = data.get('client_id', 'unknown')
                print(f"[{timestamp}] 📋 Client ID: {client_id}")
            except:
                pass
        
        elif event_type == "heartbeat":
            print(f"[{timestamp}] 💓 Heartbeat received")
        
        else:
            # Workflow message
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

def main():
    """Main entry point."""
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