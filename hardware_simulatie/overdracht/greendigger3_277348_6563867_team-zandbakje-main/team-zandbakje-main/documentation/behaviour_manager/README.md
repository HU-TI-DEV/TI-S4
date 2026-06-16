# Behaviour Manager 

`Author: Replitard`

## Overview
The behaviour manager is responsible for decision making. It coordinates all logic modules, such as navigation, digging, and perception. And it calls upon these modules to execute a given task, based on conditions that are given.

It sits in the `/src` of the project architecture and communicates exclusively through the interface layer. It does not talk to Gazebo directly.

The current implementation drives the digger through a sequence of Points of Interest and performs a dig sequence at each stop. And when the digger is done, it returns to idle.

---

## How It Works

### State Machine
The `BehaviourManager` class runs a loop that calls `step()` at a fixed interval to pull the current sensor state from `interface.py`, and dispatches to the active state handler.

Available states:

| State | Description |
|-------|-------------|
| `manual` | Disables active decision making. Used for keyboard control. |
| `idle` | Stops the digger and resets the arm to its out-of-the-way pose. |
| `drive` | Navigates to a target using POI driving, heading PID, or raw speed. |
| `dig` | Executes the full dig sequence at the current location, then advances. |
| `error` | Stops all movement when a blocking condition is detected (e.g. chassis contact). |

State transitions happen inside the step loop. For example, when the digger reaches a POI in `drive`, it transitions to `dig`. When the dig completes, it advances to the next POI or falls back to `idle` when the list of POI's is exhausted.  
by default, the digger sits in the idle state.  

---

### Drive Modes
The `drive` state currently supports three modes, selected by the arguments passed at startup.

* **POI route** (`--poi-file`): loads a JSON file of destinations and drives through them in order.
* **Single target** (`--target-x`, `--target-y`): drives to one coordinate and then idles.
* **Heading hold** (`--target-heading-degrees`): uses the PID controller to orient to a fixed heading.
* **Raw drive** (default fallback): publishes the configured linear and angular speeds directly.

`drive_poi.py` handles point-to-point navigation in order of the json list provided.  
`drive_pid.py` handles heading correction.  
`navigate.py` handles point-to-point navigation based on which point is the closest to the digger. Currently not implemented, but it's ready for stand-alone use.

---

### Dig Sequence
When the digger enters the `dig` state.

1. Drive is stopped.
2. If `--dig-heading-degrees` is set, the digger rotates to that heading with a 10 degree margine of error before digging.
3. `dig_halfmoon.dig_halfmoon()` executes the full arm movement sequence.
4. The manager advances to the next POI, or idles if the route is complete.

---

## Running the Behaviour Manager
Start Gazebo with the digger world loaded and playing, then run from the project root directory.

```bash
# Idle (default)
python3 src/behaviour_manager.py

# Drive through a POI route and dig at each stop
python3 src/behaviour_manager.py --state drive --poi-file src/poi_route.json

# Drive to a single coordinate
python3 src/behaviour_manager.py --state drive --target-x 10.0 --target-y 5.0

# Hold a heading
python3 src/behaviour_manager.py --state drive --target-heading-degrees 90.0
```

Optional flags for testing:

| Flag | Default | Description |
|------|---------|-------------|
| `--state` | `idle` | Initial state |
| `--duration-s` | none | Stop after this many seconds |
| `--period-s` | `0.1` | Time between behaviour steps |
| `--drive-linear-x` | `0.5` | Forward speed for raw drive |
| `--drive-angular-z` | `0.0` | Turn speed for raw drive |
| `--dig-heading-degrees` | `90.0` | Heading to face before each dig |

---

## Important Files

| File | Purpose |
|------|---------|
| [behaviour_manager.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/behaviour_manager.py) | State machine and entry point |
| [drive_poi.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/drive_poi.py) | Point-to-point navigation |
| [drive_pid.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/drive_pid.py) | PID heading controller |
| [dig_halfmoon.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/dig_halfmoon.py) | Arm dig sequence |
| [poi_route.json](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/poi_route.json) | POI route definition |
| [interface/interface.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/interface/interface.py) | Sensor data and command publishing |

---

## Current Assumptions
Since it's not entirely complete, there are some assumptions during testing that have to be made.

* The interface layer is running and subscribed before `step()` is called.
* POIs are static and reachable without obstacle avoidance.
* Chassis contact always indicates a problem worth stopping for.
* The dig heading enforcement is a temporary workaround to make sure the bunds are all facing down. 

---

## Known Limitations
* No obstacle avoidance; the digger will stop on chassis contact but cannot route around it, and there is nothing to call it out of the error state until another state is enforced.
* Heading enforcement before digging is a temporary fix, not a proper alignment system. Later down the line, this enforcement will be based on chassis tilt using a sensor, instead of a hardcoded direction based on simulation pose.
* The `manual` state is a stub — it does nothing yet because they keyboard logic is still external and in test.
* `--dig-heading-degrees` is always applied before every dig, regardless of current heading.

---

## Additional Documentation
For a detailed explanation of the project layer architecture, data flow, and how the behaviour manager fits into the rest of the system, see: [Architecture](../../docs/project-items/project-style/architecture.md)

For navigation details, see: [Points of Interest Navigation](../points_of_interest/README.md)
For interface details, see: [Digger Interface](../interface/README.md)

---

## Sources used:

- argparse — Parser for command-line options, arguments and subcommands. (n.d.). Python Documentation. https://docs.python.org/3/library/argparse.html
- GeeksforGeeks. (2026, May 23). Read JSON file using Python. GeeksforGeeks. https://www.geeksforgeeks.org/python/read-json-file-using-python/
- 9. classes. (n.d.). Python Documentation. https://docs.python.org/3/tutorial/classes.html
- W3Schools.com. (n.d.). https://www.w3schools.com/python/python_oop.asp