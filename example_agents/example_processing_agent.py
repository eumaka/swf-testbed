"""
Example Processing Agent: Handles data ready messages.
"""

from base_agent import ExampleAgent
import json

class ProcessingAgent(ExampleAgent):
    """
    An example agent that simulates the role of the Processing Agent.
    It listens for 'data_ready' messages.
    """

    def __init__(self):
        super().__init__(agent_type='PROCESSING', subscription_queue='processing_agent')

    def on_message(self, frame):
        """
        Handles an incoming 'data_ready' message.
        """
        print(f"Processing Agent received a message!")
        try:
            message_data = json.loads(frame.body)
            if message_data.get('msg_type') == 'data_ready':
                print(f"Processing data for: {message_data.get('filename')}")
                # 1. TODO: Call monitor API to update workflow status
                # 2. TODO: Simulate processing
                # 3. TODO: Call monitor API to mark workflow as complete
            else:
                print(f"Ignoring message of type: {message_data.get('msg_type')}")
        except Exception as e:
            print(f"Error processing message: {e}")


if __name__ == "__main__":
    agent = ProcessingAgent()
    agent.run()
