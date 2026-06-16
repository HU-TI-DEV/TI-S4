# Omgeving met Obstakels
*15/06/2026*<br>
*Radeiaan Nandoe*<br>
*Django Manders*

This prototype is the first realistic simulated room with obstacles. The goal was to simulate a room for the robot to be able to navigate through.

---

## Overview

This folder contains the earliest environment prototypes for the Gazebo simulation. It was the birthplace of the project's modular design philosophy: rather than defining everything in one large monolithic `.sdf` file, models were split into separate reusable plugins and obstacle definitions.

This separation later became the standard across the project — sensors are not defined directly inside the robot's `.sdf` file but are attached as separate plugin snippets from `models/gazebo/plugins/`, and obstacles are maintained as individual reusable Gazebo models.

---

## Prototype Files

| File | Description |
|---|---|
| `omgevingV1.sdf` | The very first environment prototype ever simulated in this project — a room with obstacles used for robot navigation |
| `kamer/kamerV1.sdf` | An attempt at a more detailed room layout but was ultimately scrapped because the models it used were too resource-intensive to render on all teammates' laptops, causing simulation issues.|

Even though kamerV1.sdf was scrapped it was still what inspired the idea of making a modular environment where sensors, objects etc just just be "plugged in" by using a simple include such as shown below

```xml
    <include>
      <uri>file:///workspace/models/gazebo/obstacles/shapes/orangeBox0_8x0_8x0_8</uri>
      <name>orangeBox</name>
      <pose>-2 0 0.4 0 0 0</pose>
    </include>
```
# Links
Model insertion using "Fuel" https://gazebosim.org/docs/latest/fuel_insert/