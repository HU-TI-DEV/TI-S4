#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

import numpy as np
import heapq
from collections import defaultdict

from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped, Twist
from visualization_msgs.msg import Marker, MarkerArray
import math


class AStarPathfinder:
    """A* pathfinding in een occupancy grid"""
    
    def __init__(self, grid, resolution, origin_x, origin_y):
        """
        grid: 2D numpy array (0=free, 100=occupied)
        resolution: kaart resolutie (m/cell)
        origin_x, origin_y: wereld coördinaten van grid origin
        """
        self.grid = grid
        self.resolution = resolution
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.height, self.width = grid.shape
        
    def world_to_grid(self, wx, wy):
        """Converteer wereld coördinaten naar grid coördinaten"""
        gx = int((wx - self.origin_x) / self.resolution)
        gy = int((wy - self.origin_y) / self.resolution)
        return gx, gy
    
    def grid_to_world(self, gx, gy):
        """Converteer grid coördinaten naar wereld coördinaten"""
        wx = self.origin_x + gx * self.resolution
        wy = self.origin_y + gy * self.resolution
        return wx, wy
    
    def is_valid(self, x, y):
        """Check of cell geldig en vrij is"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.grid[y, x] < 50
    
    def heuristic(self, x1, y1, x2, y2):
        """Euclidische afstand heuristic"""
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    def get_neighbors(self, x, y):
        """8-directionale buren"""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.is_valid(nx, ny):
                    cost = 1.414 if (dx != 0 and dy != 0) else 1.0
                    neighbors.append((nx, ny, cost))
        return neighbors
    
    def find_path(self, start_wx, start_wy, goal_wx, goal_wy):
        """
        A* pathfinding van start naar goal
        Returns lijst van (x, y) tuples in wereld coördinaten, of None
        """
        start_x, start_y = self.world_to_grid(start_wx, start_wy)
        goal_x, goal_y = self.world_to_grid(goal_wx, goal_wy)
        
        if not self.is_valid(start_x, start_y) or not self.is_valid(goal_x, goal_y):
            return None
        
        open_set = []
        counter = 0
        heapq.heappush(open_set, (0, counter, start_x, start_y))
        
        came_from = {}
        g_score = defaultdict(lambda: float('inf'))
        g_score[(start_x, start_y)] = 0
        
        closed_set = set()
        
        while open_set:
            _, _, x, y = heapq.heappop(open_set)
            
            if (x, y) in closed_set:
                continue
            
            if x == goal_x and y == goal_y:
                path = []
                current = (x, y)
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append((start_x, start_y))
                path.reverse()
                
                world_path = [self.grid_to_world(px, py) for px, py in path]
                return world_path
            
            closed_set.add((x, y))
            
            for nx, ny, cost in self.get_neighbors(x, y):
                if (nx, ny) in closed_set:
                    continue
                
                tentative_g = g_score[(x, y)] + cost
                
                if tentative_g < g_score[(nx, ny)]:
                    came_from[(nx, ny)] = (x, y)
                    g_score[(nx, ny)] = tentative_g
                    
                    f_score = tentative_g + self.heuristic(nx, ny, goal_x, goal_y)
                    counter += 1
                    heapq.heappush(open_set, (f_score, counter, nx, ny))
        
        return None


def simple_dilate(grid, iterations=1):
    """
    Simple dilation zonder scipy.
    Spreidt occupied cells uit zodat we muur-edges kunnen detecteren.
    """
    result = grid.copy()
    for _ in range(iterations):
        dilated = grid.copy()
        h, w = grid.shape
        for y in range(1, h-1):
            for x in range(1, w-1):
                # Check 3x3 neighborhood
                neighborhood = result[y-1:y+2, x-1:x+2]
                if np.any(neighborhood):
                    dilated[y, x] = 1
        result = dilated
    return result


def find_connected_components(binary_grid):
    """
    Find connected components in binary grid zonder scipy.
    Returns labeled grid en aantal components.
    """
    h, w = binary_grid.shape
    labeled = np.zeros((h, w), dtype=np.int32)
    label = 0
    
    for y in range(h):
        for x in range(w):
            if binary_grid[y, x] and labeled[y, x] == 0:
                # BFS flood fill
                label += 1
                queue = [(y, x)]
                labeled[y, x] = label
                
                while queue:
                    cy, cx = queue.pop(0)
                    # Check 4-connected neighbors
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = cy + dy, cx + dx
                        if (0 <= ny < h and 0 <= nx < w and 
                            binary_grid[ny, nx] and labeled[ny, nx] == 0):
                            labeled[ny, nx] = label
                            queue.append((ny, nx))
    
    return labeled, label


class RoomDetector(Node):

    def __init__(self):
        super().__init__('room_detector')

        # State
        self.map_data = None
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0
        self.current_path = None
        self.current_path_idx = 0
        self.pathfinder = None
        
        # Gedetecteerde openingen
        self.openings = []
        self.visited_openings = set()
        self.marker_id_counter = 0

        # Subscriptions
        self.map_sub = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            10
        )

        # Publishers
        self.markers_pub = self.create_publisher(MarkerArray, '/room_markers', 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Timers
        self.detect_timer = self.create_timer(2.0, self.detect_openings)
        self.drive_timer = self.create_timer(0.1, self.follow_path)

        self.get_logger().info('Room detector (Pure NumPy) started')


    def map_callback(self, msg):
        self.map_data = msg
        
        # Maak pathfinder aan
        w = msg.info.width
        h = msg.info.height
        res = msg.info.resolution
        origin = msg.info.origin.position
        
        data = np.array(msg.data, dtype=np.int8).reshape((h, w))
        self.pathfinder = AStarPathfinder(data, res, origin.x, origin.y)
        
        self.get_logger().info(f'Map received: {w}x{h}, resolution: {res}m')


    def detect_openings(self):
        """Detecteer openingen (doorways) tussen kamers"""
        if self.map_data is None:
            return
        
        w = self.map_data.info.width
        h = self.map_data.info.height
        res = self.map_data.info.resolution
        origin = self.map_data.info.origin.position

        data = np.array(self.map_data.data, dtype=np.int8).reshape((h, w))
        
        # Zuiver NumPy processing
        free = (data == 0).astype(np.uint8)
        occupied = (data > 50).astype(np.uint8)
        
        # ---- Openings detection via dilation ----
        # Dilateer occupied cells om muren op te sporen
        occupied_dilated = simple_dilate(occupied, iterations=1)
        
        # Edges: vrije cellen naast muren
        edge = free & occupied_dilated
        
        # ---- Find connected components ----
        labeled, num_features = find_connected_components(edge)
        
        openings_grid = []
        
        for label_id in range(1, num_features + 1):
            cluster_coords = np.argwhere(labeled == label_id)
            
            if len(cluster_coords) > 5:  # Minimale cluster grootte
                # Bereken cluster centroid
                cluster_y = np.mean(cluster_coords[:, 0])
                cluster_x = np.mean(cluster_coords[:, 1])
                
                world_x = origin.x + cluster_x * res
                world_y = origin.y + cluster_y * res
                
                openings_grid.append((world_x, world_y))
        
        self.openings = openings_grid
        if len(openings_grid) > 0:
            self.get_logger().info(f'Detected {len(openings_grid)} openings')
        self.publish_markers()


    def publish_markers(self):
        """Publiceer alle gedetecteerde openingen als markers"""
        marker_array = MarkerArray()
        
        # Clear old markers (delete first 50)
        for i in range(50):
            marker = Marker()
            marker.header.frame_id = "map"
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.id = i
            marker.action = Marker.DELETE
            marker_array.markers.append(marker)
        
        # Add new markers
        for i, (x, y) in enumerate(self.openings):
            marker = Marker()
            marker.header.frame_id = "map"
            marker.header.stamp = self.get_clock().now().to_msg()
            
            marker.type = Marker.CYLINDER
            marker.action = Marker.ADD
            marker.id = i + 100  # Offset to avoid conflicts
            
            marker.pose.position.x = x
            marker.pose.position.y = y
            marker.pose.position.z = 0.3
            
            marker.pose.orientation.w = 1.0
            
            marker.scale.x = 0.4
            marker.scale.y = 0.4
            marker.scale.z = 0.6
            
            # Rood als niet bezocht, groen als bezocht
            if (x, y) in self.visited_openings:
                marker.color.g = 1.0
                marker.color.r = 0.0
            else:
                marker.color.r = 1.0
                marker.color.g = 0.0
            
            marker.color.b = 0.0
            marker.color.a = 1.0
            
            marker_array.markers.append(marker)
        
        self.markers_pub.publish(marker_array)


    def follow_path(self):
        """Volg berekend pad naar volgende opening"""
        
        if self.current_path is None or self.current_path_idx >= len(self.current_path):
            if self.pathfinder is None or not self.openings:
                self.cmd_pub.publish(Twist())
                return
            
            # Vind niet-bezochte opening
            next_opening = None
            for opening in self.openings:
                if opening not in self.visited_openings:
                    next_opening = opening
                    break
            
            if next_opening is None:
                self.get_logger().info("Alle openingen bezocht!")
                self.cmd_pub.publish(Twist())
                return
            
            # Bereken pad met A*
            self.current_path = self.pathfinder.find_path(
                self.robot_x, self.robot_y,
                next_opening[0], next_opening[1]
            )
            
            if self.current_path is None:
                self.get_logger().warn(f"Geen pad naar opening ({next_opening[0]:.2f}, {next_opening[1]:.2f})")
                self.visited_openings.add(next_opening)
                return
            
            self.current_path_idx = 0
            self.get_logger().info(f"Pad berekend naar opening. Lengte: {len(self.current_path)}")
            return
        
        # Volg huidig pad
        target = self.current_path[self.current_path_idx]
        
        dx = target[0] - self.robot_x
        dy = target[1] - self.robot_y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist < 0.3:
            self.current_path_idx += 1
            if self.current_path_idx >= len(self.current_path):
                self.current_path = None
            return
        
        # Stuur beweging
        cmd = Twist()
        
        angle_to_target = math.atan2(dy, dx)
        angle_error = angle_to_target - self.robot_yaw
        
        while angle_error > math.pi:
            angle_error -= 2 * math.pi
        while angle_error < -math.pi:
            angle_error += 2 * math.pi
        
        if abs(angle_error) > 0.3:
            cmd.angular.z = max(-1.0, min(1.0, angle_error))
            cmd.linear.x = 0.1
        else:
            cmd.linear.x = min(0.5, 0.3 * dist)
            cmd.angular.z = max(-0.8, min(0.8, 0.5 * angle_error))
        
        self.cmd_pub.publish(cmd)


def main():
    rclpy.init()
    node = RoomDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()