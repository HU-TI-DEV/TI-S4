# Module_dev

Top-level directory for the Nautilus robotic arm control module — CV-driven
target reception, kinematics solving, and joint-level Gazebo control. Built
via CMake.

## Architecture

```
CV (/arm/target) → RobotArm::onArmTarget → moveToPosition
  → JointController (current angles)
  → KinematicsSolver::computeForwardKinematics (current FK)
  → KinematicsSolver::solveIK (target → joint angles)
  → JointController (set targets) → Gazebo
```

All joint geometry, limits, and PID configuration are read from a single
shared table, `JOINT_DEFINITIONS` (see `common/README.md`), which both
`JointController` and `KinematicsSolver` depend on — no joint parameters
are duplicated or hardcoded elsewhere.

## Project Layout
- `common/` — shared headers (incl. `JointDefinitions.hpp`), header-only interface library
- `IKSolver/` — `KinematicsSolver`: forward/inverse kinematics (FABRIK)
- `ArmCoordinatenMovement/` — `JointController`: joint state, limits, Gazebo joint interface (historical name)
- `RobotArm/` — integration layer (CV callback, manual control, interactive menu); contains `main.cpp`

Each subdirectory is a separate CMake target, linked into the `IKTest` executable.

## Build & Run

### Manually

```bash
mkdir build && cd build
cmake ..
cmake --build
./IKTest
```


The entry point (`main.cpp`) constructs a `RobotArm`, registers
SIGINT/SIGTERM handlers for clean shutdown via `RobotArm::stop()`, then
starts the joint controller and enters the interactive menu
(`RobotArm::runMenu()`). See `RobotArm/README.md` for menu options.

### Via CLion (recommended)

This project contains a Devcontainer config (see the root directory with devcontainer config). 

To run, follow the instructions as described in its REAMDE to run this project. 

The devcontainer loads all required dependencies (mainly gazebo libraries).

## Known Limitations

See component READMEs for details. Cross-cutting items:
- The IK chain is hardcoded to a fixed DOF count (see `IKSolver/README.md`)
- `JOINT_DEFINITIONS` is accessed by index in places and manually transcribed
  from the SDF (see `common/README.md`)