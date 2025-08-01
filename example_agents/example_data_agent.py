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
        Handles incoming DAQ messages (stf_gen, run_imminent, start_run, end_run).
        """
        self.logger.info("Data Agent received message")
        try:
            message_data = json.loads(frame.body)
            msg_type = message_data.get('msg_type')
            
            if msg_type == 'stf_gen':
                self.handle_stf_gen(message_data)
            elif msg_type == 'run_imminent':
                self.handle_run_imminent(message_data)
            elif msg_type == 'start_run':
                self.handle_start_run(message_data)
            elif msg_type == 'end_run':
                self.handle_end_run(message_data)
            else:
                self.logger.info("Ignoring unknown message type", extra={"msg_type": msg_type})
        except Exception as e:
            self.logger.error("Error processing message", extra={"error": str(e)})

    def handle_run_imminent(self, message_data):
        """Handle run_imminent message - create dataset in Rucio"""
        run_id = message_data.get('run_id')
        self.logger.info("Processing run_imminent message", 
                        extra={"run_id": run_id, "simulation_tick": message_data.get('simulation_tick')})
        
        # TODO: Call Rucio to create dataset for this run
        # TODO: Call monitor API to create run record
        
        # Simulate dataset creation
        self.logger.info("Created dataset for run", extra={"run_id": run_id})

    def handle_start_run(self, message_data):
        """Handle start_run message - run is starting physics"""
        run_id = message_data.get('run_id')
        self.logger.info("Processing start_run message", 
                        extra={"run_id": run_id, "simulation_tick": message_data.get('simulation_tick')})
        
        # TODO: Update run status in monitor API
        self.logger.info("Run started", extra={"run_id": run_id})

    def handle_end_run(self, message_data):
        """Handle end_run message - run has ended"""
        run_id = message_data.get('run_id')
        total_files = message_data.get('total_files', 0)
        self.logger.info("Processing end_run message", 
                        extra={"run_id": run_id, "total_files": total_files, "simulation_tick": message_data.get('simulation_tick')})
        
        # TODO: Finalize dataset in Rucio
        # TODO: Update run status in monitor API
        self.logger.info("Run ended", extra={"run_id": run_id, "total_files": total_files})

    def handle_stf_gen(self, message_data):
        """Handle stf_gen message - new STF file available"""
        filename = message_data.get('filename')
        run_id = message_data.get('run_id')
        file_url = message_data.get('file_url')
        checksum = message_data.get('checksum')
        size_bytes = message_data.get('size_bytes')
        
        self.logger.info("Processing STF file", 
                        extra={"filename": filename, "run_id": run_id, "size_bytes": size_bytes,
                              "simulation_tick": message_data.get('simulation_tick')})
        
        # TODO: Register STF file with Rucio
        # TODO: Initiate transfer to E1 facilities  
        # TODO: Call monitor API to create/update workflow
        
        # Simulate processing time
        import time
        time.sleep(0.1)
        
        # Send data_ready message to processing agent
        data_ready_message = {
            "msg_type": "data_ready",
            "filename": filename,
            "run_id": run_id,
            "file_url": file_url,
            "checksum": checksum,
            "size_bytes": size_bytes,
            "simulation_tick": message_data.get('simulation_tick'),
            "processed_by": self.agent_name
        }
        
        self.send_message('processing_agent', data_ready_message)
        self.logger.info("Sent data_ready message", 
                        extra={"filename": filename, "run_id": run_id, "destination": "processing_agent"})


if __name__ == "__main__":
    agent = DataAgent()
    agent.run()
