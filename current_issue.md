# Summary of Current Issue: `example_daqsim_agent.py` Hangs on Connection

## 1. High-Level Goal

The objective is to create a set of standalone, example agents in the `swf-testbed/example_agents/` directory. These agents should serve as a blueprint for real agents, communicating with the `swf-monitor` application via its REST API for logging/heartbeats and with ActiveMQ for messaging.

We began by implementing the `example_daqsim_agent.py` as the first example.

## 2. The Problem

The `example_daqsim_agent.py` script hangs indefinitely when executed. The script successfully starts, but it never proceeds past the ActiveMQ connection logic, and no errors are printed to the console.

## 3. Current State of the Code

### `swf-monitor` Repository (`infra/baseline-v10` branch)
- A REST API has been established at `/api/v1/`.
- Endpoints exist for `/logs/` and `/systemagents/`.
- The `/systemagents/heartbeat/` endpoint was created to allow agents to register/update their status.
- The API requires token authentication. A user `gemini` with token `39a564f5d3a2952813affa2146b9f4f6587e5273` was created for testing.
- The API and its authentication have been successfully tested with `curl`.

### `swf-testbed` Repository (`infra/baseline-v10` branch)
- A new directory `example_agents/` has been created.
- `base_agent.py`: Contains a reusable `ExampleAgent` class to handle common logic.
- `example_daqsim_agent.py`: A simple agent that inherits from `ExampleAgent`. Its purpose is to connect to ActiveMQ and (eventually) produce messages.
- `requirements.txt`: Contains `requests` and `stomp.py`.

## 4. Debugging Steps Taken & Results

The following steps were taken to diagnose the hanging issue:

1.  **Initial Run (Background):** The script was run in the background. **Result:** The agent never appeared in the API's list of system agents. No logs were visible.
2.  **Foreground Run:** The script was run in the foreground to observe errors. **Result:** The script hangs silently with no output and must be manually interrupted.
3.  **Verify ActiveMQ Service:** Checked if the ActiveMQ Docker container was running using `docker ps`. **Result:** The container is running correctly.
4.  **Verify Port Accessibility:** Used `nc -zv localhost 61616` to check if the STOMP port was open. **Result:** The port is open and the connection succeeds, ruling out firewall or port mapping issues.
5.  **Add STOMP Heartbeats:** Modified `base_agent.py` to include `heartbeats=(10000, 10000)` in the `stomp.Connection` constructor, as a lack of heartbeating is a common cause of hangs. **Result:** The script still hangs.

## 5. Current Hypothesis

- The issue is not with the `swf-monitor` API or basic network connectivity.
- The problem lies specifically within the `stomp.py` connection logic in `base_agent.py`.
- The hang occurs at the `self.conn.connect(self.mq_user, self.mq_password, wait=True)` line.
- Since heartbeats did not solve it, the issue is likely a more subtle STOMP protocol-level problem (e.g., a version mismatch, an issue with vhost, or another parameter disagreement between the client and the Artemis broker) that is causing the handshake to never complete.

## 6. Last Proposed Action

My last action before being stopped was to propose enabling the `stomp.py` library's internal debug logging to print the raw STOMP frames being sent and received. This would provide a low-level view of the handshake and reveal exactly where it is failing.
