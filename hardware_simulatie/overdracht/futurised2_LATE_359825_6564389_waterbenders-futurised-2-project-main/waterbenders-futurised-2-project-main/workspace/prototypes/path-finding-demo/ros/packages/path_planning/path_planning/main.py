from tracemalloc import start
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Twist
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from queue import Queue, PriorityQueue
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import time
import math

class FrontierExploration(Node):

    # Constants
    DISTANCE_THRESHOLD = 0.15
    ANGLE_THRESHOLD = 15 * (math.pi / 180)
    DISTANCE_TO_FRONTIER = 6.5

    def __init__(self):
        super().__init__('frontier_exploration')

        self.map = None
        self.costmap = None

        self.robot_position = None
        self.robot_orientation = 0.0

        self.path = None
        self.map_path = None

        self.prev_error = 0.0
        self.integral_error = 0.0

        self.map_2d = self.create_subscription(
            OccupancyGrid,
            '/map_2d',
            self.map_callback,
            10 # Queue size
        )

        self.global_costmap = self.create_subscription(
            OccupancyGrid,
            '/costmap',
            self.costmap_callback,
            10
        )

        self.cmd_vel = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.tf_timer = self.create_timer(0.1, self.tf_callback)

        # Timer to publish to cmd_vel topic(e.g., 10 Hz)
        self.cmd_vel_timer = self.create_timer(0.1, self.publish_cmd_vel)

        # NOTE: Lowered time/s for testing puroposes (was 0.2)
        self.draw_map_timer = self.create_timer(1.0, self.draw_map)

        # Live mapping of path-finding data
        plt.ion() # Enable interactive plotting
        self.fig, self.ax = plt.subplots()
        self.cmap = ListedColormap(['gray', 'white', 'black'])
        self.norm = BoundaryNorm([-1.5, -0.5, 0.5, 100.5], self.cmap.N)

        # The origin in the Gazebo simulation is always located in the bottom left corner, 
        # so where x, y are both minus (-x, -y). It changes as the robot moves
        # further into unknown territory
        self.map_origin_ = None
        self.map_resolution_ = None

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

    def costmap_callback(self, msg: OccupancyGrid):

        # Debug
        # self.get_logger().info('Received costmap')

        self.costmap = np.array(msg.data).reshape((msg.info.height, msg.info.width))

        return

    def frontier_exploration(self, occupancy_grid, map_origin, map_resolution):

        # TEST
        start = time.time()

        # The below if-statements are safety checks to avoid concurrency problems

        # Robot hasn't moved yet (/pose msg hasn't been sent out yet)
        if self.robot_position is None:
            self.get_logger().warn("Robot position unknown")
            return

        # Costmap doesn't exist yet
        if self.costmap is None:
            self.get_logger().warn("Costmap doesn't exist")
            return

        # Calculate robots position inside /map
        self.get_logger().info("Calculating robots position")

        robot_x, robot_y = self.robot_position
        starting_position = self.world_grid_coordinates(robot_x, robot_y, map_origin, map_resolution)
        
        # Calculate a new path
        self.get_logger().info("New path is being calculated")

        path = self.dijkstra(occupancy_grid, starting_position, map_origin, map_resolution)

        # FIX: Remove the first few waypoints to avoid the robot 
        # having to move behind itself for sudden turns in orientation
        if len(path) > 10:
            del path[0:10]

        self.map_path = path.copy()

        self.path = [self.grid_world_coordinates(column, row, map_origin, map_resolution) for (column, row) in path]

        # TEST
        # self.get_logger().info(f"Lenght of map_path & path: {len(self.map_path)}, {len(self.path)}")
        # self.get_logger().info(f"Contents: {self.map_path}, {self.path}")

        # TEST
        elapsed = time.time() - start    
        self.get_logger().info(f'frontier_exploration took {elapsed:.3f}s')

        return

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

    # Error is equal to the proportional error
    def pid_controller(self, error, Kp, Ki, Kd, dt):

        self.integral_error += error * dt # Accumulates the error over time
        derivative = (error - self.prev_error) / dt # Difference between errors

        # Store previous errors for derivative term
        self.prev_error = error

        # Output
        u = Kp * error + Ki * self.integral_error + Kd * derivative

        return u

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

        # Debug
        # self.get_logger().info(f"Current position: x={self.robot_position[0]}, y={self.robot_position[1]}")
        # self.get_logger().info(f"Current goal    : x={x}, y={y}")

        # Debug
        # self.get_logger().info(f"Published cmd_vel: linear.x={twist_msg.linear.x}, angular.z={twist_msg.angular.z}")

        return

    def quat_euler_angle(self, x, y, z, w):

        siny_cosp = 2.0 * (w * z + x * y)    
        cosy_cosp = 1.0 - 2.0 * (y*y + z*z)    

        return math.atan2(siny_cosp, cosy_cosp)

    # Convert a grid cell (x, y) to real-world coordinates
    def grid_world_coordinates(self, column_index, row_index, map_origin, map_resolution): # y, x

        world_x = (row_index * map_resolution) + map_origin[0]
        world_y = (column_index * map_resolution) + map_origin[1]

        return world_x, world_y

    # Convert real-world coordinates to grid cell (x, y)
    def world_grid_coordinates(self, x_coordinate, y_coordinate, map_origin, map_resolution):

        # Source bug: https://stackoverflow.com/questions/34952651/only-integers-slices-ellipsis-numpy-newaxis-none-and-intege
        column_index = int((y_coordinate - map_origin[1]) / map_resolution)
        row_index = int((x_coordinate - map_origin[0]) / map_resolution)

        return column_index, row_index

    def find_neighbouring_cells(self, array, column_index, row_index, diagonals=False):

        height, width = array.shape

        neighbours = []

        # All neighbouring cells (including diagonals)
        directions = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1)
        ]

        for i, (x, y) in enumerate(directions):
            if diagonals == False and i > 3:
                break
            ri = row_index + x
            ci = column_index + y
            # Check whether each cell has a neighbour (isn't at the edge of the map)
            if 0 <= ri < width and 0 <= ci < height:
                cost = 1.414 if i > 3 else 1.0 
                neighbours.append(((ci, ri), cost))

        return set(neighbours)

    def calc_relative_distance(self, target_x, target_y):

        robot_x, robot_y = self.robot_position

        # Calculate the distance between the robot and the target
        distance_x = target_x - robot_x
        distance_y = target_y - robot_y

        relative_distance = math.sqrt(distance_x**2 + distance_y**2)

        return relative_distance

    def calc_relative_angle(self, target_x, target_y):

        robot_x, robot_y = self.robot_position

        # Calculate the distance between the robot and the target
        distance_x = target_x - robot_x
        distance_y = target_y - robot_y

        absolute_angle = math.atan2(distance_y, distance_x)
        relative_angle = absolute_angle - self.robot_orientation

        # Normalize to [-π, π]
        relative_angle = (relative_angle + math.pi) % (2 * math.pi) - math.pi

        return relative_angle

    def dijkstra(self, occupancy_grid, starting_position, map_origin, map_resolution):

        # TEST
        start = time.time()
        
        # starting_position is passed as (col, row)
        frontier = PriorityQueue()
        frontier.put((0.0, starting_position))
        came_from = {starting_position: None}
        cost_so_far = {starting_position: 0.0}
        
        frontier_cell_found = False

        while not frontier.empty():
            _, current = frontier.get()
            c_curr, r_curr = current

            # look for 8-way directional neighbours
            neighbours = self.find_neighbouring_cells(occupancy_grid, c_curr, r_curr, diagonals=True)

            # for each neighbour calculate the new cost and update the frontier if it's a better path
            for ni, step_cost in neighbours:
                c, r = ni

                # calculate the world coordinates of the current cell to check distance to robot
                world_x, world_y = self.grid_world_coordinates(c, r, map_origin, map_resolution)
                distance_to_robot = self.calc_relative_distance(world_x, world_y)
                rotation_to_robot = abs(self.calc_relative_angle(world_x, world_y))

                new_cost = cost_so_far[current] + (0.8 * distance_to_robot + 0.2 * rotation_to_robot) + step_cost

                # if this path to the neighbour is better than any previous one
                if ni not in came_from or new_cost < cost_so_far[ni]:
                    # if this cell is unknown (-1) and meets minimum distance requirement we've found a valid frontier cell
                    if occupancy_grid[ni] == -1 and distance_to_robot >= self.DISTANCE_TO_FRONTIER:
                        frontier_cell_found = True
                        break
                    # check for obstacles in the costmap and skip those
                    elif self.costmap[ni] == 0:
                        cost_so_far[ni] = new_cost
                        frontier.put((new_cost, ni)) # Priority, value
                        came_from[ni] = current

            if frontier_cell_found:
                break

        if not frontier_cell_found:
            return [starting_position]

        # reconstruct path
        path = []
        while current != starting_position:
            path.append(current)
            current = came_from[current]
        path.append(starting_position)
        path.reverse()

        # TEST
        elapsed = time.time() - start    
        self.get_logger().info(f'dijkstra took {elapsed:.3f}s')

        return path

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

def main(args=None):
    rclpy.init(args=args)
    node = FrontierExploration()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
