# JointSpec & JointDefinitions

The single source of truth for all joint configuration in the Nautilus robotic arm. Both the runtime controller (`JointController`) and the kinematics solver (`KinematicsSolver`) read from this shared table — no joint parameters are hardcoded elsewhere.

## Design choices

The architecture with JointSpec and JOINT_DEFINITIONS is in itself a design choice. It is intended to separate the static values of the spec (geometry, PID values)  from the JointController class with its dynamic values.

This separation means geometry and tuning changes (e.g. adjusting a PID gain or correcting a measured offset) require touching only JointDefinitions.hpp, without recompiling logic in JointController or KinematicsSolver, and keeps both consumers guaranteed to agree on the arm's physical configuration.

---

## JointSpec

Defined in `common/JointSpec.hpp`. A plain struct describing the static properties of a single revolute joint:

```c++
struct JointSpec {
    std::string name;           // Joint name, matches SDF
    std::string topic;          // Gazebo transport topic
    double lowerLimitRad;       // Lower joint limit (radians)
    double upperLimitRad;       // Upper joint limit (radians)
    double kP, kI, kD;          // PID gains
    gz::math::Vector3d translation;   // Offset from previous joint (metres)
    gz::math::Vector3d rotationAxis;  // Axis of rotation (unit vector)
    bool actsInIK;              // Whether this joint participates in IK solving
    bool invertPublish;         // Whether to negate velocity before publishing to Gazebo
};
```

### Field notes

- `translation` and `rotationAxis` are verified against the Gazebo SDF
- `invertPublish` is needed for joints whose SDF axis direction differs from the FK convention (currently only `upperarmToForearm`, axis `(0,-1,0)`)
- `actsInIK = false` for the finger joints — they are excluded from FABRIK solving

---

## JOINT_DEFINITIONS

Defined in `common/JointDefinitions.hpp`. A runtime-constant vector of `JointSpec` entries, one per joint:

```cpp
inline const std::vector<JointSpec> JOINT_DEFINITIONS = { ... };
```

### Who uses it

| Consumer | What it reads |
|---|---|
| `JointController::initJoints()` | Constructs `Joint` objects from each spec |
| `JointController::initPublishers()` | Reads `topic` for Gazebo advertisement |
| `JointController::onJointState()` | Matches `name` against incoming Gazebo joint state |
| `KinematicsSolver::computeForwardKinematics()` | Reads `translation` and `rotationAxis` |
| `KinematicsSolver::solveIK()` | Reads `translation` for link lengths and base offsets |

### Adding or modifying a joint

Only `JOINT_DEFINITIONS` needs to change. No other file requires modification — the controller adapts automatically to the new configuration.

---

## Dependencies

- `gz::math::Vector3d` from gz-math
- C++17 (`inline` variables)

## Known limitations and recommendations

- `JOINT_DEFINITIONS` is accessed by index in places (e.g. `KinematicsSolver`'s
  `baseHeight` calculation reads `JOINT_DEFINITIONS[1]` directly). Reordering
  entries would silently break these without a compile error. Lookup-by-`name`
  would be more robust if the table is likely to be reordered.
- No validation at startup that `JOINT_DEFINITIONS` entries are internally
  consistent (e.g. `lowerLimitRad < upperLimitRad`, `rotationAxis` is a unit
  vector) — malformed entries would fail silently or produce incorrect FK/IK
  rather than an early error.
- `JOINT_DEFINITIONS` values were manually transcribed from the Gazebo SDF.
  If the SDF changes (link offsets, joint limits, etc.), this table must be
  updated by hand and re-verified - there is no automated sync. For future
  development, retrieving these values automatically via SDF would increase robustness.