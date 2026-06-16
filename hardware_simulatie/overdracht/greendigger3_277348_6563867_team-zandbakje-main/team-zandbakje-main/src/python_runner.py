"""Simple runner for the GreenDigger process flow.

This script starts the terrain-digging helper and then runs the behaviour manager in
two phases: an initial warmup phase and a drive mode phase.

Gazebo is intentionally launched separately. The runner assumes the simulation is already
running before it starts `dig_tile.py` and `behaviour_manager.py`.

    Author: Ocarian
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Paths used by the runner
SRC = Path(__file__).parent.resolve()
ENV = SRC / "environment"
DIG_TILE = SRC / "dig_tile.py"
BEHAVIOUR = SRC / "behaviour_manager.py"
POI_FILE = SRC / "poi_route.json"

# Runner configuration
INITIAL_DURATION_S = 15.0
PAUSE_AFTER_INITIAL_S = 1.0


def stop_process(proc, name):
    """Terminate a running process and wait for it to exit, with a timeout"""
    print(f"Stopping {name}...")
    proc.terminate()
    proc.wait(timeout=5)


def run_behaviour(parts):
    """Start the behaviour manager with a list of command arguments"""
    return subprocess.Popen(parts, env=get_runner_env())


def get_runner_env():
    """Return the environment with Gazebo resource path adjustments"""
    env = os.environ.copy()
    env["GZ_SIM_RESOURCE_PATH"] = str(ENV) + ":" + env.get("GZ_SIM_RESOURCE_PATH", "")
    return env


def main() -> int:
    """Run the process workflow"""
    print("Starting dig_tile.py")
    dig_tile = subprocess.Popen([sys.executable, str(DIG_TILE)], env=get_runner_env())

    print(f"Starting behaviour_manager.py for {INITIAL_DURATION_S} seconds")
    initial_behaviour = run_behaviour(
        [
            sys.executable,
            str(BEHAVIOUR),
            "--duration-s",
            str(INITIAL_DURATION_S),
        ]
    )
    initial_behaviour.wait()
    print("Initial behaviour_manager.py run complete")

    time.sleep(PAUSE_AFTER_INITIAL_S)

    print("Starting behaviour_manager.py drive mode")
    drive_behaviour = run_behaviour(
        [
            sys.executable,
            str(BEHAVIOUR),
            "--state",
            "drive",
            "--poi-file",
            str(POI_FILE),
        ]
    )

    try:
        drive_behaviour.wait()
    except KeyboardInterrupt:
        print("Keyboard interrupt received; stopping drive behaviour")
        stop_process(drive_behaviour, "behaviour_manager.py (drive mode)")
    finally:
        stop_process(dig_tile, "dig_tile.py")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
