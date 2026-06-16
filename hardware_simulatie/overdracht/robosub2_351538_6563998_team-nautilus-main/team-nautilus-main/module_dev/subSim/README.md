# subSim

Simulation environment configuration layer for the **Nautilus** project. It houses the historical and active Simulation Description Format (SDF) definitions used to instantiate the underwater world, submarine parameters, and physical robotic arm links within Gazebo.

This module contains a collection of legacy and iterative versions of the `.sdf` world files. Although older versions are retained for historical reference and regression verification, they explicitly document the evolution of the RoboSub's physical structure, link dimensions, and joint layout leading up to the deployment configurations.

---

## Design Choices

* **SDF Versioning Retention:** Rather than discarding early prototypes, multiple world iterations are preserved in this module to allow testing backward compatibility of controllers against older physical limits and inertia layouts.
* **Fixed-Base Isolation:** To simplify arm kinematics testing across different versions, the submarine body (`robosubBody`) is locked statically to the world frame using a `<joint name="fixedToWorld" type="fixed">` element, isolating arm joint profiles from vehicle dynamics.
* **Explicit Topic Mapping:** Every movable joint plugin defines a 1:1 mapped topic configuration matching the low-level string expectations found in the hardware abstraction layer (e.g., `/subToBaseTopic`, `/baseToUpperarmTopic`).

---

## Overview

`subSim` wraps the Gazebo simulation topology. It outlines environment constraints (such as a zero-gravity baseline inside the physics system), directional rendering lights, physical collision geometries for every mechanical arm element, and sets up the internal plugins required to broadcast full state models.

---

## Responsibilities

* Declares structural links, collision boundaries, and precise link lengths (e.g., `upperarm` at 0.208m, `forearm` at 0.235m) for the physical simulation engine.
* Configures physics constraints including a decoupled `<gravity>0 0 0</gravity>` matrix to specialize environments for pure kinematic tracking.
* Attaches the `gz::sim::systems::JointStatePublisher` system to output real-time absolute link telemetry.
* Registers seven distinct instances of `gz::sim::systems::JointController` to catch velocity or position commands sent across Gazebo transport.

---

## Model Topology (Version 4 Specification)

The physical link hierarchy and rotational axes are arranged as follows:

```
robosubBody (Static Box: 0.8m × 0.4m × 0.2m)
  └─ base [Z-Axis Rotation] (Limits: ±0.7854 rad)
      └─ upperarm [Y-Axis Rotation] (Limits: -1.8307 to 0 rad)
          └─ forearm [Negative Y-Axis Rotation] (Limits: -1.6493 to 0 rad)
              └─ wrist [Y-Axis Rotation] (Limits: -0.3491 to 1.7523 rad)
                  └─ hand [X-Axis Rotation] (Limits: 0 to 4.7124 rad)
                      ├─ firstfinger [Z-Axis Rotation] (Limits: 0 to 0.7854 rad)
                      └─ secondfinger [Z-Axis Rotation] (Limits: -0.7854 to 0 rad)

```

---

## Configured Communication Topics

The integrated plugins listen explicitly to the following channel addresses:

| Joint Name | Target Topic | Mechanical Type | Bound Limits (Radians) |
| --- | --- | --- | --- |
| `subToBase` | `/subToBaseTopic` | Revolute | `[-0.7854, 0.7854]` |
| `baseToUpperarm` | `/baseToUpperarmTopic` | Revolute | `[-1.8307, 0.0000]` |
| `upperarmToForearm` | `/upperarmToForearmTopic` | Revolute | `[-1.6493, 0.0000]` |
| `forearmToWrist` | `/forearmToWristTopic` | Revolute | `[-0.3491, 1.7523]` |
| `wristToHand` | `/wristToHandTopic` | Revolute | `[0.0000, 4.7124]` |
| `handToFirstfinger` | `/handToFirstfingerTopic` | Revolute | `[0.0000, 0.7854]` |
| `handToSecondfinger` | `/handToSecondfingerTopic` | Revolute | `[-0.7854, 0.0000]` |

---

## Building & Usage

These assets are descriptive XML/SDF files loaded directly by the Gazebo Simulator executable or passed into launch scripts. They do not require a C++ compilation target within the primary CMake configuration.

```bash
# Example manual invocation via Gazebo Sim
gz sim <path_to_module>/subSimV4.sdf

```

---

## Known Limitations and recommendations

* **Zero-Gravity Environment:** The environment explicitly clears forces via `<gravity>0 0 0</gravity>`. While useful for clean kinematic verification, it ignores true underwater buoyancy dynamics, drag coefficients, or current disturbances; code verified exclusively here might exhibit tracking errors on a physical deployment or under a realistic hydrodynamics plugin.
* **Hardcoded Link Geometry:** Physical properties (visual offsets, bounding boxes, collision shapes) are statically defined within the SDF string structure. Modifying the physical arm length requires updating multiple offset coordinates manually, which is highly prone to calculation errors. It is recommended to migrate to a macro-expansion format (such as ERB or xacro) if design iterations continue.