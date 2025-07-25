"""
Example DAQ Simulator Agent: Originates the workflow.
"""

from base_agent import ExampleAgent
import json
import time
import uuid
from datetime import datetime

class DaqSimAgent(ExampleAgent):
    """
    An example agent that simulates the DAQ system.
    It periodically generates 'stf_gen' messages to trigger the workflow,
    and listens on a control queue for commands.
    """

    def __init__(self):
        # This agent listens for control messages and produces STF messages.
        super().__init__(agent_type='daqsim', subscription_queue='daq_control')
        self.running = True

    def on_message(self, frame):
        """
        Handles incoming control messages.
        """
        try:
            message_data = json.loads(frame.body)
            command = message_data.get('command')
            self.log('INFO', f"Received command: {command}")
            
            if command == 'stop':
                self.running = False
            elif command == 'start':
                self.running = True
            else:
                self.log('WARNING', f"Unknown command received: {command}")

        except Exception as e:
            self.log('ERROR', f"Error processing control message: {e}")

    def run(self):
        """
        The main run loop for the DAQ simulator. For this test, we will
        just use the base class's run method to test connection and heartbeat.
        """
        super().run()


    def generate_and_send_stf(self):
        """
        Generates a fake STF message and sends it to the 'epictopic'.
        """
        filename = f"stf_{uuid.uuid4().hex[:8]}.dat"
        now = datetime.utcnow()
        
        message = {
            'msg_type': 'stf_gen',
            'filename': filename,
            'start': now.strftime('%Y%m%d%H%M%S'),
            'end': now.strftime('%Y%m%d%H%M%S'),
            'state': 'physics',
            'substate': 'running',
            'comment': 'A simulated STF file.'
        }
        
        self.log('INFO', f"Generated new STF: {filename}")
        self.send_message('epictopic', message)


if __name__ == "__main__":
    agent = DaqSimAgent()
    agent.run()