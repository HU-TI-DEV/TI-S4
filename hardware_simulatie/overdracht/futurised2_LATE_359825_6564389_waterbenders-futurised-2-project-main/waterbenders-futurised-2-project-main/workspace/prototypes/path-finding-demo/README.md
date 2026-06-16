# Path-finding prototype

*10/06/2026* \
*Django Manders*

## Table of contents
- [Path finding prototype](#path-finding-prototype)
- [Table of Contents](#table-of-contents)
- [Demo video](#demo-video)
- [What's in this folder](#whats-in-this-folder)
- [Reasoning](#reasoning)
- [Core logic](#core-logic)
- [Implementation](#implementation)
  - [1. Callbacks](#1-callbacks)
  - [2. Frontier exploration](#2-frontier-exploration)
  - [3. Dijkstra](#3-dijkstra)
  - [4. Following the path](#4-following-the-path)
  - [5. Drawing the map](#5-drawing-the-map)
- [Setup](#setup)
- [Advice](#advice)
- [Sources](#sources)

## Demo video

![[video](./demo-video.mp4)](./demo_thumbnail.png)

## What's in this folder

This folder contains everything that was needed to implement the path finding algorithm used also inside the main simulation in [path_planning/main.py](/workspace/models/ros/packages/path_planning/path_planning/main.py). Parts of this code also use the [Dijkstra](/workspace/prototypes/dijkstra-algorithm/README.md) implementation made by Sarah.

A couple of files inside this folder are essential for the path finding algorithm to work and make up the foundation of the algorithm. These are:

- **Main code:** [main.py:](./ros/packages/path_planning/path_planning/main.py)
- **Launch file:** [simulation.launch.py](./simulation.launch.py)
- **Parameters nav2_costmap_2d:** [nav2_costmap_params.yaml](./ros/nav2_costmap_params.yaml)
- **Parameters slam_toolbox:** [slam_params.yams](./ros/slam_params.yaml)

## Comparison (research)

Below a comparison is made between different options that can all be used to implement an exploration algorithm. At the end of the comparison the options we chose are discussed in more detail.

### Occupancy grid generation

An occupancy grid is used for path planning for which a different algorithm is used. It represents a grid map where each `-1` is an unknown cell, a `0` cell is a free area and `100` means an obstacle is detected by the Lidar. This is especially useful for an exploration algorithm, because by operating on one map the robot can avoid obstacles, find the shortest path and find a beneficial area to explore.

Different options include:

- **Custom lidar-based 2D map [[1]](#sources)**: 
    - Pros: Simple and not very heavy computationally and good enough for flat environments.
    - Cons: Hard to implement from scratch and misses objects outside the Lidar's field of vision.
- **3D Lidar (e.g. LeGO-LOAM [[2]](#sources), Cartographer [[3]](#sources))**:
    - Pros: Captures obstacles at multiple heights.
    - Cons: High computational cost, requires a very good computer.
- **RGB-D based map (e.g. RTAP-Map [[4]](#sources))**:
    - Pros: Easy-to integrate with already existing 3D-mapping.
    - Cons: Computationally heavy and requires robot to have an RGB-D camera.
- **Pre-built 2D Lidar map (e.g. slam_toolbox):**
    - Pros: Reliable and combines sensor data (Lidar, odometry) not very heavy computationally.
    - Cons: Most implementation are only 2D, can experience smudging at higher angular speeds.

For generating an occupancy grid we chose to go with **slam_toolbox** [[5]](#sources)  as it can be run on lower end hardware, which is important because not everyone has a good laptop. Besides that it also isn't too complicated to implement allowing us to focus first on getting everything working as we also had to keep into account that the assignment was time constrained.

### Path-finding algorithms

The path-finding algorithm determines the shortest path towards a goal for the robot to follow.

Different options include:
- **Dijkstra [[7]](#sources)**:
    - Pros: Simple to implement and guarantees the shortest path also able to consider movement costs.
    - Cons: Slow for large grids (O(n²) time complexity [[6]](#sources)) and no heuristic to guide search.
- **A-star [[8]](#sources)**:
    - Pros: Uses heuristics to prioritize search.
    - Cons: More complex in the implementation especially when having to deal with movement costs.
- **Breadth-First Search (BFS)**:
    - Pros: Extremely simple
    - Cons: Inefficient for large grids (O(n²) time complexity [[6]](#sources)) and can't take into account movement costs
- **Depth-First Search (DFS) [[9]](#sources)**:
    - Pros: More efficient than Breadth-First search
    - Cons: Does not guarantee the shortest path can get stuck in an infinite loop

For path-finding we first used **Breadth-First search**, but later progressed to **Dijkstra** as we really need to be able work with weighted cells. The largest bottleneck of the Dijkstra algorithm is its speed, which is very noticeable in the simulation. However knowing this we still chose to use Dijkstra as it is still somewhat simpler than something like A* and as already stated above we had a time constraint, which we really had to keep in mind as we didn't want things too become too complex.

## Reasoning

For the implementation a combination of existing tools are used. These function as a foundation on which the final algorithm is build. Implementing a 2D mapping system that translates the Lidar sensor data into an occupancy grid would have cost a lot of effort so for that [slam_toolbox](https://github.com/SteveMacenski/slam_toolbox) is used. To avoid obstacles [nav2_costmap_2d](https://github.com/ros-navigation/navigation2/tree/main/nav2_costmap_2d) is used. Besides that most of the code seen inside this folder is unique.

For path planning `frontier based exploration` [[10]](#sources) is used as this will always find a good area of the map to move towards and explore. Besides that the `Dijkstra` [[11]](#sources) algorithm is used to find a frontier cell and also find its shortest path from the robot. These two methods work fairly well together and combining them isn't all that much work. It is also beneficial to use Dijkstra as it can plan paths based on certain costs (e.g. rotation of the robot or distance).

## Core logic

The below is a quick overview that describes the core logic behind the path finding algorithm implemented in this folder.

### Algorithm sub parts

- **Occupancy grid map** (based on Lidar sensor data)
- **Frontier based exploration [[10]](#sources)** for determining the frontier edge cell
- **Dijkstra's algorithm [[11]](#sources)** for path planning
- **PID Controller** for navigating the robot to an (x, y) coordinate

### Steps (quick overview)

1. **Retrieve the Occupancy grid** from the ROS2 `/map_2d` topic, which generates a map using `slam_toolbox` based on the input of the Lidar sensor.
2. **Retrieve the costmap** from the ROS2 `/costmap` topic, which generates a costmap based on the map from `/map_2d`.
2. **Use frontier based exploration** to determine all frontier edge cells, i.e. points  on the map that lie between explored areas and unexplored areas. 
3. **Use a path finding algorithm** like Dijkstra or the A* algorithm to determine the closest edge cell relative to the robot.
4. **Reconstruct shortest path** from the outcome of the path finding algorithm.
5. **Calculate the angle and distance** the robot has to move towards to navigate towards the closest edge cell (requires converting grid coordinates to global world coordinates).
6. **Re-evaluate** after the robot has reached the specified edge cell or the edge cell has been marked as explored.

## Implementation

Below is a rough outline of what the code inside [main.py](./ros/packages/path_planning/path_planning/main.py) actually does. This is just a high overview so beware that some crucial operations might not be included in this description.

### 1. Callbacks

First the code waits to receive an occupancy grid published to the ROS2 topic `/map_2d` that then gets converted into a costmap used to avoid obstacles. Inside the costmap parameters file, [here](./ros/nav2_costmap_params.yaml). The size of the robot is given and the `nav2_costmap_2d` package automatically makes walls and other obstacles larger so Dijkstra will never find a path that's too close a distance to an obstacle relative to the robot.

Besides waiting to receive these map the code also waits to receive the position of the robot as this is need as a starting point for Dijkstra's algorithm.

When both of these maps are received in the code step 2 takes place. For the above operation `map_callback()`, `costmap_callback()` & `tf_callback()` are used, which look like this:

```python
def map_callback(self, msg: OccupancyGrid):

    # Debug
    # self.get_logger().info('Received map')

    occupancy_grid = np.array(msg.data).reshape((msg.info.height, msg.info.width))
    self.map = occupancy_grid.copy()

    self.map_origin_ = (msg.info.origin.position.x, msg.info.origin.position.y) # (x, y)
    self.map_resolution_ = msg.info.resolution

    if self.path is None:

        map_origin = (msg.info.origin.position.x, msg.info.origin.position.y) # (x, y)
        map_resolution = msg.info.resolution

        self.frontier_exploration(occupancy_grid, map_origin, map_resolution)

    return
```
*The map_callback() function*

```python
def costmap_callback(self, msg: OccupancyGrid):

    # Debug
    # self.get_logger().info('Received costmap')

    self.costmap = np.array(msg.data).reshape((msg.info.height, msg.info.width))

    return
```
*The costmap_callback() function*

```python
def tf_callback(self):

    try:
        transform = self.tf_buffer.lookup_transform(
                'map_2d',
                'chassis',
                rclpy.time.Time())

        position = transform.transform.translation
        orientation = transform.transform.rotation

        self.robot_position = (position.x, position.y)
        self.robot_orientation = self.quat_euler_angle(orientation.x, orientation.y, orientation.z, orientation.w)

        # Debug
        # self.get_logger().info(f'/tf position: {x, y}')
        # self.get_logger().info(f'/tf orientation: {self.quat_euler_angle(orientation.x, orientation.y, orientation.z, orientation.w)}')

    except TransformException as ex:
        self.get_logger().info(f'Failed to look up transform from frame [chassis] to frame [map_2d]: {ex}')

    return
```
*The tf_callback function*

### 2. Frontier exploration

In the second step the `frontier_exploration()` function is called and a handful of arguments are given to it. These arguments are mainly used inside the Dijkstra algorithm as this needs a lot of data to determine the correct path and translate x and y coordinates between the world and the occupancy grid. The first important data that has to be converted from world coordinates to grid coordinates is the robots current position, which happens in this line of code (using `world_grid_coordinates()`):

```python
# Calculate robots position inside /map
self.get_logger().info("Calculating robots position")

robot_x, robot_y = self.robot_position
starting_position = self.world_grid_coordinates(robot_x, robot_y, map_origin, map_resolution)
```

After that it calls `dijkstra()` to determine the closest frontier cell to the robot and find a path towards it.

### 3. Dijkstra

The exact workings of the `dijkstra()` implementation can be found [here](../dijkstra-algorithm/README.md) so please refer to that for more details.

When Dijkstra is first called it start off by initializing a priority queue that is used to account for certain costs of movements. Using this priority queue it saves any free cells that it finds while looping over the whole occupancy grid starting from the robots current position. It does this kind of like water filling a surface exploring equally in each direction, but where certain directions take higher precedence due to less costs of movement. It also takes into consideration the distance towards the frontier cell using `calc_relative_distance()` to avoid finding a goal in a blind spot of the Lidar (i.e. in the middle of the robot).

Then when it finds a frontier edge cell, i.e. a cell that sits on the border between an unexplored region and free cells. It stops the algorithm and reiterates over the path backwards to find the exact path, which is then returned as a list of grid coordinates. After this the path is used inside `publish_cmd_vel()` to make the robot follow along this path.

### 4. Following the path

The robot follows the path to the frontier cell by first following each waypoint inside the path list returned by `dijkstra()`. For this a PID controller is used to orientate the robot so that it faces the correct angle towards the specified waypoint, after which it moves forward with a constant linear velocity. If at any point in time the frontier cell is explored, goes from `-1` to another value, the path is recalculated following the steps above. The same things happens when the robot reached the final goal. The code for this part is:

```python
def publish_cmd_vel(self):

    twist_msg = Twist()

    # Check whether path exists and is long enough
    if self.path is None or len(self.path) < 2:        
        self.path = None
        return

    column, row = int(self.map_path[-1][0]), int(self.map_path[-1][1])
    neighbours = self.find_neighbouring_cells(self.map, column, row, diagonals=True) 
    values = [self.map[c, r] for (c, r), _ in neighbours]

    # Recalculate path if the final goal has been explored
    if -1 not in values:
        self.get_logger().info('Explored final goal')
        twist_msg.angular.z = 0.0
        twist_msg.linear.x = 0.0
        self.prev_error = 0.0  # Reset PD controller error for the new path
        self.integral_error = 0.0
        self.path = None
        self.cmd_vel.publish(twist_msg)
        return

    # Extract the second coordinate from the path 
    # (i.e. the first coordinate to move towards)
    x, y = self.path[1]

    # Obtain the distance and angle of the robot relative to the goal
    relative_distance = self.calc_relative_distance(x, y)
    relative_angle = self.calc_relative_angle(x, y)

    if relative_distance < self.DISTANCE_THRESHOLD: # Stop when below threshold
        # self.get_logger().info("Waypoint reached")
        self.path.pop(1) # Remove coordinate when reached (move along path)
        self.map_path.pop(0)
        self.prev_error = 0.0
        self.integral_error = 0.0

        if len(self.path) < 2:
            self.path = None
            return

        # Obtain new relative values for next waypoint
        x, y = self.path[1]
        relative_distance = self.calc_relative_distance(x, y)
        relative_angle = self.calc_relative_angle(x, y)

    # First rotate, then move forward
    if abs(relative_angle) > self.ANGLE_THRESHOLD:
        # dt is equal to 0.1, because /tf and /cmd_vel operate at 10hz
        twist_msg.angular.z = self.pid_controller(relative_angle, Kp=0.5, Ki=0.04, Kd=0.2, dt=0.1)
        twist_msg.angular.z = max(-0.5, min(0.5, twist_msg.angular.z)) # Clamp to [-0.5, 0.5]
        twist_msg.linear.x = 0.05  # Don't move while turning
    else:
        # Move phase (facing waypoint)
        twist_msg.angular.z = 0.0
        twist_msg.linear.x = 0.5
            
    self.cmd_vel.publish(twist_msg)

    return
```

### 5. Drawing the map

The occupancy grid, path and robots position are all drawn on a map on the screen using `Matplotlib`. This is especially useful when debugging, but is also very informative for anyone using the algorithm. The code responsible for this doesn't do anything fancy, which is why I won't go into more detail here. The code for this is:

```python
def draw_map(self):

    # TEST
    start = time.time()

    if self.map is None: # or self.costmap is None:
        return

    self.ax.clear()
    # Source: https://matplotlib.org/stable/users/explain/artists/imshow_extent.html#imshow-extent
    self.ax.imshow(self.map, cmap=self.cmap, norm=self.norm,
                    origin='lower') # Reflect the map to align with that of the Gazebo world
    self.ax.set_title("Occupancy Grid")

    if self.map_path:
        y = [y for y, _ in self.map_path]
        x = [x for _, x in self.map_path]
        self.ax.plot(x, y,  c='lime', linewidth=3)

        y, x = self.map_path[-1]
        self.ax.plot(x, y, marker='x', markersize=6, c='black', markeredgewidth=1.2)

    if self.robot_position and self.map_origin_:
        robot_x, robot_y = self.robot_position
        y, x = self.world_grid_coordinates(robot_x, robot_y, self.map_origin_, self.map_resolution_)
        self.ax.plot(x, y, marker='s', markersize=12, c='black', markerfacecolor='none', markeredgewidth=2, markeredgecolor='black')

    self.fig.canvas.draw()
    self.fig.canvas.flush_events()
    plt.pause(0.001)

    # TEST
    elapsed = time.time() - start    
    self.get_logger().info(f'draw_map took {elapsed:.3f}s')
```

## Setup

- The setup in this demo requires that you've first followed the instructions inside the [README.md](/workspace/models/README.md) from the main simulation and successfully ran it. So make sure you've done that first.

    - Navigate to the path-finding-demo folder:

        ```bash
        cd /workspace/prototypes/path-finding-demo
        ```
    - Source ROS2:

        ```bash
        source /opt/ros/jazzy/setup.bash
        ```
    - Build the Colcon package:

        ```bash
        colcon build
        ```
    - Source the ROS2 workspace:

        ```bash
        source install/setup.bash
        ```
    - Launch the simulation:

        ```bash
        ros2 launch simulation.launch.py
        ```

## Advice

My advice to anyone using this algorithm for autonomous exploration is to be mindful of the limitations. Mainly that it won't always find the quickest route and might therefore lose precious time.

Although the algorithm is working and useable it is far from being ready for an actual autonomous drive under extreme conditions for example, in a burning building. This is due to the fact that the current algorithm is missing a lot of critical features that are absolutely necessary inside any high stakes environment.

Below are some of the most important shortcomings:

- The algorithm uses data from a 2D Lidar, meaning it can only detect obstacles that appear exactly at a certain height. You can imagine how some obstacles can easily be missed and bumped into. To fix this one would have to use sensor data from a 3D data, but computationally that's a lot heavier. This is something that would've made the development of the code a lot harder, which is why it hasn't been implemented already.
- The robot has trouble following the path exactly at higher speeds due to using a simple PID solution for the control of the robots movements. A similar more advanced algorithm would make use of a specialized path following algorithm, e.g. Pure pursuit tracking[[12]](#sources) or Stanley control[[13]](#sources). This would not only make the robot be able to move faster, but also make the robot less prone to accidentally hitting objects in certain sharp turns.
- Dijkstra is relatively slow compared to other algorithms, like A* [[14]](#sources) . Dijkstra adds a lot of extra runtime to the algorithm making the robot have to stop in between path calculations. A more optimized algorithm using a specialize data structure would already improve the algorithm immensely. This is especially crucial in larger environments where it would have to iterate over a much larger area.
- The selection of frontier cells doesn't take into consideration the amount of area that would potentially be explored. Right now it just find the closest unexplored region, but in some scenarios these regions can be very small compared to other parts of the map where a much larger are is waiting to be explored. Also more than once the robot explores a region that really doesn't hold a lot of essential information, because the regions is surrounded by free cells. This can be fixed by first clustering areas of unknown cells and comparing their total count when finding the next frontier to move towards.
- Moving obstacles aren't handled correctly. If a dynamic obstacle is detected on the Lidar, but a path is still being followed by the robot it won't adjust based on the new information. This makes it prone to collisions with moving objects.

## Sources

1. https://atsushisakai.github.io/PythonRobotics/modules/3_mapping/lidar_to_grid_map_tutorial/lidar_to_grid_map_tutorial.html
2. https://learnopencv.com/lidar-slam-with-ros2/
3. https://google-cartographer.readthedocs.io/en/latest/
4. https://introlab.github.io/rtabmap/
5. https://github.com/SteveMacenski/slam_toolbox
6. https://www.researchgate.net/figure/Comparison-of-path-finding-algorithms_tbl1_308034798
7. https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
8. https://en.wikipedia.org/wiki/A*_search_algorithm
9. https://www.geeksforgeeks.org/dsa/applications-of-depth-first-search/
10. https://awabot.com/en/autonomous-exploration-method-frontiers/
11. https://www.redblobgames.com/pathfinding/a-star/introduction.html
12. https://wiki.purduesigbots.com/software/control-algorithms/basic-pure-pursuit
13. https://atsushisakai.github.io/PythonRobotics/modules/6_path_tracking/stanley_control/stanley_control.html
14. https://en.wikipedia.org/wiki/A*_search_algorithm
15. https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
16. https://www.cs.cmu.edu/~motionplanning/papers/sbp_papers/integrated1/yamauchi_frontiers.pdf
17. https://mechwiz.github.io/Portfolio/jackal.html
18. https://gazebosim.org/docs/latest/sensors/
<!-- 6. https://robotics.stackexchange.com/questions/98107/how-to-get-obstacle-distance-and-angle-by-using-lidar -->
