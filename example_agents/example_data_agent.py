"""
Example Data Agent: Handles STF generation messages.
"""

from base_agent import ExampleAgent
import json

class DataAgent(ExampleAgent):
    """
    An example agent that simulates the role of the Data Agent.
    It listens for 'stf_gen' messages and sends 'data_ready' messages.
    """

    def __init__(self):
        super().__init__(agent_type='DATA', subscription_queue='epictopic')

    def on_message(self, frame):
        """
        Handles an incoming 'stf_gen' message.
        """
        print(f"Data Agent received a message!")
        try:
            message_data = json.loads(frame.body)
            if message_data.get('msg_type') == 'stf_gen':
                print(f"Processing STF file: {message_data.get('filename')}")
                # 1. TODO: Call monitor API to create workflow
                # 2. TODO: Simulate processing
                # 3. TODO: Call monitor API to update workflow status
                # 4. TODO: Send 'data_ready' message to 'processing_agent' queue
            else:
                print(f"Ignoring message of type: {message_data.get('msg_type')}")
        except Exception as e:
            print(f"Error processing message: {e}")


if __name__ == "__main__":
    agent = DataAgent()
    agent.run()
