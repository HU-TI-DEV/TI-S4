# Models

Here you will find all the 3D models (SDF files) used in Gazebo. This folder contains the visual and physical layouts of the objects based on the client's requirements.

---

## File structure

    ├───desert.sdf             # Main world file that includes and spawns the models
    ├───models
    |   ├───clumsy_shrub
    |   |   ├───model.config
    |   |   └───model.sdf
    |   ├───greendigger
    |   |   ├───model.config
    |   |   └───model.sdf
    |   ├───large_shrub
    |   |   ├───model.config
    |   |   └───model.sdf
    |   ├───little_shrub
    |   |   ├───model.config
    |   |   └───model.sdf
    |   ├───tree
    |   |   ├───model.config
    |   |   └───model.sdf
    │   └───README.md          # This file

---

## 1. Design Philosophy & Client Requirements

The GreenDigger is designed as a lightweight, simplified machine without unnecessary details. The model directly implements the following requirements from the client:

* **Fixed Wheels:** The platform uses a fixed 4 wheel setup without a steering mechanism, keeping the movement base simple.
* **Electric Joint Motors:** Instead of heavy hydraulic cylinders, the joints simulate electric motors placed directly on the pivot points.
* **Front Shovel Principle:** The bucket is inverted compared to a standard excavator. This provides several major advantages:
  * **Half-Moon Trajectory:** The GreenDigger can dig a perfect half-moon shape (with a 5 meter diameter / 2.5 meter radius) from a single, fixed position.
  * **Energy Efficient:** The vehicle does not need to drive while digging. It only drives in a straight line to the next half moon location, saving a lot of battery energy.
  * **One-Shot Dumping:** It scoops and dumps the sand onto the edge of the half moon, creating a dike in one smooth motion

---

## 2. GreenDigger Technical Specifications

The dimensions in the SDF file are optimized to meet the client's size and performance requirements:

* **Chassis Platform:** Measures 4.5m long and 2.0m wide.
* **External Slew Disk (Pivot Point):** To dig the half moon shape efficiently, the arm's rotating pivot point is mounted outside the wheel platform frame (at y: 1.4m, while the chassis frame ends at y: 1.0m).
* **Ballast Counterweight:** Mounted on the exact opposite side of the chassis (at y: -1.3m) to compensate for the weight of the extended arm.
* **Wheels:** 4 identical fixed wheels with a 0.8m diameter and 0.3m width
* **Digging Arm:** Made of two main segments. Both segments are exactly 1.73 meters long. This length is optimized to perfectly cover the required 2.5-meter digging radius.
* **Front Shovel (Bucket):** A lightweight, small bucket with a width of exactly 30 cm, designed with a box shape to simulate a scooping bucket
* **Camera Sensor:** Mounted on the rotating platform to look directly forward and scan the digging area for trees.

---

## 3. Vegetation & Environment Objects

These models are used to populate the world and test the vision pipeline:

* **tree:** The main target for the camera. It features a simple rectangular trunk and a circular canopy to match our shape detection algorithm.
* **clumsy_shrub / large_shrub / little_shrub:** Different sized bushes used as distractors to test if the vision script can accurately distinguish between real trees and other green objects.

---

## 4. Gazebo Control Topics

The robot uses built-in Gazebo plugins to communicate with the C++ controller:
* **Control (_ctrl):** Topics used to send velocity commands to the joint electric motors (slew_ctrl, shoulder_ctrl, elbow_ctrl).
* **Feedback (_observer):** Topics used to read the current joint angles in real-time (slew_observer, shoulder_observer, elbow_observer).

---

## 5. Gazebo Environment Paths

When loading the desert.sdf world file, Gazebo needs to know where to find our custom models. By default, Gazebo only looks in its own system folders. 

In the run.sh script, we automatically fix this by exporting the models folder path to the GZ_SIM_RESOURCE_PATH environment variable:

```bash 
export GZ_SIM_RESOURCE_PATH=$(pwd)/models
```
If you ever want to launch the simulation or test a model manually without using our run.sh script, you must run this command in your terminal first. If you forget this, Gazebo will throw an error and fail to load the excavator and the trees.