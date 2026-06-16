# Dynamic Terrain Digging - Extended Technical Documentation

`Author: GrijzePanda`

## Overview

This Digger feature implements environmental terrain manipulation within Gazebo by allowing an excavator bucket to dynamically modify terrain during simulation.

The system simulates digging by modifying a terrain heightmap at runtime and respawning the terrain model using the updated heightmap. This creates visible holes and deformations where the excavator interacts with the ground.

The implementation was developed because Gazebo does not provide native support for real-time terrain deformation.

## World Setup

The terrain environment is defined by two SDF files:

- `world.sdf`
- `terrain.sdf`

`world.sdf` creates the simulation environment and loads:

- The terrain
- A secondary support terrain (`support_plane`)<sup>1</sup>
- The excavator
- Boundary walls
- Visual marker objects
- Lighting and sky settings

`terrain.sdf` defines the heightmap terrain model used for both visual rendering and collision detection.

The marker objects are included as visual reference points during terrain and digging development. They are not required for the digging system itself.

Four static walls surround the terrain and act as simple world boundaries.

<sup>1</sup>The secondary terrain exists to prevent the excavator from falling through the world during terrain refresh operations. Its role is explained further in the Dual-Terrain Approach section.

---

# Architecture

The digging system consists of four primary components:

1. Heightmap-based terrain generation
2. Terrain manipulation logic
3. Bucket-terrain interaction detection
4. Terrain reload/update mechanism

## Terrain Representation

The terrain is represented by a grayscale PNG heightmap.

### Heightmap Principles

* Black pixels represent lower elevations.
* White pixels represent higher elevations.
* Gray values represent intermediate elevations.
* Gradients create slopes.

Terrain elevation is calculated from the grayscale value and scaled within the height range configured in `terrain.sdf`.

Current configuration:

* Terrain size: 129 × 129 meters
* Heightmap resolution: 257 × 257 pixels
* Vertical elevation range: 10 meters

This provides an effective digging precision of approximately 50 cm per pixel.

These terrain dimensions are defined in `terrain.sdf`:

```xml
<size>129 129 10</size>
````

Several parts of the digging system assume these dimensions, including the coordinate conversion logic in `dig_tile.py`.

The same heightmap is used for both visual rendering and collision detection within `terrain.sdf`.

As a result, modifying `terrain.png` automatically updates both:

- The visible terrain surface
- The physical terrain that the excavator interacts with

---

# Current Configuration

| Parameter                       | Value                           |
| ------------------------------- | ------------------------------- |
| Terrain size                    | 129 × 129 meters                |
| Heightmap resolution            | 257 × 257 pixels                |
| Elevation range                 | 10 meters                       |
| Dig amount                      | 10 grayscale levels             |
| Minimum terrain value (bedrock) | 20 grayscale levels             |
| Terrain refresh interval        | 2.0 seconds                     |
| Heightmap file                  | `environment/media/terrain.png` |
| Approximate digging precision   | 50 cm                           |

These values are currently hardcoded in the implementation and should be reviewed if terrain dimensions or digging behaviour are changed.

---

# Terrain Generation

## make_heightmap.py

`make_heightmap.py` procedurally generates the terrain heightmap used by the simulation.

The script creates:

* A configurable linear slope
* Procedural surface roughness
* Terrain height variation

The generated image is stored as:

```text
environment/media/terrain.png
```

The heightmap is a grayscale PNG where each pixel represents a terrain height value.

### User-Configurable Parameters

The script prompts the user for three values:

#### Slope Start Height

Defines the grayscale value at the start of the terrain.

Default:

```text
80
```

#### Slope End Height

Defines the grayscale value at the end of the terrain.

Default:

```text
180
```

Different start and end values create a slope. Equal values create flat terrain.

#### Terrain Bumpiness

Controls random height variation applied to each pixel.

Default:

```text
0.5
```

Examples:

* `0` = perfectly smooth terrain
* Higher values = rougher terrain

### Terrain Generation Process

For each column of pixels:

1. A base grayscale value is calculated using linear interpolation between the start and end heights.
2. Random noise is added using the configured bumpiness value.
3. The resulting value is clamped between 0 and 255.
4. The final image is saved as the terrain heightmap.

### Notes

The terrain generation system supports:

* Flat terrain
* Sloped terrain
* Rough terrain
* Sloped terrain with roughness

Support for slopes and roughness was added to better match the original terrain model and improve realism.

---

# Dynamic Terrain System

## Research Findings

Initial research determined that Gazebo does not support runtime terrain deformation out of the box.

Several approaches were investigated, including:

* Runtime model modification
* Runtime visual updates
* Mesh-based terrain
* Heightmap-based terrain

Heightmaps were ultimately selected because they could be regenerated and reloaded with relatively little complexity while still providing realistic terrain deformation.

This solution uses:

* Heightmaps
* Python scripts
* Gazebo service calls
* Contact sensors
* Terrain respawning

This approach was considered the most practical and maintainable solution within the limitations of Gazebo.

---

# Bucket-Terrain Interaction

## Contact-Based Digging

The original proof of concept used manually supplied coordinates.

The final implementation uses actual bucket-terrain contact data.

### Implementation

A rod extension was added to the end of the excavator arm.

A contact sensor is attached to this rod and publishes contact events through Gazebo. 

Contact reporting is enabled through the Gazebo Contact System plugin configured in `world.sdf`.

Current contact topic:

```text
/world/starting_environment/model/digger/model/digger/model/mounted_arm/link/ee_link/sensor/rod_contact/contact
```

The contact callback stores:

* Whether the bucket is touching terrain
* Contact X coordinate
* Contact Y coordinate

These values are stored in the shared interface state and are continuously monitored by the digging system.

### Important Design Decision

The system uses contact coordinates rather than bucket pose.

Reason:

* Contact coordinates provide the actual interaction point with the terrain.
* Pose only provides the bucket location and does not indicate where terrain contact occurred.

### Contact Processing

The contact callback processes the first contact position reported by Gazebo.

When multiple contact positions are available, only the first reported position is currently used.

The excavation location is therefore determined by the first available contact point.

---

# Terrain Manipulation

## dig_tile.py

`dig_tile.py` is responsible for:

1. Monitoring bucket contact events
2. Converting world coordinates to terrain pixels
3. Modifying the heightmap
4. Triggering terrain refreshes

### Coordinate Mapping

The terrain is modified using heightmap pixels rather than world coordinates.

When a bucket contact occurs:

1. The contact sensor reports world-space coordinates.
2. The coordinates are converted into pixel coordinates.
3. The corresponding heightmap pixel is modified.

The conversion uses:

```text
meters_per_pixel = terrain_size / (heightmap_resolution - 1)
```

Current values:

* Terrain size: 129 meters
* Heightmap resolution: 257 pixels

Result:

```text
1 pixel = 0.50 meters (roughly)
```

Any future changes to terrain dimensions or heightmap resolution require corresponding updates to the coordinate conversion logic.

### Digging Process

When terrain contact is detected:

1. Contact coordinates are received.
2. World coordinates are converted to heightmap coordinates.
3. The target pixel is modified.
4. The terrain is marked for refresh.
5. The worker thread eventually refreshes the terrain.

### Tile-Based Excavation

The current implementation performs excavation on a per-pixel basis.

Each dig operation lowers a single pixel within the heightmap.

Repeated dig operations create larger excavated areas by modifying neighbouring pixels over time.

This approach provides sufficient precision for excavator-scale interactions while remaining computationally inexpensive.

### Digging Depth Limits

Digging is implemented by reducing the grayscale value of the target pixel.

Current configuration:

```text
DIG_AMOUNT = 10
MIN_VAL = 20
```

Each dig event lowers a pixel by 10 grayscale levels.

Once a pixel reaches a grayscale value of 20, no further digging can occur at that location.

This minimum value acts as a virtual bedrock layer and prevents unlimited excavation.

### Duplicate Dig Prevention

To prevent excessive digging while the bucket remains stationary, the system remembers the most recently modified pixel.

If consecutive digging events target the same pixel, the event is ignored.

Benefits:

* Reduces unnecessary terrain modification
* Reduces redundant updates
* Prevents unrealistically fast excavation of a single location

---

# Terrain Refresh System

## Why Respawning Is Required

Gazebo cannot directly update an active terrain heightmap at runtime.

After modifying the heightmap PNG:

1. The updated image is saved.
2. The existing terrain is removed.
3. A new terrain is spawned.
4. The updated heightmap is loaded.

This causes the terrain deformation to become visible in the simulation.

---

## Terrain Reload Implementation

Terrain refreshing is performed through Gazebo service calls.

The interface layer issues commands equivalent to:

```text
gz service /world/starting_environment/remove
gz service /world/starting_environment/create
```

These services remove and recreate the terrain model using the updated heightmap.

If terrain updates stop functioning, Gazebo service availability should be checked before investigating the terrain generation logic.

### Interface Layer Responsibilities

The original implementation performed terrain spawning and despawning directly from `dig_tile.py`.

This was later refactored so that Gazebo communication is handled by `interface.py`, while `dig_tile.py` is only responsible for digging logic and terrain manipulation. This better matches the intended architecture, where simulation interaction is centralized within the interface layer.

During development, an attempt was made to use the Gazebo Transport API directly through Python message types such as:

* `gz.msgs.Entity`
* `gz.msgs.EntityFactory`

While this approach functioned in some cases, it proved unreliable under repeated terrain refresh operations and was ultimately abandoned.

The current implementation uses `subprocess.run()` to invoke Gazebo services through the `gz service` command-line interface. Although this is arguably less elegant than using the Transport API directly, it was found to be significantly more reliable in practice.

Future developers may wish to revisit the Transport API approach if a more robust implementation becomes available, but the current solution was chosen primarily for stability.

---

## Dual-Terrain Approach

A problem was observed during terrain respawning:

* Terrain disappears briefly.
* The excavator falls through the world.

To prevent this, two identical terrain entities are maintained:

1. `terrain`
2. `support_plane`

Both are loaded from the same `terrain.sdf` definition and refreshed in succession.

This creates the illusion of continuous terrain availability and prevents the excavator from falling while terrain updates are occurring.

---

## Update Scheduling

The final implementation uses:

* A worker thread
* A terrain dirty flag
* A fixed refresh interval

Current configuration:

```text
RESPAWN_INTERVAL = 2.0 seconds
```

Digging operations only mark the terrain as needing an update.

A background worker periodically checks:

* Whether modifications have occurred
* Whether enough time has elapsed since the last refresh

If both conditions are met:

1. The heightmap is saved.
2. Terrain models are refreshed.

This approach batches multiple digging events into a single terrain update and prevents excessive terrain respawning.

---

# Visual Improvements

## Terrain Textures

Once terrain texturing was implemented, a sandy gravel texture and normal map were selected to better match the intended excavation environment.

Files:

```text
gravelly_sand_diff_1k.png
gravelly_sand_nor_gl_1k.png
```

The normal map is used to simulate small surface details through lighting calculations without increasing terrain geometry complexity.

Both assets originate from [Poly Haven](https://polyhaven.com/a/gravelly_sand).

---

# Performance and Optimization

## Initial Optimization Attempt

A queue-based approach was introduced to process terrain updates asynchronously.

Goals:

* Reduce callback workload
* Improve stability
* Reduce excessive respawns

### Result

The queue introduced latency.

Terrain updates accumulated faster than they could be processed, causing delays to increase over time.

The approach was ultimately abandoned.

---

## Final Optimization

The queue implementation was removed.

The final design uses:

* Direct terrain modification
* A worker thread
* Fixed-interval terrain refreshes

Benefits:

* Lower latency
* Predictable update behaviour
* No queue backlog
* Reduced overhead

Terrain changes are applied in batches rather than requiring a terrain refresh after every individual dig operation.

---

# Important Files

| File                            | Purpose                                                                    |
| ------------------------------- | -------------------------------------------------------------------------- |
| [world.sdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/world.sdf)                     | Main simulation world definition                                           |
| [terrain.sdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/terrain.sdf)                   | Terrain model definition and heightmap configuration                       |
| [make_heightmap.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/make_heightmap.py)             | Generates procedural terrain heightmaps                                    |
| [dig_tile.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/dig_tile.py)                   | Handles digging logic and terrain refreshes                                |
| [interface.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/interface/interface.py)                  | Gazebo communication layer, contact subscriptions, spawning and despawning |
| [terrain.png](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/media/terrain.png) | Generated terrain heightmap                                                |
| [gravelly_sand_diff_1k.png](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/media/textures/gravelly_sand_diff_1k.png)     | Terrain texture                                                            |
| [gravelly_sand_nor_gl_1k.png](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/media/textures/gravelly_sand_nor_gl_1k.png)   | Terrain normal map                                                         |

---

# Media Assets

Directory structure:

```text
media/
├── terrain.png
├── gravelly_sand_diff_1k.png
└── gravelly_sand_nor_gl_1k.png
```

## terrain.png

Generated automatically by:

```text
make_heightmap.py
```

Resolution:

```text
257 × 257 pixels
```

Purpose:

* Stores terrain elevation data

## gravelly_sand_diff_1k.png

Diffuse terrain texture.

## gravelly_sand_nor_gl_1k.png

Normal map used to improve lighting detail and perceived surface depth.

---

# Current Assumptions

The current implementation assumes:

* Terrain dimensions are 129 × 129 meters.
* Heightmap resolution is 257 × 257 pixels.
* Terrain elevation is represented by a grayscale PNG.
* Terrain updates occur through model respawning.
* Bucket contact coordinates determine excavation location.
* The first reported contact point is used.
* Terrain refreshes occur at fixed intervals.
* Digging precision is approximately 50 cm.

Changing these assumptions will likely require updates to:

* Heightmap generation
* Coordinate conversion
* Terrain refresh logic
* Digging behaviour

---

# Possible Future Improvements

1. Investigate ways to support terrain deformation directly during simulation.
2. Explore alternatives to terrain respawning when updating the terrain.
3. Improve digging accuracy by using a higher-resolution terrain model.
4. Make terrain dimensions configurable instead of using fixed world sizes.
5. Explore excavation methods that are more advanced than per-pixel updates.
6. Consider using multiple contact points for more realistic digging behavior.
7. Improve terrain update frequency to allow smoother excavation.
8. Optimize terrain update and respawning processes to improve performance.
