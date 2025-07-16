"""
This module contains the base class for all example agents.
"""

import os
import time
import stomp
import requests
import json
import logging

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ExampleAgent(stomp.ConnectionListener):
    """
    A base class for creating standalone STF workflow agents.

    This class handles the common tasks of:
    - Connecting to the ActiveMQ message broker (and inheriting from stomp.ConnectionListener).
    - Communicating with the swf-monitor REST API.
    - Running a persistent process with graceful shutdown.
    """

    def __init__(self, agent_type, subscription_queue):
        self.agent_type = agent_type
        self.subscription_queue = subscription_queue
        self.agent_name = f"{self.agent_type.lower()}-agent-example"

        # Configuration from environment variables
        self.monitor_url = os.getenv('SWF_MONITOR_URL', 'http://localhost:8000').rstrip('/')
        self.mq_host = os.getenv('ACTIVEMQ_HOST', 'localhost')
        self.mq_port = int(os.getenv('ACTIVEMQ_PORT', 61616))
        self.mq_user = os.getenv('ACTIVEMQ_USER', 'admin')
        self.mq_password = os.getenv('ACTIVEMQ_PASSWORD', 'admin')

        self.conn = stomp.Connection(host_and_ports=[(self.mq_host, self.mq_port)])
        self.conn.set_listener('', self)
        self.api = requests.Session()
        # In a real scenario, you might want to add auth headers
        # self.api.headers.update({'Authorization': f'Bearer {os.getenv("API_TOKEN")}'})

    def run(self):
        """
        Connects to the message broker and runs the agent's main loop.
        """
        logging.info(f"Starting {self.agent_name}...")
        try:
            self.conn.connect(self.mq_user, self.mq_password, wait=True)
            self.conn.subscribe(destination=self.subscription_queue, id=1, ack='auto')
            logging.info(f"Connected to ActiveMQ and subscribed to '{self.subscription_queue}'")
            
            # Initial registration/heartbeat
            self.send_heartbeat()

            logging.info(f"{self.agent_name} is running. Press Ctrl+C to stop.")
            while True:
                time.sleep(60) # Keep the main thread alive, heartbeats can be added here
                self.send_heartbeat()

        except KeyboardInterrupt:
            logging.info(f"Stopping {self.agent_name}...")
        except stomp.exception.ConnectFailedException:
            logging.error("Failed to connect to ActiveMQ. Please check the connection details.")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
        finally:
            if self.conn and self.conn.is_connected():
                self.conn.disconnect()
                logging.info("Disconnected from ActiveMQ.")

    def on_error(self, frame):
        logging.error(f'Received an error from ActiveMQ: {frame.body}')

    def on_message(self, frame):
        """
        Callback for handling incoming messages.
        This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement on_message")

    def send_message(self, destination, message_body):
        """
        Sends a JSON message to a specific destination.
        """
        try:
            self.conn.send(body=json.dumps(message_body), destination=destination)
            logging.info(f"Sent message to '{destination}': {message_body}")
        except Exception as e:
            logging.error(f"Failed to send message to '{destination}': {e}")

    def _api_request(self, method, endpoint, json_data=None):
        """
        Helper method to make a request to the monitor API.
        """
        url = f"{self.monitor_url}/api/v1{endpoint}"
        try:
            response = self.api.request(method, url, json=json_data, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {method.upper()} {url} - {e}")
            return None

    def send_heartbeat(self):
        """Registers the agent and sends a heartbeat to the monitor."""
        logging.info("Sending heartbeat...")
        payload = {
            "instance_name": self.agent_name,
            "agent_type": self.agent_type,
            "status": "OK",
            "description": f"Example {self.agent_type} agent."
        }
        self._api_request('post', '/systemagents/heartbeat/', payload)

    def log(self, level, message):
        """Sends a log record to the monitor."""
        payload = {
            "app_name": "example_agent",
            "instance_name": self.agent_name,
            "level_name": level.upper(),
            "message": message
        }
        self._api_request('post', '/logs/', payload)
