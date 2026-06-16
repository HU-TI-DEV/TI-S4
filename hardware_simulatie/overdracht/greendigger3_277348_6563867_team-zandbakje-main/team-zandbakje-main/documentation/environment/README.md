# Dynamic Terrain Digging - Overview and Handover

`Author: GrijzePanda`

## Overview

This Digger feature allows the excavator to dig into terrain during simulation.

Because Gazebo does not support terrain deformation at runtime, digging is simulated by modifying a heightmap image and reloading the terrain model.

The result is a visible hole where the bucket touches the ground.

## World Setup

* Two SDF files define the terrain environment:
  * world.sdf — builds the simulation scene and loads: the terrain, a support plane, the excavator, boundary walls, visual markers, and lighting/sky.
  * terrain.sdf — specifies the heightmap terrain used for visuals and collision.

---

# How It Works

The system consists of three main parts:

### 1. Terrain Generation

The terrain is generated from a grayscale PNG (`terrain.png`).

* Black = low terrain
* White = high terrain
* Gradients = slopes

`make_heightmap.py` creates this image automatically and can generate:

* Flat terrain
* Sloped terrain
* Rough terrain

Current terrain configuration:

* Terrain size: 129 × 129 meters
* Heightmap resolution: 257 × 257 pixels

This gives a digging precision of roughly 50 cm.

(The same heightmap is used for both terrain rendering and collision detection, so modifying the image updates both the visible terrain and the physical surface the excavator interacts with.)

---

### 2. Bucket Contact Detection

A contact sensor is attached to the rod at the end of the excavator arm.

When the rod touches the terrain:

1. Gazebo reports the contact location.
2. The contact coordinates are stored by `interface.py`.
3. `dig_tile.py` reads these coordinates and starts digging.

The system uses the actual contact point, not the bucket pose.

---

### 3. Terrain Modification

`dig_tile.py` converts the contact location into a pixel position on the heightmap.

The corresponding pixel is lowered by a fixed amount.

Current settings:

* Dig amount: 10 grayscale levels
* Minimum value (bedrock): 20

Once a pixel reaches the minimum value, it can no longer be dug deeper.

To prevent excessive digging, repeated contact on the same pixel is ignored.

---

# Terrain Refreshing

After modifying the heightmap:

1. The PNG is saved.
2. The terrain model is removed.
3. The terrain model is spawned again.

This is necessary because Gazebo cannot update a heightmap of a spawned model.

Two terrain models are maintained:

- `terrain`
- `support_plane`

Both use the same heightmap. The secondary terrain helps prevent the excavator from falling through the world while terrain refreshes are taking place.

Terrain updates occur every 2 seconds at most, allowing multiple digging operations to be grouped together.


# Textures

The terrain uses a sandy gravel texture and normal map from [Poly Haven](https://polyhaven.com/a/gravelly_sand).

---

# Important Files

| File | Purpose |
|--------|---------|
| [world.sdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/world.sdf) | Main simulation world |
| [terrain.sdf](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/terrain.sdf) | Heightmap terrain definition |
| [make_heightmap.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/make_heightmap.py) | Terrain generation |
| [dig_tile.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/dig_tile.py) | Digging logic |
| [interface.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/interface/interface.py) | Gazebo communication |
| [terrain.png](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/environment/media/terrain.png) | Terrain heightmap |

---

# Current Assumptions

The implementation currently assumes:

* Terrain size is 129 × 129 meters.
* Heightmap size is 257 × 257 pixels.
* Terrain updates happen through respawning.
* Digging is based on bucket contact events.
* Digging precision is approximately 50 cm.

If any of these values change, the coordinate conversion logic in `dig_tile.py` will likely need to be updated.

---

# Possible Future Improvements

* Look into ways to support terrain deformation directly in Gazebo.
* Explore methods for updating terrain without respawning it each time.
* Try increasing terrain resolution to improve digging accuracy.
* Consider using multiple contact points instead of only the first one.
* Investigate performance optimizations, especially around terrain updates.

---

# Additional Documentation

This document provides a high-level overview of the Digger feature and its implementation.

For a more detailed explanation of the system architecture, design decisions, terrain generation process, coordinate conversion, optimization history, and implementation details, see: [Dynamic Terrain Digging - Extended Technical Documentation](TECHNICAL_DOCUMENTATION.md)

---

## Sources used:

* Gazebo Answers. (n.d.). *Change a model's appearance within Ignition Gazebo*. [https://answers.gazebosim.org/question/28043/](https://answers.gazebosim.org/question/28043/)
* Gazebo Answers. (n.d.). *Updating the visual of a model using the ModelPlugin*. [https://answers.gazebosim.org/question/24742/](https://answers.gazebosim.org/question/24742/)
* Gazebo Answers. (n.d.). *Ways to simulate dirt digging in Gazebo?*. [https://answers.gazebosim.org/question/21933/](https://answers.gazebosim.org/question/21933/)
* Gazebo Sim. (n.d.). *Gazebo rendering: HeightMap*. [https://gazebosim.org/api/rendering/10/heightmap.html](https://gazebosim.org/api/rendering/10/heightmap.html)
* Gazebo Sim. (n.d.). *Gazebo Sim: Load image heightmaps and digital elevation models (DEM)*. [https://gazebosim.org/api/sim/10/heightmap_dem.html](https://gazebosim.org/api/sim/10/heightmap_dem.html)
* Open Robotics. (2025). *Simulating terrain in Gazebo*. Open Robotics Discourse. [https://discourse.openrobotics.org/t/simulating-terrain-in-gazebo/48533](https://discourse.openrobotics.org/t/simulating-terrain-in-gazebo/48533)
* Samahu. (n.d.). *robotics-dynamic-terrain* [GitHub repository]. GitHub. [https://github.com/Samahu/robotics-dynamic-terrain](https://github.com/Samahu/robotics-dynamic-terrain)
* The Gazebo Authors. (n.d.). *gz-rendering* [GitHub repository]. GitHub. [https://github.com/gazebosim/gz-rendering](https://github.com/gazebosim/gz-rendering)
