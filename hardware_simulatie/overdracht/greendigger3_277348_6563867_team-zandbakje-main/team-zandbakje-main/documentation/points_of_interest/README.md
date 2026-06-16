# Points of Interest Navigation - Overview and Handover

`Author: GrijzePanda`

## Overview

This feature enables the digger to autonomously navigate to predefined Points of Interest (POIs) within the simulation environment.

POIs are represented by world coordinates stored in a route file. The navigation system drives the digger from one destination to the next using position data from Gazebo and heading control provided by a PID controller.

The current implementation is integrated into the behaviour manager and is used as part of the digger's autonomous operation.

---

# How It Works

The system consists of four main parts:

### 1. Route Definition

POIs are defined in:

```text
src/poi_route.json
```

Each entry contains:

* A name
* An X coordinate
* A Y coordinate

The order of entries determines the order in which destinations are visited.

Visual marker objects also exist in the simulation world, but navigation uses the coordinates defined in the route file rather than querying marker locations from Gazebo.

---

### 2. Pose Tracking

The digger position is obtained from Gazebo through `interface.py`.

The navigation system uses:

* Current X position
* Current Y position
* Current heading (IMU)

These values are used to calculate the direction and distance to the current destination.

---

### 3. Navigation Controller

`drive_poi.py` performs point-to-point navigation.

Responsibilities:

* Calculate distance to target
* Calculate desired heading
* Apply PID steering corrections
* Control forward speed
* Determine when a destination has been reached

Forward speed is automatically reduced when:

* The digger is not facing the target
* The digger is approaching the destination

---

### 4. Route Execution

The behaviour manager loads the route file and visits each POI in sequence.

Example:

```bash
python3 code/src/behaviour_manager.py --state drive --poi-file poi_route.json
```

Other behaviours (such as digging) may be executed after arriving at a destination before continuing to the next POI.

---

# Important Files

| File             | Purpose                              |
| ---------------- | ------------------------------------ |
| [drive_poi.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/drive_poi.py)   | Point-to-point navigation controller |
| [drive_pid.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/drive_pid.py)   | PID heading controller               |
| [poi_route.json](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/poi_route.json) | POI route definition                 |
| [interface.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/interface/interface.py)   | Provides pose and IMU data           |
| [world.sdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/world.sdf)      | Visual marker placement              |
| [marker.sdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/marker.sdf)     | Marker model definition              |

---

# Current Assumptions

The implementation currently assumes:

* POIs are predefined and static.
* Navigation occurs on a mostly obstacle-free map.
* Position data comes from Gazebo.
* Heading data comes from the IMU.
* The digger can physically reach all configured destinations.

---

# Possible Future Improvements

* Implement obstacle avoidance to handle objects in the environment.
* Explore path-planning algorithms for more efficient navigation.
* Support navigation using planned routes instead of direct travel between destinations.
* Extend navigation to account for additional factors beyond X/Y position.
* Automate the synchronisation of marker locations and route definitions.
* Further tune or improve the navigation controller for better performance.
* Investigate ways to detect and recover when the digger becomes stuck.


---

# Additional Documentation

This document provides a high-level overview of the POI navigation feature.

For a detailed explanation of the architecture, navigation algorithms, route configuration, pose tracking, PID integration, and implementation details, see: [Points of Interest Navigation - Extended Technical Documentation](TECHNICAL_DOCUMENTATION.md)
