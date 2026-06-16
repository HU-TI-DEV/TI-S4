# Points of Interest Navigation - Extended Technical Documentation

`Author: GrijzePanda`

## Overview

This feature enables the digger to autonomously navigate to predefined Points of Interest (POIs) within the simulation environment.

A Point of Interest represents a target location in the world that the digger can drive to without user intervention.

The navigation system is responsible for:

* Loading POI locations
* Tracking the current digger position
* Calculating a heading toward a destination
* Steering using a PID controller
* Controlling forward velocity
* Determining when a destination has been reached

POI navigation provides coordinate-based movement only. Higher-level behaviours determine when navigation should begin and which destination should be selected.

---

# Architecture

The POI navigation system consists of four primary components:

1. Point of Interest definition
2. Pose tracking
3. Point-to-point navigation
4. Route execution

The navigation controller receives a target coordinate and continuously generates drive commands until the destination is reached.

---

# Point of Interest Definition

## Route File

POIs are defined in a JSON configuration file:

```text
src/poi_route.json
````

Example:

```json
[
  {"name": "marker1", "x":  20.0, "y":  20.0},
  {"name": "marker2", "x":   0.0, "y":  20.0},
]
```

Each entry defines:

* A marker name
* An X world coordinate
* A Y world coordinate

Navigation targets are loaded from this file and converted into coordinate pairs for use by the navigation controller.

To modify a route:

* Add entries to create new destinations
* Remove entries to skip destinations
* Reorder entries to change traversal order

The route file is the primary configuration mechanism for POI navigation.

## Visual Markers

Visual marker objects are defined separately within:

```text
world.sdf
```

These markers provide a visual indication of POI locations within the simulation environment.

The navigation system does not query marker locations from Gazebo. Instead, it uses coordinates defined within the route file.

If marker locations are changed within `world.sdf`, the corresponding coordinates must also be updated within the route file.

### Design Decision

Visual markers and navigation targets are intentionally decoupled.

Advantages:

* Simple implementation
* Easy route configuration
* No Gazebo model lookups required

Disadvantages:

* Marker coordinates exist in two locations
* Route definitions and marker positions can become inconsistent

---

## World Boundaries

Boundary walls are used to keep the digger inside the valid navigation area.

The digger can often recover from minor collisions but cannot recover from driving beyond the terrain boundaries. These walls help prevent the vehicle from leaving the navigable area.


---

# Pose Tracking

## Position Source

The navigation system obtains the digger position through Gazebo's dynamic pose information.

Current topic:

```text
/world/starting_environment/dynamic_pose/info
```

`interface.py` subscribes to this topic and stores:

```python
state["pose"]["current_x"]
state["pose"]["current_y"]
```

These values are accessed through:

```python
interface.get_state()
```

The navigation system uses these values to calculate distance and direction to the current target.

Only X and Y coordinates are used.

---

## Heading Source

Heading information is obtained from IMU orientation data.

The navigation controller extracts the current yaw angle from the IMU quaternion and uses it to determine steering corrections.

Navigation commands are only generated once valid pose and heading data become available.

---

# Point-to-Point Navigation

## drive_poi.py

`drive_poi.py` contains the primary POI navigation logic.

Responsibilities include:

* Reading current position
* Calculating distance to a target
* Calculating target heading
* Applying steering corrections
* Controlling forward speed
* Detecting destination arrival

The controller returns linear and angular velocity commands for the digger.

---

## Distance Calculation

For every control cycle:

```text
dx = target_x - current_x
dy = target_y - current_y
```

Distance is calculated using Euclidean distance:

```text
d = √(dx² + dy²)
```

If the distance falls below the configured tolerance, navigation is considered complete.

Current configuration:

```python
POSITION_TOLERANCE = 2.0
```

When the calculated distance falls below this tolerance, the destination is considered reached.

A relatively large tolerance was selected because smaller values caused the digger to spend excessive time attempting to reach an exact coordinate.

---

## Heading Calculation

The desired heading is calculated using:

```text
θ = atan2(dy, dx)
```

The difference between the desired heading and current heading is calculated as a heading error and passed to the steering controller.

---

## PID-Based Steering

The navigation system uses a PID controller for heading control.

The controller is responsible for:

* Turning toward the target
* Correcting heading drift
* Maintaining stable steering behaviour

Navigation logic determines where the digger should go, while steering corrections are delegated to the PID controller.

---

## Speed Control

Forward speed is adjusted according to both heading alignment and target proximity.

### Heading Alignment

Forward speed is reduced when the digger is not facing the target.

This encourages heading correction before significant forward motion occurs.

Large heading errors can reduce forward velocity to zero, allowing the digger to rotate in place.

### Target Proximity

Forward speed is gradually reduced as the digger approaches the destination.

This produces smoother arrivals and reduces overshoot.

Current configuration:

```python
MAX_LINEAR_SPEED = 2.5
```

---

# Multi-Point Navigation

Two route-selection approaches exist within the codebase.

## Ordered Route Execution

The behaviour manager implementation loads destinations from `poi_route.json` and visits them in the order defined within the file.

This is the primary navigation approach used by the current system.

## Nearest-Unvisited Selection

The other implementation selects the nearest unvisited POI by:

1. Reading the current position.
2. Calculating the distance to all unvisited POIs.
3. Selecting the closest destination.

This implementation remains useful as a reference and testing tool but is no longer the primary navigation workflow.

---

# Important Files

| File             | Purpose                                         |
| ---------------- | ----------------------------------------------- |
| [drive_poi.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/drive_poi.py)   | Point-to-point navigation controller            |
| [drive_pid.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/drive_pid.py)   | Heading controller                              |
| [poi_route.json](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/poi_route.json) | POI definitions                                 |
| [interface.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/interface/interface.py)   | Provides pose and IMU data                      |
| [world.sdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/world.sdf)      | Visual marker placement and world configuration |
| [marker.sdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/marker.sdf)     | Marker model definition                         |

## Legacy / Testing Files

| File                   | Purpose                                            |
| ---------------------- | -------------------------------------------------- |
| [navigate.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/navigate.py)          | Earlier nearest-POI navigation prototype           |
| [navigate_to_point.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/tests/navigate_to_point.py) | Earlier standalone point-navigation implementation |
| [pid_heading.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/tests/pid_heading.py)       | Earlier heading-controller implementation          |

Note: These files remain useful as development references, and some behavior might still be dependent on these files, later implementations may choose to refactor them.

---

# Assumptions and Improvement Suggestions

The current implementation assumes:

* POIs are predefined and static.
* Position data is available from Gazebo.
* Heading data is available from the IMU.
* Navigation occurs on a mostly obstacle-free map.
* The digger can physically reach all configured destinations.

Possible Future Improvements:

* Implement obstacle avoidance to improve navigation in more complex environments.
* Explore path-planning algorithms to generate more efficient routes.
* Support route-based navigation instead of relying on direct travel between points.
* Extend navigation to consider additional factors beyond X/Y coordinates.
* Improve position accuracy by refining arrival detection and tolerances.
* Further optimize PID tuning to enhance navigation performance.
* Automate the synchronisation of marker locations and route definitions.
* Add recovery mechanisms to help the digger detect and recover from situations where it becomes stuck.
