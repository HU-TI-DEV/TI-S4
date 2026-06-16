# ArmCoordinatenMovement

Low-level joint control and state tracking layer for the **Nautilus** robotic arm. Manages individual joint kinematics limitations, running standalone PID control loops, and maintaining hardware/simulation synchronisation via Gazebo transport.

---

## Design Choices

* **PID Decoupling:** Instead of raw position forcing, velocity commands are calculated dynamically using a Proportional Integral Derivative (PID) loop per joint to ensure smooth physical transitions.
* **Thread-Safe State Copies:** The controller enforces a clear boundary between the background execution loop and external API requests by protecting joint resources with dedicated mutexes (`controllerJointsMutex`, `controllerRealPosMutex`) and returning thread-safe copies of joint objects.
* **Configuration-Driven Joints:** Joint limits, names, and Gazebo topic mappings are defined centrally in `JOINT_DEFINITIONS` rather than hardcoded, allowing joint configurations to be added or changed without touching controller logic.
* **Stable Heap Storage for Gazebo Nodes:** Since `gz::transport::Node` is non-copyable and non-movable, publishers and nodes are stored as `std::vector<std::unique_ptr<gz::transport::Node>>` to guarantee stable addresses across the object's lifetime.
---

## Overview

`ArmCoordinatenMovement` consists of `Joint` (representing a single physical or simulated axis) and `JointController` (managing the group lifecycle). It reads target commands (typically sent by an IK solver), compares them against real-time feedback from Gazebo, computes safe output velocities, and streams these commands directly back to the simulator.

---

## Responsibilities

* Subscribes to `/world/robosubSimulationV4/model/robosub/joint_state` to ingest physical telemetry.
* Enforces hardware joint limits by clamping input targets using static structural bounds specified in `JointDefinitions.h`.
* Runs a background thread processing loop at a deterministic interval (`UPDATE_RATE_MS = 100ms`).
* Translates position errors into bounded velocity commands (`MAX_VELOCITY = 5.0 rad/s`) utilizing anti-windup clamped PID tracking.
* Publishes calculated velocity steps over unique Gazebo transport topics per joint.

---

## API

### Lifecycle

```cpp
void start(); // Starts the background PID control loop thread
void stop();  // Stops the control loop thread safely and joins it
bool isRunning();

```

### Motion Control

```cpp
JointController();
```

Constructor calls `initJoints()`, `initPublishers()`, and `initSubscriber()` in sequence, then waits 500ms for Gazebo topic discovery before the control loop starts.

### Control loop

Runs on a background thread at `UPDATE_RATE_MS = 100ms`. Each tick:

1. Syncs `jointCurrentPos` from real Gazebo positions (closed-loop feedback)
2. Calls `updatePosition(elapsed)` on every joint
3. Publishes velocity commands to Gazebo via `publishAll()`

### Closed-loop feedback

Subscribes to `/world/robosubSimulationV4/model/robosub/joint_state`. On each message, matches joint names against `JOINT_DEFINITIONS` and updates `controllerRealPositions`. This is synced into each `Joint` at the start of every control tick.

### Gazebo nodes

`gz::transport::Node` is non-copyable and non-movable . Publishers are stored as `std::vector<gz::transport::Node::Publisher>` with nodes held as `std::vector<std::unique_ptr<gz::transport::Node>>` to keep them at stable heap addresses. [^1], [^2]

### Key methods

| Method | Description |
|---|---|
| `start()` | Starts the background control loop thread. |
| `stop()` | Stops the loop and joins the thread. |
| `setJointTarget(int, double)` | Sets a single joint target (radians). |
| `setAllTargets(vector<double>)` | Sets all joint targets at once. |
| `getJoint(int)` | Returns a copy of a joint (thread-safe). |
| `getCurrentPositions()` | Returns PID-estimated positions for all joints. |
| `getRealPositions()` | Returns Gazebo ground-truth positions for all joints. |

---

## Dependencies

- `common/JointSpec.hpp` and `common/JointDefinitions.hpp`
- gz-transport, gz-msgs, gz-math
- C++17

--- 

## Sources

[^1]: “gazebosim/gz-transport: Transport library for component communication based on publication/subscription and service calls.,” GitHub. Available: https://github.com/gazebosim/gz-transport/blob/main/src/Node.cc

[^2]: “gazebosim/gz-transport: Transport library for component communication based on publication/subscription and service calls.,” GitHub. Available: https://github.com/gazebosim/gz-transport/blob/main/include/gz/transport/Node.hh