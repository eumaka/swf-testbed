"""
Example Data Agent: Handles STF generation messages.
"""

from base_agent import ExampleAgent
import json
import requests
from datetime import datetime

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
        run_conditions = message_data.get('run_conditions', {})
        self.logger.info("Processing run_imminent message", 
                        extra={"run_id": run_id, "simulation_tick": message_data.get('simulation_tick')})
        
        # Create run record in monitor
        self.create_run_record(run_id, run_conditions)
        
        # TODO: Call Rucio to create dataset for this run
        
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
        
        # Register STF file and workflow with monitor
        self.register_stf_file(message_data)
        
        # TODO: Register STF file with Rucio
        # TODO: Initiate transfer to E1 facilities  
        
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
        
        # Update workflow status
        self.update_workflow_status(filename, 'data_complete', 'data')
        
        self.logger.info("Sent data_ready message", 
                        extra={"filename": filename, "run_id": run_id, "destination": "processing_agent"})


    def create_run_record(self, run_id, run_conditions):
        """Create run record in monitor API"""
        try:
            run_data = {
                "run_number": int(run_id),
                "start_time": datetime.now().isoformat(),
                "run_conditions": run_conditions
            }
            
            response = self._api_request('post', '/runs/', run_data)
            if response:
                self.logger.info("Created run record", extra={"run_id": run_id})
            else:
                self.logger.warning("Failed to create run record", extra={"run_id": run_id})
        except Exception as e:
            self.logger.error("Error creating run record", extra={"run_id": run_id, "error": str(e)})
    
    def register_stf_file(self, message_data):
        """Register STF file and create workflow record"""
        filename = message_data.get('filename')
        run_id = message_data.get('run_id')
        file_url = message_data.get('file_url')
        checksum = message_data.get('checksum')
        size_bytes = message_data.get('size_bytes')
        
        try:
            # First, register the STF file
            stf_data = {
                "run": int(run_id),
                "machine_state": message_data.get('substate', 'physics'),
                "file_url": file_url,
                "file_size_bytes": size_bytes,
                "checksum": checksum,
                "status": "registered",
                "metadata": {
                    "simulation_tick": message_data.get('simulation_tick'),
                    "comment": message_data.get('comment', ''),
                    "start": message_data.get('start'),
                    "end": message_data.get('end')
                }
            }
            
            stf_response = self._api_request('post', '/stf-files/', stf_data)
            
            if stf_response:
                self.logger.info("Registered STF file", extra={"filename": filename, "run_id": run_id})
                
                # Create workflow record
                workflow_data = {
                    "filename": filename,
                    "daq_state": message_data.get('state', 'run'),
                    "daq_substate": message_data.get('substate', 'physics'),
                    "generated_time": datetime.now().isoformat(),
                    "stf_start_time": self._parse_time_string(message_data.get('start')),
                    "stf_end_time": self._parse_time_string(message_data.get('end')),
                    "current_status": "data_received",
                    "current_agent": "data",
                    "stf_metadata": message_data
                }
                
                workflow_response = self._api_request('post', '/workflows/', workflow_data)
                
                if workflow_response:
                    self.logger.info("Created STF workflow", extra={"filename": filename})
                else:
                    self.logger.warning("Failed to create STF workflow", extra={"filename": filename})
            else:
                self.logger.warning("Failed to register STF file", extra={"filename": filename})
                
        except Exception as e:
            self.logger.error("Error registering STF file", extra={"filename": filename, "error": str(e)})
    
    def update_workflow_status(self, filename, status, agent_type):
        """Update workflow status after processing"""
        try:
            # This would typically require getting the workflow ID first
            # For now, we'll log the status change
            self.logger.info("Workflow status updated", 
                           extra={"filename": filename, "status": status, "agent": agent_type})
        except Exception as e:
            self.logger.error("Error updating workflow status", 
                            extra={"filename": filename, "error": str(e)})
    
    def _parse_time_string(self, time_str):
        """Parse time string from DAQ simulator format to ISO format"""
        if not time_str:
            return datetime.now().isoformat()
        try:
            # Convert from format like '20250801143000' to ISO format
            dt = datetime.strptime(time_str, '%Y%m%d%H%M%S')
            return dt.isoformat()
        except:
            return datetime.now().isoformat()


if __name__ == "__main__":
    agent = DataAgent()
    agent.run()
