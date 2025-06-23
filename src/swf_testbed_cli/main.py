import typer
import shutil
from pathlib import Path
import subprocess

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
        print(f"Created {dest_conf.resolve()}")

@app.command()
def start():
    """
    Starts the testbed services using supervisord.
    """
    print("Starting testbed services...")
    subprocess.run(["supervisorctl", "-c", "supervisord.conf", "start", "all"])

@app.command()
def stop():
    """
    Stops the testbed services.
    """
    print("Stopping testbed services...")
    subprocess.run(["supervisorctl", "-c", "supervisord.conf", "stop", "all"])

@app.command()
def status():
    """
    Checks the status of the testbed services.
    """
    print("Checking testbed status...")
    subprocess.run(["supervisorctl", "-c", "supervisord.conf", "status"])

if __name__ == "__main__":
    app()
