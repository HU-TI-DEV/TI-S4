import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
import numpy as np
from tf2_ros import Buffer, TransformListener
import math
from queue import Queue
import matplotlib.pyplot as plt

class MapAnalyzer(Node):

    # Constants
    DISTANCE_THRESHOLD = 0.75

    def __init__(self):
        super().__init__('path_finding')

        self.grid = None

        self.grid_origin = None
        self.grid_resolution = 0.0

        self.grid_width = 0
        self.grid_height = 0

        self.robot_position = None
        self.robot_orientation = 0.0

        self.world_path = None

        self.prev_error = 0.0

        self.map = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            10 # Queue size
        )

        self.cmd_vel = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.pose = self.create_subscription(
            PoseWithCovarianceStamped,
            '/pose',
            self.pose_callback,
            10
        )

        # Timer to publish to cmd_vel topic(e.g., 10 Hz)
        self.timer = self.create_timer(0.1, self.publish_cmd_vel)

    def pose_callback(self, msg: PoseWithCovarianceStamped):

        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation

        self.robot_position = (position.x, position.y)
        self.robot_orientation = self.quat_euler_angle(orientation.x, orientation.y, orientation.z, orientation.w)

        # Debug
        # self.get_logger().info(f'Received position: {position.x, position.y}')
        # self.get_logger().info(f'Received orientation: {self.quat_euler_angle(orientation.x, orientation.y, orientation.z, orientation.w)}')

    def quat_euler_angle(self, x, y, z, w):
        siny_cosp = 2.0 * (w * z + x * y)    
        cosy_cosp = 1.0 - 2.0 * (y*y + z*z)    
        return math.atan2(siny_cosp, cosy_cosp)

    def calc_distance_rotation(self, target_x, target_y):

        robot_x, robot_y = self.robot_position

        # Calculate the distance between the robot and the target
        distance_x = target_x - robot_x
        distance_y = target_y - robot_y

        relative_distance = math.sqrt(distance_x**2 + distance_y**2)

        absolute_angle = math.atan2(distance_y, distance_x)
        relative_angle = absolute_angle - self.robot_orientation
        relative_angle = (relative_angle + math.pi) % (2 * math.pi) - math.pi # Normalize to [-π, π]

        return relative_distance, relative_angle

    def pd_controller(self, error, Kp, Kd, dt):
        derivative = (error - self.prev_error) / dt
        # Store previous error for derivative term
        self.prev_error = error

        # Output
        u = Kp * error + Kd * derivative

        return u

    def publish_cmd_vel(self):

        twist_msg = Twist()

        # Check whether world_path exists
        if self.world_path is None: # Using 'is None' is faster then checking with ==
            self.get_logger().info('No path exists yet')
            return

        if len(self.world_path) <= 1:
            self.get_logger().info('Path is too short or has already been completed')
            twist_msg.angular.z = 0.0
            twist_msg.linear.x = 0.0
            self.cmd_vel.publish(twist_msg)
            return

        # Extract the second coordinate from the path (i.e. the first coordinate to move towards)
        x, y = self.world_path[1]

        # Test messages
        self.get_logger().info(f"Current position: x={self.robot_position[0]}, y={self.robot_position[1]}")
        self.get_logger().info(f"Current goal    : x={x}, y={y}")

        relative_distance, relative_angle = self.calc_distance_rotation(x, y)

        if relative_distance < self.DISTANCE_THRESHOLD: # Stop when below threshold
            self.world_path.pop(1) # Remove the coordinates when reached,
            # so that each function call it will move along the planned path
            twist_msg.angular.z = 0.0 # Stop turning completely
            twist_msg.linear.x = 0.4

            # Debug messages
            self.get_logger().warn("Goal reached")

        else:
            # dt is equal to 0.2, because /pose changes at 5hz
            twist_msg.angular.z = self.pd_controller(relative_angle, Kp=0.5, Kd=0.2, dt=0.2)
            twist_msg.angular.z = max(-1.0, min(1.0, twist_msg.angular.z)) # Clamp to [-0.5, 0.5]

            # twist_msg.linear.x = 0.2  # Fixed forward speed (deprecated)

            # Linear speed that decreases as the relative_distance changes (slows down as you approach)
            linear_speed = 0.4 * (1 - min(1.0, relative_distance / 0.5))  # Max speed at 0.5m away
            twist_msg.linear.x = max(0.1, linear_speed)  # Never go below 0.05 m/s

        self.cmd_vel.publish(twist_msg)

        # Debug
        # self.get_logger().info(f"Published cmd_vel: linear.x={twist_msg.linear.x}, angular.z={twist_msg.angular.z}")

        return
        
    # Convert real-world coordinates to grid cell (x, y)
    def world_grid_coordinates(self, ix, iy):

        # Calculate the grid x, y coordinates and invert the y-axis. 
        # The round() function is used to convert the decimal values to the nearest 
        # grid cell, because cells are always whole values and cannot be fractional indices
        grid_x = round((ix - self.grid_origin[0]) / self.grid_resolution)
        grid_y = self.grid_height - 1 - round((iy - self.grid_origin[1]) / self.grid_resolution)

        # Clamp to grid bounds to avoid the robots position being outside the grid. 
        # This happens when the map generated by the Lidar hasn't explored the region 
        # the robot is currently in (e.g. at the start where the Lidar only scans forward).
        grid_x = max(0, min(self.grid_width - 1, grid_x))
        grid_y = max(0, min(self.grid_height - 1, grid_y))

        return grid_y, grid_x

    # Convert a grid cell (x, y) to real-world coordinates
    def grid_world_coordinates(self, iy, ix):

        world_x = self.grid_origin[0] + ix * self.grid_resolution
        world_y = self.grid_origin[1] + (self.grid_height - 1 - iy) * self.grid_resolution

        return world_x, world_y

    def find_neighbouring_cells(self, array, iy, ix, diagonals=False):

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
            nx = ix + x
            ny = iy + y
            # Check whether each cell has a neighbour (isn't at the edge of the map)
            if 0 <= nx < width and 0 <= ny < height:
                index_pair = ny, nx # x and y are reversed so (iy, ix) is the correct way
                neighbours.append(index_pair)

        return neighbours

    # Scans the occupancy grid and identifies all free cells (0) adjacent to unknown cells (-1), resulting in frontier edge cells or candidate boundaries
    def candidate_boundaries(self, grid):

        height, width = grid.shape
        candidate_boundaries = []

        for iy in range(height):
            for ix in range(width):

                if grid[iy, ix] == -1:
                    index_pair = iy, ix
                    neighbours = self.find_neighbouring_cells(grid, iy, ix, diagonals=True)
                    neighbouring_values = [grid[ny, nx] for ny, nx in neighbours]
                    # self.get_logger().info(f"{neighbours}")
                    # self.get_logger().info(f"{neighbouring_values}")

                    if 3 <= neighbouring_values.count(-1) <= 4:

                        world_x, world_y = self.grid_world_coordinates(iy, ix)
                        if self.calc_distance_rotation(world_x, world_y)[0] <= 0.95:
                            continue

                        neighbours = self.find_neighbouring_cells(grid, iy, ix, diagonals=False)
                        for ni in neighbours:
                            if grid[ni] == 0 and ni not in candidate_boundaries:
                                candidate_boundaries.append(ni)

                    # for ni in neighbours:
                        # Check if neighbouring cell is unknown (-1) and coordinates 
                        # haven't already been added to 'candidate_boundaries' (avoids duplicates)
                        # if grid[ni] == -1:
                        #     index_pair = iy, ix
                        #     candidate_boundaries.append(index_pair)
                        #     break

        # self.get_logger().info(f"{candidate_boundaries}")
        return candidate_boundaries

    def find_edge_cells(self, grid):

        height, width = grid.shape
        edge_cells = []

        for iy in range(height):
            for ix in range(width):

                if grid[iy, ix] == 0:
                    index_pair = iy, ix
                    neighbours = self.find_neighbouring_cells(grid, iy, ix, diagonals=True)

                    for ni in neighbours:
                        # Check if neighbouring cell is unknown (-1) and coordinates 
                        if grid[ni] == -1 and index_pair not in edge_cells:
                            edge_cells.append(index_pair)
                            break

        # self.get_logger().info(f"{candidate_boundaries}")
        return edge_cells

    def cluster_edge_cells(self, edge_cells, grid):

        height, width = grid.shape
        clusters = []
        visited = set()

        for cell in edge_cells:
            if cell in visited:
                continue

            cluster = []
            frontier = Queue()
            frontier.put(cell)
            visited.add(cell)

            while not frontier.empty():

                current = frontier.get()
                cluster.append(current)

                neighbours = self.find_neighbouring_cells(grid, current[0], current[1], diagonals=False)

                for ni in neighbours:
                    if ni not in edge_cells:
                        continue
                    elif ni not in visited:
                        frontier.put(ni)
                        visited.add(ni)

            clusters.append(cluster)
                        
        return clusters

    def candidate_boundaries_2(self, grid):

        candidate_boundaries = []

        edge_cells = self.find_edge_cells(grid)
        clusters = self.cluster_edge_cells(edge_cells, grid)

        self.get_logger().info(f"Full cluster list: {clusters}")
        for cluster in clusters:

            if len(cluster) < 3:
                continue

            # candidate_boundaries.extend(cluster) # Extend the list with the items in cluster
            for index_pair in cluster:
                world_x, world_y = self.grid_world_coordinates(index_pair[0], index_pair[1])
                if self.calc_distance_rotation(world_x, world_y)[0] <= 0.95:
                    continue

                candidate_boundaries.append(index_pair)

        return candidate_boundaries

    # Source: https://www.redblobgames.com/pathfinding/a-star/introduction.html
    # Scans grid and returns the first step in the direction of the closest valid edge cell (candidate boundary)
    def breadth_first_search(self, grid, start: tuple):

        edge_cells = self.candidate_boundaries(grid)

        if not edge_cells:
            self.get_logger().warn("No frontier cells found")

        frontier = Queue()
        frontier.put(start)
        reached = {}
        reached[start] = None

        while not frontier.empty():

            """
                Normally the edge cell closest to the robot is selected as the next path to move towards. 
                However because of false unknown cells (-1), which are actaully free (0) but wrongly identified.
                The closest path will always be a random value somewhere close to the robots proximity.

                To temporarily fix this the below statements exits the function prematurely once the last
                edge cell (one with greatest distance from the robot) has been found, i.e. when 'edge_cells' 
                is empty
            """
            # if not edge_cells:
            #     break

            current = frontier.get()
            neighbours = self.find_neighbouring_cells(grid, current[0], current[1])

            # Exit the loop prematurely when a frontier 
            # edge cell has been reached and remove it value
            if current in edge_cells:
                edge_cells.remove(current)
                break

            for ni in neighbours:
                if ni not in reached and grid[ni] != 100:
                    # Below doesn't allow -1
                    # if ni not in reached and grid[ni] == 0:
                    frontier.put(ni)
                    reached[ni] = current

        path = []
        while current != start:
            path.append(current)
            current = reached[current]
        path.append(start)
        path.reverse()

        # Test messages
        # print("Reached: ", reached)
        # print("Values of reached: ", [grid[ni] for ni, _ in reached.items()])

        return path
        
    def map_callback(self, msg: OccupancyGrid):

        self.get_logger().info('Received map')

        # Debug
        # if self.world_path is not None:
        #     wx, wy = self.world_path[-1]
        #     self.get_logger().warn(f"Final goal grid coordinates (y, x): {self.world_grid_coordinates(wx, wy)}")

        self.grid = np.array(msg.data).reshape((msg.info.height, msg.info.width))

        # The origin in the Gazebo simulation is always located in the bottom left corner, 
        # so where x, y are both minus (-x, -y). It changes as the robot moves
        # further into unknown territory
        self.grid_origin = (msg.info.origin.position.x, msg.info.origin.position.y) # (x, y)
        self.grid_resolution = msg.info.resolution
        self.grid_width = msg.info.width
        self.grid_height = msg.info.height

        # Debug
        # self.get_logger().info(f'Map origin: {self.grid_origin}')
        # self.get_logger().info(f'Map resolution: {self.grid_resolution}')
        # self.get_logger().info(f'Map width: {self.grid_width}')
        # self.get_logger().info(f'Map height: {self.grid_height}')

        # Additional check to determine whether the robot hasn't moved (i.e. a /pose msg hasn't been sent out yet)
        if self.robot_position is None:
            self.get_logger().warn("Robot position unknown")
            return

        # Skip if the robot is outside the current map bounds
        # robot_x, robot_y = self.robot_position
        # if (robot_x < self.grid_origin[0] or # Left of map
        #     robot_x > self.grid_origin[0] + self.grid_width * self.grid_resolution or # Right of map
        #     robot_y < self.grid_origin[1] or # Below map
        #     robot_y > self.grid_origin[1] + self.grid_height * self.grid_resolution): # Above map
        #     self.get_logger().warn("Robot is outside the current map bounds. Waiting for map update...")
        #     return

        # Skip if a path is still being executed
        if self.world_path is not None:
            if len(self.world_path) > 1:
                self.get_logger().warn("Current path hasn't been fully completed")
                return

        self.get_logger().warn("New path is being calculated")

        # Calculate a new path
        grid_position = self.world_grid_coordinates(self.robot_position[0], self.robot_position[1])
        grid_path = self.breadth_first_search(self.grid, grid_position)
        self.world_path = [self.grid_world_coordinates(cell_y, cell_x) for (cell_y, cell_x) in grid_path]

        # Debug
        self.get_logger().warn(f"Final goal (x, y): {self.world_path[-1]}")
        # self.get_logger().info(f"Grid path length: {len(grid_path)}, path: {grid_path[:5]}")

        return
 
def main(args=None):
    rclpy.init(args=args)
    node = MapAnalyzer()

    """
    TESTS
    """

    # Values meaning:
    # -1 = unknown
    # 0  = free
    # 100 = occupied

    # Width of 4 and height of 3
    arr = np.array([ 
        [0, 100, 100, -1], 
        [0, 0, 0, 100],
        [-1, 0, 0, -1]
    ])

    arr2 = np.array([ 
        [-1, -1, 0, -1], 
        [-1, -1, 0, 100],
        [-1, 0, 0, -1]
    ])
    
    assert node.find_neighbouring_cells(arr, 0, 0) == [(1, 0), (0, 1)], "4-way neighbours don't match"
    assert node.find_neighbouring_cells(arr, 0, 0, True) == [(1, 0), (0, 1), (1, 1)], "Diagonal neighbours don't match"

    # node.candidate_boundaries(arr2)
    # assert node.candidate_boundaries(arr) == [(1, 0), (2, 1), (2, 2)], "Candidate boundaries are invalid"

    # assert node.breadth_first_search(arr, (0, 0)) == [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3)], "Custom breadth first search invalid"

    try:
        rclpy.spin(node)  # Run until ctrl-c is pressed
    except KeyboardInterrupt:
        pass

    # After ctrl-c plot the latest map
    if node.grid is not None:

        plt.imshow(node.grid, cmap='gray')
        plt.title("Occupancy Grid")
        plt.show()

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
