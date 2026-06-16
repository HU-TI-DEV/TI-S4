# Runner Workflow

`Author: Ocarian`

## Overview

The script is responsible for launching the general workflow and running the behaviour manager in a two-phase sequence.

This keeps the Gazebo world active while the behaviour manager restarts into drive mode and enables digging.

---

## How It Works

### Process flow

1. `dig_tile.py` starts and runs continuously.
2. `behaviour_manager.py` runs once for 15 seconds in an initial phase.
3. The initial behaviour manager process stops.
4. `behaviour_manager.py` restarts in drive mode with the POI route.

### Why Gazebo is separate

The runner does not launch Gazebo itself.
Gazebo must already be running because `dig_tile.py` and `behaviour_manager.py` rely on the simulation environment and the interface layer.

Separating Gazebo from the runner ensures that:

* terrain updates from `dig_tile.py` are preserved
* the world scene stays loaded while behaviour control restarts
* no complex gazebo communication issues occur during startup

---

## Usage

Run Gazebo first from the terminal within the /src/environment folder:

```bash
gz sim world.sdf
```

Then start the runner within the /src folder:

```bash
python3 python_runner.py
```

Re-create the heightmap when you're done (you can press enter for default values):

```bash
python3 make_heightmap.py
```

---

## Important Files

| File | Purpose |
|------|---------|
| [python_runner.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/python_runner.py) | Process launcher for `dig_tile.py` and `behaviour_manager.py` |
| [dig_tile.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/dig_tile.py) | Terrain update and digging helper |
| [behaviour_manager.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/behaviour_manager.py) | Behaviour state machine and drive mode logic |
| [poi_route.json](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/poi_route.json) | Point-of-interest route for drive mode |

---

## Assumptions

* Gazebo is running and the `/clock` topic is available.
* `dig_tile.py` refreshes the terrain map from `src/environment/media`.
* The initial behaviour manager run is only to initialize the system before drive mode.
* Drive mode is started using `behaviour_manager.py --state drive --poi-file poi_route.json`.

---

## Notes

* If the environment or process startup order changes, this runner is the first file to update.

## Sources used:

* Borislav Hadzhiev. Run multiple Python files concurrently / one after the other. bobbyhadz. Published April 13, 2024. [https://bobbyhadz.com/blog/how-to-run-multiple-python-files](https://bobbyhadz.com/blog/how-to-run-multiple-python-files)
* Tutorial Reference. How to run multiple Python files concurrently or sequentially in Python. Tutorial Reference. (n.d.). [https://tutorialreference.com/python/examples/faq/python-how-to-run-multiple-python-files-concurrently-or-sequentially ](https://tutorialreference.com/python/examples/faq/python-how-to-run-multiple-python-files-concurrently-or-sequentially )