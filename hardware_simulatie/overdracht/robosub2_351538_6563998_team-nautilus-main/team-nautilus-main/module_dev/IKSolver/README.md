# KinematicsSolver

A C++ kinematics module for the **Nautilus** robotic arm, providing forward kinematics (FK) and inverse kinematics (IK) solving using the FABRIK algorithm. Built against the Gazebo/Ignition math library (`gz::math`).

<!-- TOC -->
* [KinematicsSolver](#kinematicssolver)
  * [Overview](#overview)
  * [Design Choices](#design-choices)
  * [Arm Configuration](#arm-configuration)
  * [API](#api)
    * [Constructor](#constructor)
    * [Forward Kinematics](#forward-kinematics)
    * [Inverse Kinematics](#inverse-kinematics)
  * [Dependencies](#dependencies)
  * [Building](#building)
  * [Recommendations and known limitations](#recommendations-and-known-limitations)
  * [Sources](#sources)
<!-- TOC -->

---

## Overview

`KinematicsSolver` computes the 3D world-space positions of each joint in the Nautilus AUV robotic arm, and solves inverse kinematics to reach a target position. Joint geometry is read directly from the shared `JOINT_DEFINITIONS` table in `common/JointDefinitions.hpp`, making the solver data-driven and independent of hardcoded link parameters.

---

## Design Choices

For inverse kinematics, a FABRIK algorithm fit best for the purposes of the arm. This is because FABRIK is one of the fastest algorithms when it comes to inverse kinematics, and is highly expandable, allowing the addition of many additional joints without a significant loss in performance, as FABRIK operates linearly over the chain. [^1]. Furthermore, it offers smooth motion to the target position, and the algorithm itself is relatively easy to implement, compared to other IK algorithms.

For forward kinematics, the solver composes a sequence of per-joint rigid-body transforms along the kinematic chain, starting from the base and accumulating outward to the end effector [^2]. Rotations are represented as quaternions and composed via quaternion multiplication, avoiding the singularities (gimbal lock) and axis-order dependencies associated with Euler-angle representations when chaining rotations about different joint axes [^3]. Geometry is read directly from JOINT_DEFINITIONS, which stores each joint's translation vector and rotation axis as defined by the simulation model, keeping the solver consistent with the SDF.

---

## Arm Configuration

The arm consists of 7 joints, of which 5 participate in IK solving (`actsInIK = true`):

| Joint               | Type      | Axis      | Translation from previous     |
|---------------------|-----------|-----------|-------------------------------|
| `subToBase`         | Yaw       | Z         | `(0, 0, −0.1206)`            |
| `baseToUpperarm`    | Pitch     | +Y        | `(0, 0, −0.0206)`            |
| `upperarmToForearm` | Pitch     | −Y        | `(−0.208, 0, −0.0292)`       |
| `forearmToWrist`    | Pitch     | +Y        | `(0.235, 0, 0)`              |
| `wristToHand`       | Roll      | X         | `(0.1601, 0, 0)`             |
| `handToFirstfinger` | —         | —         | IK excluded                  |
| `handToSecondfinger`| —         | —         | IK excluded                  |

All offsets are in metres. Verified against the Gazebo SDF.

---

## API

### Constructor
```cpp
KinematicsSolver(int numJoints);
```

### Forward Kinematics
```cpp
std::vector<gz::math::Vector3d> computeForwardKinematics(
    const std::vector<double>& jointAngles
);
```
Computes world-space positions for each IK-participating joint given a vector of joint angles in radians. Geometry is read from `JOINT_DEFINITIONS` — only joints with `actsInIK = true` are included.

**Returns** a vector of `gz::math::Vector3d` positions from world origin to end-effector. These are XYZ coordinates of each of the positions of the links that participate in IK.

### Inverse Kinematics
```cpp
std::vector<double> solveIK(
    const gz::math::Vector3d& targetPos,
    const std::vector<gz::math::Vector3d>& currentJointPositions
);
```
Solves joint angles to reach `targetPos` using the FABRIK algorithm in a projected 2D plane.

**Strategy:**
- Joint 0 (yaw): solved analytically via `atan2(target.Y, target.X)`
- Joints 1–3 (pitch): solved via 2D FABRIK in the radial/height `(r, z)` plane
- Joint 4 (roll): set to 0, does not affect end-effector position

**Returns** a vector of 5 joint angles in radians, ordered base to end-effector.



---

## Dependencies

- **gz-math** — `gz::math::Vector3d`, `gz::math::Pose3d`
- **JointDefinitions.hpp** — shared joint geometry and configuration
- C++17 or later

---

## Building

Part of the Nautilus project, built via the project CMake configuration (included as a library in module_dev/CMakeLists.txt). No standalone build target provided.

---

## Recommendations and known limitations

- Joint limits are not enforced inside the IK solver — clamping happens downstream in `Joint::setTarget()`
- Roll joint (wristToHand) is not solved — end-effector orientation is not controlled
- IK assumes the arm operates in a single vertical plane after yaw rotation — targets with complex 3D orientation are not supported
- Currently, the IK chain is hardcoded to the arm's current 3-segment pitch configuration (4 control points). The link lengths and geometry are read dynamically from `JOINT_DEFINITIONS`, but the FABRIK loop bounds and the output vector size (5) assume this fixed DOF count. Generalizing to arbitrary N-DOF would mean driving the loop and output sizing off `JOINT_DEFINITIONS`; deferred because the arm is fixed-geometry and any change would require re-validation against the SDF.
- `baseHeight` in `solveIK` indexes `JOINT_DEFINITIONS[1]` directly with an assumed offset value. If the definitions table is reordered, this breaks silently with no compile error. A lookup-by-name would be more robust.

---

## Sources

[^1]: A. Aristidou and J. Lasenby, “FABRIK: A fast, iterative solver for the Inverse Kinematics problem,” Graphical Models, vol. 73, no. 5, pp. 243–260, Sep. 2011, doi: https://doi.org/10.1016/j.gmod.2011.05.003.

[^2]: A. Stevens, "Forward Kinematics," in *Modeling, Motion Planning, and Control of Manipulators and Mobile Robots*, Y. Wang, Ed. Clemson University Open Textbooks, 2021. [Online]. Available: https://opentextbooks.clemson.edu/wangrobotics/chapter/forward-kinematics/

[^3]: K. Shoemake, “Animating rotation with quaternion curves,” ACM SIGGRAPH Computer Graphics, vol. 19, no. 3, pp. 245–254, Jul. 1985, doi: 10.1145/325165.325242. Available: https://dl.acm.org/doi/epdf/10.1145/325165.325242