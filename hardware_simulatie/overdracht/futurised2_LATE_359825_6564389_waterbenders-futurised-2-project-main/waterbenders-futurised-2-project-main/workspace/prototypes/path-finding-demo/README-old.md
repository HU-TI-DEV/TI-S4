# Manual path-finding demo

The instructions in this manual continue where the setup for the `lidarSensorOmgeving` in the [README.MD](../lidarSensorOmgeving/ReadMe.md) left off. It is therefore necessary to have completed those instructions first.

## Setup guide

### Quick Docker commands

Run the commands below (one by one) to execute the path finding algorithm in a simulation:

    cd /workspace/prototypes/path-finding-demo/

    # Launch Gazebo simulation
    gz sim room-v2.sdf &

    # Source ROS2
    source /opt/ros/jazzy/setup.bash

    ros2 launch slam_toolbox.launch.py &

    python3 path_finding.py

<!-- # Source the workspace -->
<!-- source install/setup.bash -->

**Only run after the below installation**

### 1. Install packages 

Run your Gazebo Docker container with:

    docker run -it <image> bash

Use the below command to install `colcon`:

    apt update
    apt install python3-colcon-common-extensions

colcon is the build tool used in ROS2. It's a general multi-package build tool for creating packages.

### 2. Build ROS2 packages

First navigate to `/path-finding-demo/` with:

    cd /workspace/prototypes/path-finding-demo/

And run the following command to build all colcon packages in the workspace:

    colcon build

To only selectively build a single package use:

    colcon build --packages-select path_finding

#### Commit the Docker container

Open a new terminal and run `docker ps` and identify the correct CONTAINER ID corresponding to the image that's running.

Then commit the docker with:

    docker commit <container-id> name:version

### 3. Run the path finding algorithm

See [Quick Docker commands](#quick-docker-commands) (at top of the page)

## Build your own ROS2 package

Navigate to your own ROS2 workspace and use the below command to create a package with a pre-built node:

    ros2 pkg create --build-type ament_python --node-name my_node my_package

This will generate a basic package template, which one can use to develop custom colcon packages for ROS2. You can now edit `my_package/my_package/node.py` to subscribe/publish to a topic and add custom logic. See [text](url) for an example of the code structure.

After that build the package using (inside the package folder):

    colcon build

And add it to the `.launch.py` file, like this:

```python
    my_package = Node(
        package='my_package',
        executable='node',  # Matches the entry point in setup.py
        name='minimal_publisher',
        output='screen',
    )

    return LaunchDescription([
        bridge,
        static_laser_tf,
        slam_launch,
        my_package # <-- Added custom package
    ])
```

Source: https://roboticsknowledgebase.com/wiki/common-platforms/ros/ros2-custom-package/

<!---->
<!-- ## 3. Source ROS2 -->
<!---->
<!-- Source ROS2 with the below command. This needs to be repeated each time you re-enter the Docker container. -->
<!---->
<!--     source /opt/ros/jazzy/setup.bash -->

## Core logic

The below is a quick overview that describes the core logic behind the path finding algorithm implemented in [path_finding.py](./path_finding/path_finding/main.py) 

### Algorithm sub parts

- **Occupancy grid map [[1]](#sources)** (based on Lidar sensor data)
- **Frontier based exploration [[2]](#sources)** for determining the frontier edge cell
- **Breadth First Search (BFS) algorithm [[3]](#sources)** for pathfinding
- **PD Controller** for navigating the robot to an (x, y) coordinate

### Steps (quick overview)

1. **Retrieve the Occupancy grid** from the ROS2 `/map` topic, which generates a map using `slam_toolbox` based on the input of the Lidar sensor.
2. **Use frontier based exploration** to determine all frontier edge cells, i.e. points  on the map that lie between explored areas and unexplored areas. 
3. **Use a path finding algorithm** like Breadth First Search (BFS) or the A* algorithm to determine the closest edge cell relative to the robot.
4. **Reconstruct shortest path** from the outcome of the path finding algorithm.
5. **Calculate the angle and distance** the robot has to move towards to navigate towards the closest edge cell (requires converting grid coordinates to global world coordinates).
6. **Re-evaluate** after the robot has reached the specified edge cell.

## Sources

1. https://robotics.stackexchange.com/questions/98107/how-to-get-obstacle-distance-and-angle-by-using-lidar
2. https://awabot.com/en/autonomous-exploration-method-frontiers/
3. https://www.redblobgames.com/pathfinding/a-star/introduction.html
4. https://atsushisakai.github.io/PythonRobotics/modules/3_mapping/lidar_to_grid_map_tutorial/lidar_to_grid_map_tutorial.html
5. https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
6. https://mechwiz.github.io/Portfolio/jackal.html
7. https://gazebosim.org/docs/latest/sensors/
8. https://www.cs.cmu.edu/~motionplanning/papers/sbp_papers/integrated1/yamauchi_frontiers.pdf
