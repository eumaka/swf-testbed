#!/usr/bin/env python3
"""
Remote SSE Sender: Sends test messages through ActiveMQ that will be relayed to SSE clients.

This script demonstrates sending workflow messages that the monitor will broadcast
to connected SSE clients. It inherits from BaseAgent to use standard logging and
ActiveMQ connectivity.
"""

from swf_common_lib.base_agent import BaseAgent
import json
import time
import sys

class RemoteSSESender(BaseAgent):
    """
    Example agent that sends test messages to demonstrate SSE functionality.
    Sends a few test messages and exits.
    """

    def __init__(self):
        super().__init__(agent_type='SSE_SENDER', subscription_queue='epictopic')
        self.messages_to_send = [
            {
                'msg_type': 'sse_test',
                'processed_by': 'remote-sse-sender',
                'run_id': 'test-run-001',
                'message': 'Hello from SSE sender!',
                'data': 'This is a test message for SSE demonstration'
            },
            {
                'msg_type': 'data_ready',
                'processed_by': 'remote-sse-sender', 
                'run_id': 'test-run-001',
                'filename': 'test_file_001.dat',
                'message': 'Simulated data ready event'
            },
            {
                'msg_type': 'processing_complete',
                'processed_by': 'remote-sse-sender',
                'run_id': 'test-run-001', 
                'filename': 'test_file_001.dat',
                'message': 'Simulated processing complete event'
            }
        ]

    def on_message(self, frame):
        """Handle incoming messages (not needed for this sender-only example)."""
        pass

    def run_sender(self):
        """Send test messages and exit."""
        self.logger.info("Starting Remote SSE Sender")
        self.logger.info(f"Will send {len(self.messages_to_send)} test messages")
        
        # Wait a moment for connection to stabilize
        time.sleep(2)
        
        for i, message in enumerate(self.messages_to_send, 1):
            self.logger.info(f"Sending message {i}/{len(self.messages_to_send)}: {message['msg_type']}")
            
            try:
                # Send message to ActiveMQ topic
                self.send_message('epictopic', json.dumps(message))
                self.logger.info(f"Successfully sent message: {message['msg_type']} for run {message['run_id']}")
                
                # Brief pause between messages
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Failed to send message {i}: {e}")
        
        self.logger.info("All test messages sent successfully")
        self.logger.info("Remote SSE Sender completed - exiting")

def main():
    """Main entry point."""
    try:
        sender = RemoteSSESender()
        sender.run_sender()
        
    except KeyboardInterrupt:
        print("\nReceived interrupt signal - exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()