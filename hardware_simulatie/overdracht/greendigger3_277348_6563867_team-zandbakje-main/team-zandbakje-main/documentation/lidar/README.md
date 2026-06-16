# LiDAR Object Detection and Clustering - Extended Technical Documentation

`Author: ShelleKjell`

## Overview

This component processes raw LiDAR point cloud data received from Gazebo and extracts potential objects from the environment.

The processing pipeline performs:

* Point cloud decoding
* Range filtering
* Voxel-based downsampling
* Ground plane removal
* Euclidean clustering
* Terrain bump rejection
* Object centroid estimation

The system is designed to identify physical obstacles and objects while filtering out ground surfaces and small terrain irregularities.

---

# Architecture

The LiDAR processing system consists of six primary stages:

1. Point cloud acquisition
2. Point cloud decoding
3. Range filtering
4. Voxel downsampling
5. Ground removal
6. Object clustering

Each incoming LiDAR frame is processed independently.

---

# Point Cloud Acquisition

## Data Source

Point cloud data is received through Gazebo Transport.

Current topic:

```text
/digger/lidar/points/points
```

The application subscribes to this topic using:

```cpp
node.Subscribe(
    "/digger/lidar/points/points",
    &LidarProcessor::OnPointCloud,
    &proc);
```

Each message contains a packed point cloud represented by:

```cpp
gz::msgs::PointCloudPacked
```

Incoming messages trigger the processing callback.

---

# Point Cloud Decoding

## Callback Processing

The main processing entry point is:

```cpp
OnPointCloud(...)
```

For each point in the incoming cloud:

```cpp
float x;
float y;
float z;
```

coordinates are extracted from the packed binary buffer.

The implementation assumes:

```text
offset 0  -> x
offset 4  -> y
offset 8  -> z
```

using:

```cpp
std::memcpy(...)
```

to reconstruct the floating-point values.

### Invalid Point Removal

Points are discarded if any coordinate is not finite:

```cpp
if (!std::isfinite(x) ||
    !std::isfinite(y) ||
    !std::isfinite(z))
```

This prevents corrupted or invalid sensor measurements from entering the processing pipeline.

---

# Range Filtering

## Maximum Detection Range

After decoding, the distance from the sensor origin is calculated:

```text
r = √(x² + y² + z²)
```

Only points within the configured range are retained.

Current configuration:

```cpp
maxRange = 30.0f;
```

Points beyond this distance are discarded.

### Design Motivation

Limiting the processing range:

* Reduces computational cost
* Removes distant sensor noise
* Improves clustering performance
* Focuses detection on nearby obstacles

---

# Voxel Downsampling

## Purpose

Raw LiDAR scans can contain a large number of points.

To reduce processing load, the point cloud is downsampled using a voxel grid filter.

Implementation:

```cpp
pcl::VoxelGrid<pcl::PointXYZ>
```

Current voxel size:

```cpp
voxelSize = 0.06f
```

Each voxel stores a representative point while nearby points are merged.

### Benefits

Voxel filtering:

* Reduces point count
* Improves clustering speed
* Reduces sensor noise
* Maintains overall object shape

---

# Ground Removal

## RANSAC Plane Segmentation

Ground detection is performed using RANSAC plane fitting.

Implementation:

```cpp
pcl::SACSegmentation<pcl::PointXYZ>
```

Configuration:

```cpp
SACMODEL_PLANE
SAC_RANSAC
```

The algorithm attempts to identify the dominant planar surface in the scene.

Current settings:

```cpp
distanceThreshold = 0.07
maxIterations = 100
```

### Ground Extraction

Detected plane points are considered ground points.

These points are removed using:

```cpp
pcl::ExtractIndices
```

with:

```cpp
setNegative(true)
```

resulting in a point cloud containing only non-ground objects.

### Design Motivation

Ground removal significantly improves clustering quality by preventing the terrain from forming a large cluster.

---

# Object Clustering

## Euclidean Cluster Extraction

Objects are detected using Euclidean distance clustering.

Implementation:

```cpp
pcl::EuclideanClusterExtraction<pcl::PointXYZ>
```

A KD-tree is constructed for efficient neighbour searches:

```cpp
pcl::search::KdTree
```

### Configuration

Cluster tolerance:

```cpp
clusterTolerance = 0.30f
```

Minimum cluster size:

```cpp
minClusterSize = 60
```

Maximum cluster size:

```cpp
maxClusterSize = 20000
```

### Clustering Process

Points are grouped into the same cluster when neighbouring points fall within the configured distance threshold.

Each resulting cluster is treated as a potential object.

---

# Terrain Bump Rejection

## Purpose

Even after ground removal, small terrain irregularities can remain.

Examples:

* Small bumps
* Surface roughness
* Ground segmentation errors

These can produce false object detections.

---

## Height-Based Filtering

For each cluster:

```cpp
minZ
maxZ
```

are calculated.

Cluster height is then computed:

```text
height = maxZ - minZ
```

Current threshold:

```cpp
height < 0.10
```

Clusters below this threshold are rejected.

### Design Motivation

Real objects typically exhibit greater vertical extent than terrain artefacts.

This simple filter removes many false positives while preserving larger obstacles.

---

# Object Characterisation

## Centroid Calculation

For accepted clusters, the geometric centre is calculated.

For a cluster containing N points:

```text
cx = Σx / N
cy = Σy / N
cz = Σz / N
```

This centroid provides an approximate object location.

---

## Distance Estimation

Object distance is calculated using:

```text
distance = √(cx² + cy² + cz²)
```

This value represents the distance between the LiDAR sensor and the detected object centroid.

---

# Diagnostic Output

For each LiDAR frame the system reports:

```text
raw points
voxel points
non-ground points
cluster count
```

For every accepted cluster:

```text
cluster id
point count
cluster center
distance
```

Example:

```text
BLOCK 0
points: 512
center: (4.2, 1.7, 0.9)
distance: 4.63
```

This information is intended for debugging and performance evaluation.

---

# Important Files

| File                                | Purpose                               |
| ----------------------------------- | ------------------------------------- |
| lidar.cpp                           | Main LiDAR processing implementation  |


---

# Current Configuration

| Parameter           | Value  | Purpose                          |
| ------------------- | ------ | -------------------------------- |
| maxRange            | 30.0 m | Maximum detection distance       |
| voxelSize           | 0.06 m | Voxel grid resolution            |
| clusterTolerance    | 0.30 m | Cluster neighbour distance       |
| minClusterSize      | 60     | Minimum cluster size             |
| maxClusterSize      | 20000  | Maximum cluster size             |
| distanceThreshold   | 0.07 m | Ground segmentation threshold    |
| maxIterations       | 100    | RANSAC iterations                |
| bumpHeightThreshold | 0.10 m | Terrain bump rejection threshold |

---

# Assumptions and Improvement Suggestions

The current implementation assumes:

* The dominant plane represents the ground.
* Objects extend sufficiently above the terrain.
* LiDAR data contains valid XYZ coordinates.
* Nearby objects are spatially separated enough for Euclidean clustering.
* The environment is relatively structured and navigable.

Possible Future Improvements:

* Add object tracking between frames.
* Introduce bounding box estimation.
* Estimate object velocity using temporal data.
* Replace simple bump filtering with geometric classification.
* Implement adaptive clustering based on distance.
* Improve ground segmentation for uneven terrain.
* Publish detected objects through Gazebo Transport topics.
* Integrate obstacle detections directly into the navigation system.
* Add visualisation markers for detected clusters.
* Support classification of detected object types.

---

# General advice for follow-up project

* Lidar testing is unfinished and it is clear that there are limitations to the gazebo environment. To get the full scope of the lidar possibilties, lidar should be tested in different environments to see the reliabity of the system in a real world setting.
* Lidar in gazebo gives the option to see how different materials reflect with the lidar lasers. This could be used to seperate obstacles from the ground or even seperate the digger itself by ignoring its material. This could however, translate bad outside of the simulation with the many irregularities in the materials in the surface. More advancements in lidar could make this option useable but i would not recommend using this as the final solution right now.
* Lidardebug.sdf is the environment where the code works correctly. Use this as a bridge to completing lidar integration.
* Lidar is using the pointcloud topic, laserscan topic has not been used or tested. If laserscan is used, a different format of information will be given which will NOT work in the current Lidar.cpp
* info on limitations of a real digger are limited, making the values for what makes an object dangerous possibly unrealistic. These values can easily be changed in the code when more information outside of the simulation is available.
* Lidar is not the definitive solution to the obstacle problem and different methodes have been researched by other project groups. Maximize the potential of Lidar, but dont force it where it shows its limits.


---

# References

Baeldung. (n.d.). RANSAC algorithm explained. Baeldung. Retrieved June 15, 2026, from https://www.baeldung.com/cs/ransac

NEON Science. (n.d.). LiDAR basics. National Ecological Observatory Network (NEON). Retrieved June 15, 2026, from https://www.neonscience.org/resources/learning-hub/tutorials/lidar-basics

Patil, S. (n.d.). LiDAR obstacle detection project [Computer software]. GitHub. Retrieved June 15, 2026, from https://github.com/sumukhpatil/LiDAR-Obstacle-Detection-Project