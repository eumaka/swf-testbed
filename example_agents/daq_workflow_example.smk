# EXAMPLE ONLY - NOT USED BY TESTBED
# ====================================
# This Snakemake file demonstrates how a DAQ workflow could be expressed in Snakemake format.
# However, the actual testbed uses SimPy directly for DAQ simulation (see daq_simulator.py).
# 
# We explored using Snakemake but decided that SimPy provides better discrete event simulation
# capabilities without requiring a complex Snakemake-to-SimPy translator.
#
# Original description:
# DAQ State Machine Workflow
# This simulates ePIC DAQ state transitions with programmatic STF generation

# Configuration
RUN_NUMBER = "100001"
STF_INTERVAL_SECONDS = 30  # STFs generated every 30 seconds during run/physics

# State 1: no_beam / not_ready (starting state)
rule initial_state:
    output:
        state="daq_states/01_no_beam_not_ready.json"
    params:
        duration_minutes=5,
        state="no_beam",
        substate="not_ready"
    shell:
        """
        echo "DAQ State: no_beam/not_ready - Collider not operating"
        mkdir -p daq_states
        cat > {output.state} << EOF
{{
    "state": "{params.state}",
    "substate": "{params.substate}",
    "timestamp": "$(date -Iseconds)",
    "duration_minutes": {params.duration_minutes},
    "description": "Collider not operating"
}}
EOF
        sleep 2  # Brief pause for simulation
        """

# State 2: beam / not_ready 
rule beam_not_ready:
    input:
        prev_state="daq_states/01_no_beam_not_ready.json"
    output:
        state="daq_states/02_beam_not_ready.json",
        run_imminent="daq_events/run_{run}_imminent.json".format(run=RUN_NUMBER)
    params:
        duration_minutes=5,
        state="beam", 
        substate="not_ready",
        run_number=RUN_NUMBER
    shell:
        """
        echo "DAQ State: beam/not_ready - Beam on, run start imminent"
        mkdir -p daq_events
        
        cat > {output.state} << EOF
{{
    "state": "{params.state}",
    "substate": "{params.substate}",
    "timestamp": "$(date -Iseconds)",
    "duration_minutes": {params.duration_minutes},
    "description": "Beam operating, detector not ready"
}}
EOF

        # Broadcast run imminent message
        cat > {output.run_imminent} << EOF
{{
    "msg_type": "run_imminent",
    "run_id": "{params.run_number}",
    "timestamp": "$(date -Iseconds)",
    "run_conditions": {{
        "beam_energy": "5 GeV",
        "magnetic_field": "1.5T",
        "detector_config": "physics",
        "bunch_structure": "216x216"
    }}
}}
EOF
        sleep 2
        """

# State 3: beam / ready
rule beam_ready:
    input:
        prev_state="daq_states/02_beam_not_ready.json"
    output:
        state="daq_states/03_beam_ready.json"
    params:
        duration_minutes=1,
        state="beam",
        substate="ready"
    shell:
        """
        echo "DAQ State: beam/ready - Ready for physics declaration"
        cat > {output.state} << EOF
{{
    "state": "{params.state}",
    "substate": "{params.substate}",
    "timestamp": "$(date -Iseconds)",
    "duration_minutes": {params.duration_minutes},
    "description": "Collider and detector ready, awaiting physics declaration"
}}
EOF
        sleep 2
        """

# State 4: run / physics (first period) - triggers run start + STF generation
rule run_physics_1:
    input:
        prev_state="daq_states/03_beam_ready.json"
    output:
        state="daq_states/04_run_physics_1.json",
        run_start="daq_events/run_{run}_start.json".format(run=RUN_NUMBER),
        stf_trigger="daq_triggers/physics_period_1.trigger"
    params:
        duration_minutes=5,
        state="run",
        substate="physics",
        run_number=RUN_NUMBER,
        stf_interval=STF_INTERVAL_SECONDS
    shell:
        """
        echo "DAQ State: run/physics (period 1) - Physics datataking active"
        mkdir -p daq_triggers
        
        cat > {output.state} << EOF
{{
    "state": "{params.state}",
    "substate": "{params.substate}",
    "timestamp": "$(date -Iseconds)",
    "duration_minutes": {params.duration_minutes},
    "description": "Physics datataking period 1",
    "stf_generation": true,
    "stf_interval_seconds": {params.stf_interval}
}}
EOF

        # Broadcast run start
        cat > {output.run_start} << EOF
{{
    "msg_type": "start_run",
    "run_id": "{params.run_number}",
    "timestamp": "$(date -Iseconds)",
    "state": "{params.state}",
    "substate": "{params.substate}"
}}
EOF

        # Create trigger for programmatic STF generation (SimPy will use this)
        cat > {output.stf_trigger} << EOF
{{
    "run_id": "{params.run_number}",
    "physics_period": 1,
    "start_time": "$(date -Iseconds)",
    "duration_minutes": {params.duration_minutes},
    "stf_interval_seconds": {params.stf_interval},
    "state": "{params.state}",
    "substate": "{params.substate}"
}}
EOF
        sleep 2
        """

# State 5: run / standby
rule run_standby:
    input:
        prev_state="daq_states/04_run_physics_1.json"
    output:
        state="daq_states/05_run_standby.json"
    params:
        duration_seconds=30,
        state="run",
        substate="standby"
    shell:
        """
        echo "DAQ State: run/standby - Brief standby period"
        cat > {output.state} << EOF
{{
    "state": "{params.state}",
    "substate": "{params.substate}",
    "timestamp": "$(date -Iseconds)",
    "duration_seconds": {params.duration_seconds},
    "description": "Brief standby, no STF generation"
}}
EOF
        sleep 2
        """

# State 6: run / physics (second period)
rule run_physics_2:
    input:
        prev_state="daq_states/05_run_standby.json"
    output:
        state="daq_states/06_run_physics_2.json",
        stf_trigger="daq_triggers/physics_period_2.trigger"
    params:
        duration_minutes=3,  # Shorter second period
        state="run",
        substate="physics",
        run_number=RUN_NUMBER,
        stf_interval=STF_INTERVAL_SECONDS
    shell:
        """
        echo "DAQ State: run/physics (period 2) - Physics datataking resumed"
        cat > {output.state} << EOF
{{
    "state": "{params.state}",
    "substate": "{params.substate}",
    "timestamp": "$(date -Iseconds)",
    "duration_minutes": {params.duration_minutes},
    "description": "Physics datataking period 2",
    "stf_generation": true,
    "stf_interval_seconds": {params.stf_interval}
}}
EOF

        # Create trigger for second physics period STF generation
        cat > {output.stf_trigger} << EOF
{{
    "run_id": "{params.run_number}",
    "physics_period": 2,
    "start_time": "$(date -Iseconds)", 
    "duration_minutes": {params.duration_minutes},
    "stf_interval_seconds": {params.stf_interval},
    "state": "{params.state}",
    "substate": "{params.substate}"
}}
EOF
        sleep 2
        """

# State 7: beam / not_ready (run ended)
rule beam_not_ready_end:
    input:
        prev_state="daq_states/06_run_physics_2.json"
    output:
        state="daq_states/07_beam_not_ready_end.json",
        run_end="daq_events/run_{run}_end.json".format(run=RUN_NUMBER)
    params:
        duration_minutes=3,
        state="beam",
        substate="not_ready",
        run_number=RUN_NUMBER
    shell:
        """
        echo "DAQ State: beam/not_ready - Run ended, shifters stopped datataking"
        cat > {output.state} << EOF
{{
    "state": "{params.state}",
    "substate": "{params.substate}",
    "timestamp": "$(date -Iseconds)",
    "duration_minutes": {params.duration_minutes},
    "description": "Run ended by shifters"
}}
EOF

        # Broadcast run end
        cat > {output.run_end} << EOF
{{
    "msg_type": "end_run",
    "run_id": "{params.run_number}",
    "timestamp": "$(date -Iseconds)",
    "total_physics_periods": 2
}}
EOF
        sleep 2
        """

# State 8: no_beam / not_ready (final state)
rule final_state:
    input:
        prev_state="daq_states/07_beam_not_ready_end.json"
    output:
        state="daq_states/08_no_beam_not_ready_final.json"
    params:
        state="no_beam",
        substate="not_ready"
    shell:
        """
        echo "DAQ State: no_beam/not_ready - Collider shutdown, cycle complete"
        cat > {output.state} << EOF
{{
    "state": "{params.state}",
    "substate": "{params.substate}",
    "timestamp": "$(date -Iseconds)",
    "description": "Collider not operating, DAQ cycle complete"
}}
EOF
        """

# Complete realistic DAQ cycle
rule all:
    input:
        "daq_states/08_no_beam_not_ready_final.json"