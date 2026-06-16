#!/usr/bin/env python3
"""
A* navigator voor de Flip-robot.
=================================
- Bouwt een opgeblazen costmap uit de SLAM /map (obstakels verbreed met de
  robotstraal, plus een zachte kostengradiënt zodat de robot het midden van
  doorgangen kiest).
- Plant met A* (eigen binaire min-heap) een pad door bekende vrije ruimte.
- Kiest automatisch het dichtstbijzijnde frontier = opening naar onontdekt
  gebied (= deuropening naar de volgende kamer). Je kunt ook handmatig een
  doel klikken in RViz met de "2D Nav Goal" knop.
- Publiceert het pad als nav_msgs/Path op /planned_path → zichtbaar als lijn
  in RViz.
- Volgt het pad met pure pursuit en wijkt uit voor obstakels via de lidar.

NIEUW: Deurcheck + middenrijden
  Wanneer de robot een frontier-doel nadert (binnen DOOR_CHECK_DIST), meet hij
  via de LIDAR:
    1. Hoe breed de opening is → te smal? Blacklist + kies ander doel.
    2. Waar precies het midden van de opening zit → robot rijdt altijd door
       het midden, niet scheef langs een deurstijl.
"""

import rclpy
from rclpy.node import Node
from rclpy.time import Time
import numpy as np
import math
import time
from collections import deque

from nav_msgs.msg import OccupancyGrid, Odometry, Path
from geometry_msgs.msg import PoseStamped, Twist
from sensor_msgs.msg import LaserScan
from tf2_ros import Buffer, TransformListener


# ─── Robot- en planningsparameters ──────────────────────────────────────────────
ROBOT_RADIUS    = 0.40   # m — lethal inflatie (hard geblokkeerd binnen deze straal)
SOFT_RADIUS     = 1.2    # m — zachte kostenzone buiten de lethal ring.
                         #     Groter = robot houdt meer afstand van muren.
                         #     In smalle gangen overlappen de zones van beide wanden,
                         #     wat de robot automatisch naar het midden duwt.
SOFT_WEIGHT     = 12.0   # kostenmultiplier in de zachte zone (hoger = meer omrijden).
                         #     Samen met SOFT_RADIUS bepaalt dit hoe ver de planner
                         #     omgaat om muren te vermijden.
UNKNOWN_PENALTY = 2.0    # kostenstraf voor rijden door onverkend gebied

GOAL_TOL        = 0.5    # m — doel bereikt binnen deze afstand
LOOKAHEAD       = 1.0    # m — pure-pursuit vooruitkijkafstand
MAX_SPEED       = 0.65   # m/s
LIDAR_SAFE      = 0.5    # m — noodstop als obstakel dichterbij dan dit
ASTAR_MAX_ITER  = 120000 # veiligheidslimiet op A*-expansies

# ─── Deurcheck-parameters ────────────────────────────────────────────────────────
ROBOT_WIDTH     = 0.85   # m — robotbreedte (0.75m) + 0.10m veiligheidsmarge
DOOR_CHECK_DIST = 1.5    # m — afstand tot frontier waarop gemeten wordt


# ─── Binaire min-heap priority queue ────────────────────────────────────────────
class MinHeap:
    def __init__(self):
        self.items = []

    def __len__(self):
        return len(self.items)

    def push(self, priority, value):
        self.items.append((priority, value))
        self._sift_up(len(self.items) - 1)

    def pop(self):
        top = self.items[0]
        last = self.items.pop()
        if self.items:
            self.items[0] = last
            self._sift_down(0)
        return top

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self.items[i][0] < self.items[parent][0]:
                self.items[i], self.items[parent] = self.items[parent], self.items[i]
                i = parent
            else:
                break

    def _sift_down(self, i):
        n = len(self.items)
        while True:
            smallest = i
            l, r = 2 * i + 1, 2 * i + 2
            if l < n and self.items[l][0] < self.items[smallest][0]:
                smallest = l
            if r < n and self.items[r][0] < self.items[smallest][0]:
                smallest = r
            if smallest == i:
                break
            self.items[i], self.items[smallest] = self.items[smallest], self.items[i]
            i = smallest


# ─── Costmap ────────────────────────────────────────────────────────────────────
class Costmap:
    def __init__(self, grid_msg):
        self.res      = grid_msg.info.resolution
        self.origin_x = grid_msg.info.origin.position.x
        self.origin_y = grid_msg.info.origin.position.y
        self.h        = grid_msg.info.height
        self.w        = grid_msg.info.width

        raw = np.array(grid_msg.data, dtype=np.int8).reshape((self.h, self.w))

        occ     = raw > 50
        unknown = raw == -1

        lethal_cells = max(1, int(round(ROBOT_RADIUS / self.res)))
        soft_cells   = max(1, int(round(SOFT_RADIUS  / self.res)))

        lethal = occ.copy()
        for _ in range(lethal_cells):
            lethal = self._dilate(lethal)

        cost = np.zeros((self.h, self.w), dtype=np.float32)
        ring = lethal.copy()
        for k in range(soft_cells):
            nxt = self._dilate(ring)
            new_cells = nxt & ~ring
            cost[new_cells] = (soft_cells - k) / soft_cells
            ring = nxt

        self.traversable = ~lethal
        cost[unknown & self.traversable] += UNKNOWN_PENALTY
        self.cost = cost

    @staticmethod
    def _dilate(mask):
        out = mask.copy()
        out[1:,  :] |= mask[:-1, :]
        out[:-1, :] |= mask[1:,  :]
        out[:,  1:] |= mask[:, :-1]
        out[:, :-1] |= mask[:, 1:]
        return out

    def world_to_grid(self, wx, wy):
        return int((wx - self.origin_x) / self.res), \
               int((wy - self.origin_y) / self.res)

    def grid_to_world(self, gx, gy):
        return self.origin_x + (gx + 0.5) * self.res, \
               self.origin_y + (gy + 0.5) * self.res

    def in_bounds(self, gx, gy):
        return 0 <= gx < self.w and 0 <= gy < self.h

    def is_free(self, gx, gy):
        return self.in_bounds(gx, gy) and self.traversable[gy, gx]

    def snap_to_free(self, gx, gy, radius=30):
        gx = max(0, min(self.w - 1, gx))
        gy = max(0, min(self.h - 1, gy))
        if self.is_free(gx, gy):
            return gx, gy
        best, best_d = None, None
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = gx + dx, gy + dy
                if self.is_free(nx, ny):
                    d = dx * dx + dy * dy
                    if best_d is None or d < best_d:
                        best_d, best = d, (nx, ny)
        return best


# ─── A* ─────────────────────────────────────────────────────────────────────────
def astar(cm: Costmap, start_world, goal_world):
    start = cm.world_to_grid(*start_world)
    goal  = cm.world_to_grid(*goal_world)

    snapped_start = cm.snap_to_free(*start)
    snapped_goal  = cm.snap_to_free(*goal)
    if snapped_start is None or snapped_goal is None:
        return None
    sx, sy = snapped_start
    gx, gy = snapped_goal

    neighbors = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
                 (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]

    def heuristic(x, y):
        return math.hypot(x - gx, y - gy)

    open_heap = MinHeap()
    open_heap.push(0.0, (sx, sy))
    came_from = {}
    g_score = {(sx, sy): 0.0}
    closed = set()

    iters = 0
    while len(open_heap) and iters < ASTAR_MAX_ITER:
        iters += 1
        _, (x, y) = open_heap.pop()

        if (x, y) == (gx, gy):
            cells = [(x, y)]
            while (x, y) in came_from:
                x, y = came_from[(x, y)]
                cells.append((x, y))
            cells.reverse()
            return [cm.grid_to_world(cx, cy) for cx, cy in cells]

        if (x, y) in closed:
            continue
        closed.add((x, y))

        for dx, dy, step in neighbors:
            nx, ny = x + dx, y + dy
            if not cm.is_free(nx, ny) or (nx, ny) in closed:
                continue
            move = step * (1.0 + SOFT_WEIGHT * cm.cost[ny, nx])
            tentative = g_score[(x, y)] + move
            if tentative < g_score.get((nx, ny), float('inf')):
                g_score[(nx, ny)] = tentative
                came_from[(nx, ny)] = (x, y)
                f = tentative + heuristic(nx, ny)
                open_heap.push(f, (nx, ny))

    return None


def smooth_path(path, every=3):
    if path is None or len(path) <= 2:
        return path
    thinned = path[::every]
    if thinned[-1] != path[-1]:
        thinned.append(path[-1])
    return thinned


def quaternion_to_yaw(q):
    siny = 2.0 * (q.w * q.z + q.x * q.y)
    cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny, cosy)


# ─── Navigator node ─────────────────────────────────────────────────────────────
class AStarNavigator(Node):

    def __init__(self):
        super().__init__('astar_navigator')

        self.costmap   = None
        self.map_msg   = None
        self.scan      = None
        self.robot_x   = 0.0
        self.robot_y   = 0.0
        self.robot_yaw = 0.0
        self.odom_x    = 0.0
        self.odom_y    = 0.0
        self.odom_yaw  = 0.0
        self.odom_ok   = False

        self.tf_buffer   = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.goal        = None
        self.path        = None
        self.path_idx    = 0
        self.manual_goal = False
        self.fail_count  = 0

        self.avoiding    = False
        self.avoid_until = 0.0
        self.avoid_dir   = 1.0
        self.avoid_start = 0.0

        self.travel_yaw  = 0.0
        self.have_travel = False

        self.blacklist      = []
        self.last_move_time = time.time()
        self.last_move_x    = 0.0
        self.last_move_y    = 0.0

        # Bijhouden welke frontier-doelen al op deurbreed + midden gecheckt zijn
        self.door_checked = set()

        self.create_subscription(OccupancyGrid, '/map',       self.on_map,  10)
        self.create_subscription(Odometry,      '/odom',      self.on_odom, 10)
        self.create_subscription(LaserScan,     '/scan',      self.on_scan, 10)
        self.create_subscription(PoseStamped,   '/goal_pose', self.on_goal, 10)

        self.cmd_pub  = self.create_publisher(Twist, '/cmd_vel',      10)
        self.path_pub = self.create_publisher(Path,  '/planned_path', 10)

        self.create_timer(0.5, self.plan_loop)
        self.create_timer(0.1, self.drive_loop)

        self.get_logger().info(
            'A* navigator gestart. Kiest automatisch een opening, of klik een '
            'doel met de 2D Nav Goal knop in RViz.')

    # ── Callbacks ───────────────────────────────────────────────────────────────
    def on_map(self, msg):
        self.map_msg = msg

    def on_odom(self, msg):
        self.odom_ok  = True
        self.odom_x   = msg.pose.pose.position.x
        self.odom_y   = msg.pose.pose.position.y
        self.odom_yaw = quaternion_to_yaw(msg.pose.pose.orientation)

        tx, ty, tyaw = 0.0, 0.0, 0.0
        try:
            t = self.tf_buffer.lookup_transform('map', 'odom', Time())
            tx   = t.transform.translation.x
            ty   = t.transform.translation.y
            tyaw = quaternion_to_yaw(t.transform.rotation)
        except Exception:
            pass

        c, s = math.cos(tyaw), math.sin(tyaw)
        self.robot_x   = tx + c * self.odom_x - s * self.odom_y
        self.robot_y   = ty + s * self.odom_x + c * self.odom_y
        self.robot_yaw = tyaw + self.odom_yaw

        ddx = self.robot_x - self.last_move_x
        ddy = self.robot_y - self.last_move_y
        if math.hypot(ddx, ddy) > 0.2:
            self.travel_yaw  = math.atan2(ddy, ddx)
            self.have_travel = True
            self.last_move_time = time.time()
            self.last_move_x = self.robot_x
            self.last_move_y = self.robot_y

    def on_scan(self, msg):
        self.scan = msg

    def on_goal(self, msg):
        self.goal        = (msg.pose.position.x, msg.pose.position.y)
        self.manual_goal = True
        self.path        = None
        self.get_logger().info(
            f'Handmatig doel: ({self.goal[0]:.2f}, {self.goal[1]:.2f})')

    # ── Plannen (2 Hz) ──────────────────────────────────────────────────────────
    def plan_loop(self):
        if self.map_msg is None or not self.odom_ok:
            return

        self.costmap = Costmap(self.map_msg)

        if self.goal is not None:
            if math.hypot(self.goal[0] - self.robot_x,
                          self.goal[1] - self.robot_y) < GOAL_TOL:
                self.get_logger().info('Doel bereikt!')
                self.goal        = None
                self.path        = None
                self.manual_goal = False

        if self.goal is not None and not self.manual_goal:
            if time.time() - self.last_move_time > 8.0:
                self.get_logger().warn(
                    f'Vastgelopen bij ({self.goal[0]:.2f}, {self.goal[1]:.2f}) '
                    f'— op blacklist, kies nieuw doel.')
                self.blacklist.append(self.goal)
                if len(self.blacklist) > 20:
                    self.blacklist.pop(0)
                self.goal = None
                self.path = None
                self.last_move_time = time.time()

        if self.goal is None:
            frontier = self.find_frontier()
            if frontier is None:
                return
            self.goal = frontier
            self.get_logger().info(
                f'Nieuw frontier-doel: ({frontier[0]:.2f}, {frontier[1]:.2f})')

        path = astar(self.costmap, (self.robot_x, self.robot_y), self.goal)
        if path is None:
            self.fail_count += 1
            if not self.manual_goal or self.fail_count >= 4:
                self.get_logger().warn(
                    f'Geen A*-pad naar ({self.goal[0]:.2f}, {self.goal[1]:.2f}) '
                    f'— doel losgelaten.')
                self.goal = None
                self.manual_goal = False
                self.fail_count = 0
            self.path = None
            return

        self.fail_count = 0
        self.path     = smooth_path(path)
        self.path_idx = 0
        self.publish_path(self.path)

    # ── Frontier-detectie ────────────────────────────────────────────────────────
    def find_frontier(self):
        msg  = self.map_msg
        h, w = msg.info.height, msg.info.width
        res  = msg.info.resolution
        ox   = msg.info.origin.position.x
        oy   = msg.info.origin.position.y

        data    = np.array(msg.data, dtype=np.int8).reshape((h, w))
        free    = data == 0
        unknown = data == -1

        adj_unknown = (
            np.roll(unknown,  1, axis=0) | np.roll(unknown, -1, axis=0) |
            np.roll(unknown,  1, axis=1) | np.roll(unknown, -1, axis=1)
        )
        frontier = free & adj_unknown
        frontier &= self.costmap.traversable

        cm = self.costmap
        start = cm.snap_to_free(*cm.world_to_grid(self.robot_x, self.robot_y))
        if start is None:
            return None

        reachable = np.zeros_like(cm.traversable)
        dq = deque([start])
        reachable[start[1], start[0]] = True
        while dq:
            x, y = dq.popleft()
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if cm.is_free(nx, ny) and not reachable[ny, nx]:
                    reachable[ny, nx] = True
                    dq.append((nx, ny))

        frontier &= reachable
        if not np.any(frontier):
            return None

        labels = np.full(frontier.shape, -1, dtype=np.int32)
        clusters = []
        fset = frontier
        for (sr, sc) in map(tuple, np.argwhere(frontier)):
            if labels[sr, sc] != -1:
                continue
            cid = len(clusters)
            dq = deque([(sr, sc)])
            labels[sr, sc] = cid
            cells = []
            while dq:
                r, c = dq.popleft()
                cells.append((r, c))
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = r + dr, c + dc
                        if (0 <= nr < h and 0 <= nc < w and fset[nr, nc]
                                and labels[nr, nc] == -1):
                            labels[nr, nc] = cid
                            dq.append((nr, nc))
            arr = np.array(cells)
            clusters.append((len(cells), arr[:, 0].mean(), arr[:, 1].mean()))

        rr = (self.robot_y - oy) / res
        rc = (self.robot_x - ox) / res
        fwd_yaw = self.travel_yaw if self.have_travel else self.robot_yaw

        best_score, best_goal = None, None
        for size, mr, mc in clusters:
            if size < 3:
                continue
            dist_cells = math.hypot(mr - rr, mc - rc)
            if dist_cells < (0.8 / res):
                continue
            ang  = math.atan2(mr - rr, mc - rc)
            head = math.cos(ang - fwd_yaw)
            dist_m = dist_cells * res
            score = size * 0.5 - dist_m * 0.5 + head * 8.0
            if head < -0.2:
                score -= 10.0
            gx = ox + (mc + 0.5) * res
            gy = oy + (mr + 0.5) * res
            if any(math.hypot(gx - bx, gy - by) < 1.0 for bx, by in self.blacklist):
                continue
            if best_score is None or score > best_score:
                best_score, best_goal = score, (gx, gy)

        return best_goal

    # ── NIEUW: deuropening meten (breedte + midden) ──────────────────────────────
    def measure_opening(self):
        """
        Meet de breedte én het midden van de opening voor de robot via de LIDAR.

        Hoe het werkt:
          LIDAR-rays die door de opening gaan hebben bereik > 75% van de afstand
          tot het doel (ze 'zien' de kamer achter de deur). Rays die de deurstijl
          of muur raken hebben een kortere afstand.

          - Breedte: hoekspan van de open rays → fysieke breedte via
                     w = 2 · afstand · sin(span / 2)
          - Midden:  middelste hoek van de open rays → projecteer op de
                     doelafstand → wereldcoördinaten van het openingscentrum

          De 5e–95e percentiel van de hoeken filtert LIDAR-ruis aan de randen.

        Returns:
          (width_m, center_x, center_y)
            width_m          — breedte in meters
                               999.0 = meting niet mogelijk (sensor/hoek), ga door
                               0.0   = volledig geblokkeerd
            center_x/center_y — wereldcoördinaten van het midden (None als onbekend)
        """
        if self.scan is None or self.goal is None:
            return 999.0, None, None

        dist = math.hypot(self.goal[0] - self.robot_x,
                          self.goal[1] - self.robot_y)
        if dist < 0.1:
            return 999.0, None, None

        # Hoek van de robot naar het doel, relatief aan zijn eigen heading
        goal_bearing = math.atan2(self.goal[1] - self.robot_y,
                                  self.goal[0] - self.robot_x)
        rel = goal_bearing - self.robot_yaw
        while rel >  math.pi: rel -= 2 * math.pi
        while rel < -math.pi: rel += 2 * math.pi

        # Alleen meten als de robot redelijk recht op de deur staat;
        # een scheve meting geeft een te brede of te smalle schatting.
        if abs(rel) > math.radians(40):
            return 999.0, None, None

        ranges     = np.array(self.scan.ranges, dtype=np.float32)
        a_min      = self.scan.angle_min
        a_inc      = self.scan.angle_increment
        n          = len(ranges)
        max_r      = self.scan.range_max

        # Hoek van elke ray, relatief aan de richting naar de deur
        ray_angles = a_min + np.arange(n) * a_inc
        rel_angles = ray_angles - rel
        rel_angles = ((rel_angles + np.pi) % (2 * np.pi)) - np.pi  # -π … +π

        in_sector = np.abs(rel_angles) < math.radians(70)   # alleen ±70° rondom de deur
        threshold = dist * 0.75                              # "door opening" drempel
        open_mask = in_sector & (ranges > threshold) & np.isfinite(ranges)

        if not np.any(open_mask):
            return 0.0, None, None   # volledig geblokkeerd

        open_angles = rel_angles[open_mask]

        # Percentiel-filter: negeer de ruis-uitschieters aan de randen
        p5  = float(np.percentile(open_angles,  5))
        p95 = float(np.percentile(open_angles, 95))

        span  = p95 - p5
        width = 2.0 * dist * math.sin(span / 2.0)

        # ── Midden van de opening ──────────────────────────────────────────────
        # De middelste hoek van de open zone geeft de richting naar het centrum.
        # center_rel is de laterale afwijking t.o.v. de richting naar het doel:
        #   0.0  → de robot rijdt al perfect op het midden af
        #   > 0  → opening ligt iets naar links
        #   < 0  → opening ligt iets naar rechts
        center_rel = (p5 + p95) / 2.0

        # Absolute richting van het midden in de wereld
        center_bearing = self.robot_yaw + rel + center_rel

        # Wereldcoördinaten van het openingscentrum (op de deuropeningsafstand)
        center_x = self.robot_x + dist * math.cos(center_bearing)
        center_y = self.robot_y + dist * math.sin(center_bearing)

        return float(width), center_x, center_y

    # ── Pad publiceren voor RViz ────────────────────────────────────────────────
    def publish_path(self, path):
        msg = Path()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()
        for wx, wy in path:
            ps = PoseStamped()
            ps.header = msg.header
            ps.pose.position.x = wx
            ps.pose.position.y = wy
            ps.pose.orientation.w = 1.0
            msg.poses.append(ps)
        self.path_pub.publish(msg)

    # ── Lidar-obstakelinfo ──────────────────────────────────────────────────────
    def obstacle_info(self):
        if self.scan is None:
            return True, 10.0, 10.0, 10.0
        ranges = np.array(self.scan.ranges, dtype=np.float32)
        a_min  = self.scan.angle_min
        a_inc  = self.scan.angle_increment
        n      = len(ranges)
        max_r  = self.scan.range_max
        ranges = np.where(np.isfinite(ranges), ranges, max_r)

        def sector(lo, hi):
            i0 = max(0, min(n - 1, int((math.radians(lo) - a_min) / a_inc)))
            i1 = max(0, min(n - 1, int((math.radians(hi) - a_min) / a_inc)))
            if i0 > i1:
                i0, i1 = i1, i0
            s = ranges[i0:i1 + 1]
            return float(np.min(s)) if len(s) else max_r

        front = sector(-50, 50)
        left  = sector(50, 110)
        right = sector(-110, -50)
        return front > LIDAR_SAFE, front, left, right

    # ── Rijden (10 Hz) ──────────────────────────────────────────────────────────
    def drive_loop(self):
        if not self.odom_ok or self.goal is None:
            return

        front_ok, front_d, left_d, right_d = self.obstacle_info()
        cmd = Twist()
        now = time.time()

        # Noodvermijding
        if not front_ok and not self.avoiding:
            self.avoiding    = True
            self.avoid_dir   = -1.0 if right_d > left_d else 1.0
            self.avoid_start = now
            self.avoid_until = now + 3.0

        if self.avoiding:
            cleared = front_ok and (now - self.avoid_start) > 0.4
            if cleared or now > self.avoid_until:
                self.avoiding = False
                self.path = None
                return
            cmd.angular.z = self.avoid_dir * 1.0
            cmd.linear.x  = 0.0
            self.cmd_pub.publish(cmd)
            return

        # Doel bereikt?
        if math.hypot(self.goal[0] - self.robot_x,
                      self.goal[1] - self.robot_y) < GOAL_TOL:
            self.cmd_pub.publish(Twist())
            return

        if not self.path:
            return

        # ── DEURCHECK: breedte meten + route via het midden ──────────────────────
        # Alleen voor automatisch gekozen frontier-doelen, niet voor handmatige
        # RViz-doelen. De check gebeurt één keer per doel (door_checked).
        if not self.manual_goal and self.goal not in self.door_checked:
            dist_to_goal = math.hypot(self.goal[0] - self.robot_x,
                                      self.goal[1] - self.robot_y)
            if dist_to_goal <= DOOR_CHECK_DIST:
                width, door_cx, door_cy = self.measure_opening()
                self.door_checked.add(self.goal)   # sla nooit twee keer op

                if width < ROBOT_WIDTH:
                    # ── Te smal: doel overslaan ───────────────────────────────
                    self.get_logger().warn(
                        f'Opening ({self.goal[0]:.2f}, {self.goal[1]:.2f}) '
                        f'te smal: {width:.2f}m (min. {ROBOT_WIDTH}m) — overgeslagen.')
                    self.blacklist.append(self.goal)
                    if len(self.blacklist) > 20:
                        self.blacklist.pop(0)
                    self.goal = None
                    self.path = None
                    self.cmd_pub.publish(Twist())   # kort stoppen
                    return

                else:
                    # ── Breed genoeg: route via het MIDDEN sturen ─────────────
                    self.get_logger().info(
                        f'Opening ({self.goal[0]:.2f}, {self.goal[1]:.2f}) '
                        f'breed genoeg: {width:.2f}m — rijdt via het midden.')

                    if door_cx is not None:
                        # Voeg het gemeten openingscentrum in als eerste waypoint
                        # zodat de robot niet scheef door de deur rijdt maar
                        # precies door het midden gaat.
                        #
                        # Pad wordt:  [door_midden] + [rest van het originele pad]
                        # De pure-pursuit volgt dit en stuurt de robot naar het
                        # midden voordat hij verder rijdt naar het frontier-doel.
                        remaining = self.path[self.path_idx:]
                        self.path = [(door_cx, door_cy)] + remaining
                        self.path_idx = 0
                        self.publish_path(self.path)   # zichtbaar in RViz
                        self.get_logger().info(
                            f'   → deuropening midden: '
                            f'({door_cx:.2f}, {door_cy:.2f})')
        # ── EINDE DEURCHECK ──────────────────────────────────────────────────────

        # Al gepasseerde waypoints overslaan
        while self.path_idx < len(self.path) - 1:
            wx, wy = self.path[self.path_idx]
            if math.hypot(wx - self.robot_x, wy - self.robot_y) < 0.3:
                self.path_idx += 1
            else:
                break

        # Pure pursuit: mik op een punt ~LOOKAHEAD meter vooruit op het pad
        target = self.path[self.path_idx]
        for i in range(self.path_idx, len(self.path)):
            wx, wy = self.path[i]
            if math.hypot(wx - self.robot_x, wy - self.robot_y) >= LOOKAHEAD:
                target = (wx, wy)
                break

        angle_err = math.atan2(target[1] - self.robot_y,
                               target[0] - self.robot_x) - self.robot_yaw
        while angle_err >  math.pi: angle_err -= 2 * math.pi
        while angle_err < -math.pi: angle_err += 2 * math.pi

        scale = max(0.3, min(1.0, (front_d - LIDAR_SAFE) / 0.7))

        if abs(angle_err) > 0.7:
            cmd.angular.z = max(-1.5, min(1.5, 2.0 * angle_err))
            cmd.linear.x  = 0.0
        else:
            cmd.linear.x  = MAX_SPEED * scale
            cmd.angular.z = max(-1.2, min(1.2, 1.2 * angle_err))

        self.cmd_pub.publish(cmd)


def main():
    rclpy.init()
    node = AStarNavigator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()