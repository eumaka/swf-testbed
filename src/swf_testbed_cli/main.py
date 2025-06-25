import typer
import shutil
from pathlib import Path
import subprocess
import os
import psutil

app = typer.Typer()

SUPERVISORD_CONF_TEMPLATE = Path(__file__).parent.parent.parent / "supervisord.conf"

@app.command()
def init():
    """
    Initializes the testbed environment by creating a supervisord.conf file
    and a logs directory.
    """
    print("Initializing testbed environment...")

    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print(f"Created directory: {logs_dir.resolve()}")

    # Copy supervisord.conf
    dest_conf = Path("supervisord.conf")
    if dest_conf.exists():
        print(f"{dest_conf} already exists. Skipping.")
    else:
        shutil.copy(SUPERVISORD_CONF_TEMPLATE, dest_conf)
        print(f"Created {dest_conf}")

@app.command()
def start():
    """
    Starts the testbed services using supervisord and docker compose.
    """
    print("Starting testbed services...")
    print("--- Starting Docker services ---")
    subprocess.run(["docker", "compose", "up", "-d"])
    print("--- Starting supervisord services ---")
    subprocess.run(["supervisorctl", "-c", "supervisord.conf", "start", "all"])

@app.command()
def stop():
    """
    Stops the testbed services.
    """
    print("Stopping testbed services...")
    print("--- Stopping supervisord services ---")
    subprocess.run(["supervisorctl", "-c", "supervisord.conf", "stop", "all"])
    print("--- Stopping Docker services ---")
    subprocess.run(["docker", "compose", "down"])

@app.command()
def status():
    """
    Checks the status of the testbed services.
    """
    print("--- Docker services status ---")
    subprocess.run(["docker", "compose", "ps"])
    print("\n--- supervisord services status ---")
    subprocess.run(["supervisorctl", "-c", "supervisord.conf", "status"])

def _check_process_running(process_name: str) -> bool:
    """Checks if a process with the given name is running."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False

def _check_postgres_connection():
    """Checks the connection to the PostgreSQL database."""
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USER", "admin")
    db_name = os.getenv("DB_NAME", "swfdb")

    print(f"--- Checking PostgreSQL connection at {db_host}:{db_port} ---")
    try:
        result = subprocess.run(
            ["pg_isready", "-h", db_host, "-p", db_port, "-U", db_user, "-d", db_name],
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout.strip())
        if "accepting connections" not in result.stdout:
            print("Warning: PostgreSQL is not ready.")
            return False
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error checking PostgreSQL status: {e}")
        print("Please ensure PostgreSQL is running and `pg_isready` is in your PATH.")
        return False

def _check_activemq_connection():
    """Checks if ActiveMQ is listening on its port."""
    amq_port = os.getenv("ACTIVEMQ_PORT", "61616")
    print(f"--- Checking ActiveMQ connection on port {amq_port} ---")
    result = subprocess.run(f"lsof -i -P -n | grep LISTEN | grep ':{amq_port}'", shell=True, capture_output=True)
    if result.returncode == 0:
        print(f"ActiveMQ appears to be running and listening on port {amq_port}.")
        return True
    else:
        print(f"Warning: Could not detect a service listening on port {amq_port}.")
        print("Please ensure ActiveMQ is running.")
        return False

@app.command("start-local")
def start_local():
    """
    Starts the local testbed services using supervisord.
    """
    print("Starting local testbed services...")

    db_ok = _check_postgres_connection()
    amq_ok = _check_activemq_connection()

    if not db_ok or not amq_ok:
        print("\nError: One or more background services are not available. Aborting.")
        raise typer.Abort()

    print("\n--- Starting supervisord services ---")
    if not _check_process_running("supervisord"):
        print("supervisord is not running, starting it now...")
        subprocess.run(["supervisord", "-c", "supervisord.conf"])
    else:
        print("supervisord is already running.")
    
    subprocess.run(["supervisorctl", "-c", "supervisord.conf", "start", "all"])

@app.command("stop-local")
def stop_local():
    """
    Stops the local testbed services.
    """
    print("--- Stopping local supervisord services ---")
    subprocess.run(["supervisorctl", "-c", "supervisord.conf", "stop", "all"])
    # Optionally, shutdown supervisord itself
    # subprocess.run(["supervisorctl", "-c", "supervisord.conf", "shutdown"])

@app.command("status-local")
def status_local():
    """
    Checks the status of the locally running testbed services.
    """
    print("--- Local services status ---")
    _check_postgres_connection()
    _check_activemq_connection()
    print("\n--- supervisord services status ---")
    # Check if supervisord is running
    if _check_process_running("supervisord"):
        print("supervisord is running.")
        subprocess.run(["supervisorctl", "-c", "supervisord.conf", "status"])
    else:
        print("supervisord is not running.")

if __name__ == "__main__":
    app()
