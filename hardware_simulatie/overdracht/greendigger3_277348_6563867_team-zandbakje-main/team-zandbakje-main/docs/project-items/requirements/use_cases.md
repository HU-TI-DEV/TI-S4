# Use Cases

`Authors: Ocarian, Replitard, GrijzePanda, ShelleKjell` 

## UC-01: Report Digger Status

### Goal
The digger provides status and sensor data to the system.
### Primary Actor
System / Operator
### Trigger
The digger is active in the simulation.
### Preconditions
- The digger is running
- Sensors are active
- Communication is available
### Main Flow
1. The digger sends status information to topic.
2. Operator subscribes to topic.
### Postconditions
- The operator has the sensor data.
### Related Requirements
- F-001
- NF-001


## UC-02: Detect Local Obstacle

### Goal
The digger detects obstacles in its direct surroundings.
### Primary Actor
Digger
### Trigger
The digger moves or scans the environment.
### Preconditions
- LIDAR or obstacle sensors are active
- The digger is operational
### Main Flow
1. The digger scans the local environment.
2. The digger identifies a possible obstacle.
3. The obstacle is classified as relevant or not relevant.
4. The detection result is stored or reported.
### Postconditions
- Nearby obstacle is detected and known to the system
### Related Requirements
- F-002
- F-012
- NF-002
- NF-012


## UC-03: Avoid Obstacle While Driving

### Goal
The digger avoids a detected obstacle during movement.
### Primary Actor
Digger
### Trigger
An obstacle is detected on the current route.
### Preconditions
- An obstacle has been detected
- Locomotion is available
### Main Flow
1. The digger determines a safe avoidance maneuver.
2. The digger changes its route.
3. The digger continues driving while keeping safe distance.
### Alternate Flows
- If avoidance is not possible, the digger drives back and reroutes.
- If excavation was planned, the digger skips that section.
### Postconditions
- The obstacle is avoided or the route is safely interrupted
### Related Requirements
- F-004
- F-008
- F-011
- NF-004
- NF-008
- NF-011


## UC-04: Localize Relative to Target or World Origin

### Goal
The digger determines its own position.
### Primary Actor
Digger
### Trigger
The digger starts up or receives a movement task.
### Preconditions
- Localization data is available
- Simulation world is active
### Main Flow
1. The digger reads localization data.
2. The digger calculates its current position.
3. The digger compares its position to the target or world origin.
4. The digger updates its internal state.
### Postconditions
- The digger knows its current position
### Related Requirements
- F-003
- NF-003

## UC-05: Execute Digging Pattern

### Goal
The digger performs a standard excavation movement pattern.
### Primary Actor
Digger
### Trigger
A digging command or digging location is available.
### Preconditions
- The digger is at the correct position
- Excavation control is available
- The terrain is valid enough to continue
### Main Flow
1. The digger starts the digging sequence.
2. The digger performs the required movement pattern.
3. The digger finishes the excavation step.
### Alternate Flows
- If terrain is uneven, stance compensation is applied.
- If an obstacle is detected, the section is skipped.
### Postconditions
- The digging pattern has been executed or skipped safely
### Related Requirements
- F-006
- F-007
- F-008
- NF-006
- NF-007
- NF-008

## UC-06: Manually Control Actuators

### Goal
The operator directly controls the digger.
### Primary Actor
Operator
### Trigger
The operator gives manual keyboard input.
### Preconditions
- Manual control mode is enabled
- The digger is connected to Gazebo input handling
### Main Flow
1. The operator presses a control key.
2. The system interprets the input.
3. The digger receives the actuator command.
4. The digger performs the requested movement.
### Postconditions
- The digger responds to manual input
### Related Requirements
- F-009
- NF-009


## UC-07: Follow Planned Path

### Goal
The digger follows a planned route through the environment.
### Primary Actor
Digger
### Trigger
A path or route is available.
### Preconditions
- The digger is localized
- Locomotion is available
- A path exists
### Main Flow
1. The digger receives or generates a path.
2. The digger starts driving toward the next point.
3. The digger updates its position while moving.
4. The digger continues until the path is completed.
### Alternate Flows
- The digger replans when an obstacle is detected.
- The digger stops when the path becomes invalid.
### Postconditions
- The path is completed or interrupted safely
### Related Requirements
- F-005
- F-010
- F-011
- NF-005
- NF-010
- NF-011