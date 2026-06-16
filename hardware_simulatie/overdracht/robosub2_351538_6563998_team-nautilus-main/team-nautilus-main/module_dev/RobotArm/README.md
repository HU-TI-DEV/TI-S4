# RobotArm

Top-level integration layer for the **Nautilus** robotic arm: wires together joint control, kinematics solving, and CV-driven autonomous targeting via Gazebo transport.

---

## Design Choices

`RobotArm` maps between the full joint set (including gripper) and the IK-participating subset by filtering on `JOINT_DEFINITIONS[i].actsInIK`, so adding or removing joints from IK solving requires no changes here - only JointDefinitions.hpp.

--- 

## Overview

`RobotArm` ties `JointController` and `KinematicsSolver` together into a single interface. It exposes manual joint control, an interactive diagnostics menu, and a CV-driven autonomous mode that subscribes to `/arm/target` and drives the end-effector toward received 3D positions via IK.

---

## Responsibilities

- Subscribes to `/arm/target` (gz-transport) for CV-supplied target positions
- Converts current joint angles → FK → world positions → IK → new joint targets
- Maps between full joint index space (7 joints, including gripper) and the IK-participating subset (5 joints), using `JOINT_DEFINITIONS[i].actsInIK`
- Provides an interactive CLI menu for manual joint control and FK/IK diagnostics

---

## API

### Lifecycle
```cpp
void start();  // starts the joint controller
void stop();   // stops the joint controller
```

### Manual control
```cpp
void setJointTarget(int index, double targetRad);
void setAllTargets(const std::vector<double>& targetsRad);
Joint getJoint(int index);
std::vector<double> getCurrentPositions();
std::vector<double> getRealPositions();
```

### Inverse Kinematics
```cpp
void moveToPosition(const gz::math::Vector3d& targetPos);
```
Reads current joint angles, filters to IK-participating joints, computes current FK positions, solves IK for `targetPos`, and applies the resulting angles back to the corresponding joints.

### Autonomous Control
```cpp
void onArmTarget(const gz::msgs::Vector3d& msg);
```
Triggered on `/arm/target`. No-ops unless `autoControl` is enabled. Sets gripper joints (5, 6) to a fixed open pose, then calls `moveToPosition`.

### Interactive menu
```cpp
void runMenu();
```
CLI loop for joint-by-joint control plus diagnostics:
- `97` — toggle auto control (CV-driven mode)
- `98` — test IK by entering target coordinates
- `99` — print FK diagnostics (current angles + computed chain positions)
- `0–6` — select a joint and enter a target angle in degrees

---

## Dependencies

- **JointController.hpp** — joint state, limits, Gazebo joint interface
- **KinematicsSolver** — Forward and Inverse Kinematics
- **JointDefinitions.hpp** — shared joint geometry and `actsInIK` flags
- **gz-transport** — `/arm/target` subscription
- C++17 or later

---

## Building

Part of the Nautilus project, built via the project CMake configuration. No standalone build target provided.

---

## Known Limitations and recommendations

- The gripper pose set in `onArmTarget` (joints 5 and 6, ±π/4) is hardcoded — there is no configurable "open" pose, and these indices assume a fixed joint layout.
- `onArmTarget` does not validate the incoming target against arm reach or joint limits before calling `moveToPosition`; out-of-reach handling is delegated entirely to `KinematicsSolver::solveIK`.
- No feedback loop between `moveToPosition` and execution — it issues a single IK solve and target write per callback, with no verification that the arm reached the target before the next message arrives.
- The menu's joint-index validation (`choice >= JOINT_DEFINITIONS.size()`) assumes menu indices map 1:1 to `JOINT_DEFINITIONS` indices; if the two ever diverge this will silently misroute commands.
