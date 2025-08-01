"""
Example Processing Agent: Handles data ready messages.
"""

from base_agent import ExampleAgent
import json
import time

class ProcessingAgent(ExampleAgent):
    """
    An example agent that simulates the role of the Processing Agent.
    It listens for 'data_ready' messages.
    """

    def __init__(self):
        super().__init__(agent_type='PROCESSING', subscription_queue='processing_agent')

    def on_message(self, frame):
        """
        Handles incoming workflow messages (data_ready, run_imminent, start_run, end_run).
        """
        self.logger.info("Processing Agent received message")
        try:
            message_data = json.loads(frame.body)
            msg_type = message_data.get('msg_type')
            
            if msg_type == 'data_ready':
                self.handle_data_ready(message_data)
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
        """Handle run_imminent message - prepare for processing tasks"""
        run_id = message_data.get('run_id')
        self.logger.info("Processing run_imminent message", 
                        extra={"run_id": run_id, "simulation_tick": message_data.get('simulation_tick')})
        
        # TODO: Initialize processing resources for this run
        # TODO: Call monitor API to register processing tasks
        
        # Simulate preparation
        self.logger.info("Prepared processing resources for run", extra={"run_id": run_id})

    def handle_start_run(self, message_data):
        """Handle start_run message - run is starting physics"""
        run_id = message_data.get('run_id')
        self.logger.info("Processing start_run message", 
                        extra={"run_id": run_id, "simulation_tick": message_data.get('simulation_tick')})
        
        # TODO: Start monitoring for data_ready messages
        self.logger.info("Ready to process data for run", extra={"run_id": run_id})

    def handle_end_run(self, message_data):
        """Handle end_run message - run has ended"""
        run_id = message_data.get('run_id')
        total_files = message_data.get('total_files', 0)
        self.logger.info("Processing end_run message", 
                        extra={"run_id": run_id, "total_files": total_files, "simulation_tick": message_data.get('simulation_tick')})
        
        # TODO: Finalize processing tasks for this run
        # TODO: Update monitor API with final processing statistics
        self.logger.info("Processing complete for run", extra={"run_id": run_id, "total_files": total_files})

    def handle_data_ready(self, message_data):
        """Handle data_ready message - process STF file"""
        filename = message_data.get('filename')
        run_id = message_data.get('run_id')
        file_url = message_data.get('file_url')
        checksum = message_data.get('checksum')
        size_bytes = message_data.get('size_bytes')
        processed_by = message_data.get('processed_by')
        
        self.logger.info("Processing STF data", 
                        extra={"filename": filename, "run_id": run_id, "size_bytes": size_bytes,
                              "processed_by": processed_by, "simulation_tick": message_data.get('simulation_tick')})
        
        # TODO: Download STF file from file_url
        # TODO: Run reconstruction/analysis algorithms 
        # TODO: Create output files (DST, histograms, etc.)
        # TODO: Register output files with Rucio
        # TODO: Call monitor API to update workflow status
        
        # Simulate processing time (longer than data agent)
        import time
        time.sleep(0.5)  # Simulate compute-intensive processing
        
        # Send processing_complete message
        processing_complete_message = {
            "msg_type": "processing_complete",
            "filename": filename,
            "run_id": run_id,
            "input_file_url": file_url,
            "input_checksum": checksum,
            "input_size_bytes": size_bytes,
            "output_files": [
                f"{filename.replace('.dat', '.dst')}",
                f"{filename.replace('.dat', '.hist.root')}"
            ],
            "processing_time_ms": 500,
            "simulation_tick": message_data.get('simulation_tick'),
            "processed_by": self.agent_name
        }
        
        # Send to monitoring/analysis agents
        self.send_message('monitoring_agent', processing_complete_message)
        self.logger.info("Sent processing_complete message", 
                        extra={"filename": filename, "run_id": run_id, "destination": "monitoring_agent"})


if __name__ == "__main__":
    agent = ProcessingAgent()
    agent.run()
