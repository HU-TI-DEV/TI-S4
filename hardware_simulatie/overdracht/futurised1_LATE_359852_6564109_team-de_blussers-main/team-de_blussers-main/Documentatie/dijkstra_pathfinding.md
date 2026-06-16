# Dijkstra Pathfinding - Tonk (Waterblus Robot)

## Overzicht

De `dijkstra_path_planner` node zorgt voor autonome navigatie van de Tonk. Hij bouwt automatisch een kaart op uit de LiDAR-sensor, vindt het kortste pad naar een opgegeven doel en stuurt de robot via de DiffDrive controller.

```
LiDAR (/lidar/pointcloud)
        │
        ▼
┌───────────────────┐
│  Occupancy Grid   │  ← 2D kaart: vrij (wit) / bezet (zwart)
│  (200×120 cellen) │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Dijkstra zoeker  │  ← vindt kortste pad van robot naar doel
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Pad volger       │  ← stuurt de robot langs de waypoints
│  (P-regelaar)     │
└────────┬──────────┘
         │
         ▼
    /cmd_vel (Twist)
```

---

## Stap 1 - Occupancy Grid bouwen

### Wat is een occupancy grid?

Een occupancy grid is een 2D raster van cellen. Elke cel heeft één van twee waarden:

| Waarde | Betekenis |
|--------|-----------|
| `0`    | Vrij - de robot kan hier rijden |
| `100`  | Bezet - hier zit een muur, auto of pilaar |

### Hoe worden de LiDAR-punten omgezet?

De LiDAR staat op de robot en meet afstanden in alle richtingen. Elke meting is een (x, y, z) punt in het **sensor-frame** (relatief aan de robot).

Om die punten op de kaart te plaatsen, moeten we ze vertalen naar het **odom-frame** (de vaste wereld). Dit doen we met de bekende robotpositie uit de odometrie:

```
wx = cos(yaw) × lx − sin(yaw) × ly + robot_x
wy = sin(yaw) × lx + cos(yaw) × ly + robot_y
```

Daarna berekenen we in welke gridcel het punt valt:

```
col = (wx − grid_origin_x) / resolutie
row = (wy − grid_origin_y) / resolutie
```

### Obstakel-inflatie

De robot is **1.6 m breed**. Als we de obstakels niet vergroten, kan het pad berekend worden langs een muur die de robot nooit kan passeren.

Daarom inflateren we elk obstakel met **1.0 m** in alle richtingen. Zo rijdt het pad altijd veilig langs obstakels.

```
Zonder inflatie:        Met inflatie (1 m):

  ##                      ████
  ##    ←── pad            ████████
  ##                      ████
```

### Gridparameters

| Parameter | Waarde | Toelichting |
|-----------|--------|-------------|
| Resolutie | 0.2 m/cel | Nauwkeurigheid van de kaart |
| Breedte | 200 cellen | 40 m horizontaal |
| Hoogte | 120 cellen | 24 m verticaal |
| Oorsprong | (−20, −12) | Linksonder in odom-frame |
| Inflatieradius | 1.0 m | Veiligheidszone rond obstakels |

---

## Stap 2 - Dijkstra pathfinding

### Wat doet Dijkstra?

Dijkstra's algoritme vindt het **goedkoopste pad** in een gewogen graaf. In ons geval is de graaf het occupancy grid: elke vrije cel is een knoop, en de kost is de afstand tussen buren.

### Hoe werkt het in de code?

We gebruiken een **priority queue** (min-heap): de cel met de laagste totale kost van de start wordt altijd als eerste verwerkt.

```
┌──────────────────────────────────────────────────────┐
│ INITIALISATIE                                        │
│   dist[start] = 0                                    │
│   dist[alle andere cellen] = ∞                       │
│   queue = [(0, start)]                               │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│ HERHALING (totdat queue leeg is of doel bereikt)     │
│                                                      │
│  1. Pak cel met laagste kost uit de queue            │
│  2. Stop als dit de doelcel is ✓                     │
│  3. Bekijk alle 8 buren:                             │
│     • Is de buur bezet? → sla over                  │
│     • Is nieuwe kost lager? → update en voeg toe     │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│ PAD TRACEREN (via prev-array)                        │
│   Volg prev[] van doel terug naar start              │
│   Draai de lijst om → pad van start naar doel        │
└──────────────────────────────────────────────────────┘
```

### Acht-verbondenheid

We gaan van elke cel naar 8 buren (ook diagonaal). Diagonale stappen kosten √2 × resolutie, rechte stappen kosten 1 × resolutie:

```
  ↖ ↑ ↗
  ← · →      · = huidige cel
  ↙ ↓ ↘      kosten: √2, 1, √2, 1, 1, √2, 1, √2
```

### Voorbeeld pad in het grid

```
Start(S) naar Doel(D) met muur(██):

  · · · · · · · ·
  · S · · █ · · ·
  · · · · █ · D ·
  · · · · █ · · ·
  · · · · · · · ·

Dijkstra pad (●):

  · · · · · · · ·
  · S ● · █ · · ·
  · · · ● █ ● D ·
  · · · · █ · · ·
  · · · · · · · ·
```

Het pad buigt om de muur heen via de kortste route.

---

## Stap 3 - Pad volgen (regelaar)

### Proportionele richting-regelaar

De robot volgt de waypoints één voor één. Voor elk waypoint berekenen we:

1. **Hoekfout** = gewenste richting − huidige richting (robot yaw)
2. **Stuurcommando** = `KP_ANGULAR × hoekfout`
3. **Rijsnelheid** = `MAX_LINEAR × cos(hoekfout)`

De cosinus-factor zorgt dat de robot langzamer rijdt bij grote hoekfouten:

```
Hoekfout = 0°   → cos(0) = 1.0  → volle snelheid vooruit
Hoekfout = 45°  → cos(45°) ≈ 0.7 → 70% snelheid
Hoekfout = 90°  → cos(90°) = 0   → alleen draaien, niet rijden
```

### Waypoint switching

De robot gaat naar het volgende waypoint zodra hij binnen **0.4 m** is van het huidige. Het doel wordt als bereikt beschouwd binnen **0.5 m**.

### Parameters

| Parameter | Waarde | Toelichting |
|-----------|--------|-------------|
| `KP_ANGULAR` | 2.0 | Hoe snel bijsturen (hoger = agressiever) |
| `MAX_LINEAR` | 1.0 m/s | Maximale rijsnelheid |
| `MAX_ANGULAR` | 2.0 rad/s | Maximale draaisnelheid |
| `WAYPOINT_TOL` | 0.4 m | Afstand voor waypoint-wissel |
| `GOAL_TOL` | 0.5 m | Afstand voor "doel bereikt" |

---

## Topics

### Subscribers (input)

| Topic | Type | Beschrijving |
|-------|------|-------------|
| `/lidar/pointcloud` | `sensor_msgs/PointCloud2` | Gefilterde LiDAR punten (robot-relatief) |
| `/odom` | `nav_msgs/Odometry` | Robotpositie en -oriëntatie |
| `/goal_pose` | `geometry_msgs/PoseStamped` | Doellocatie (uit RViz of code) |

### Publishers (output)

| Topic | Type | Beschrijving |
|-------|------|-------------|
| `/cmd_vel` | `geometry_msgs/Twist` | Rijcommando's naar DiffDrive |
| `/map` | `nav_msgs/OccupancyGrid` | Gebouwde occupancy grid (voor RViz) |
| `/path` | `nav_msgs/Path` | Geplande route (voor RViz) |

---

## Gebruik

### Opstarten

```bash
cd ros2
colcon build --packages-select tonk_mapping
source install/setup.bash
ros2 launch tonk_mapping mapping.launch.py
```

### Doel instellen via RViz

1. Open RViz (start automatisch mee met de launch)
2. Klik op de **"2D Nav Goal"** / **SetGoal** knop in de toolbar (pijl-icoon)
3. Klik in het 3D venster op de gewenste bestemming
4. De robot begint automatisch te rijden

### Doel instellen via terminal

```bash
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped \
  "{header: {frame_id: 'map'}, pose: {position: {x: 5.0, y: 3.0, z: 0.0}, orientation: {w: 1.0}}}"
```

### Debuggen

```bash
# Bekijk de bezette cellen in de kaart
ros2 topic echo /map --no-arr | grep -E "width|height|resolution"

# Bekijk de waypoints
ros2 topic echo /path

# Bekijk de rijcommando's
ros2 topic echo /cmd_vel

# Stop de robot direct
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}"
```

---

## Architectuur in de ROS2-graaf

```
Gazebo (parking_garage.world)
  │
  ├── /lidar/points ──→ [ros_gz_bridge] ──→ [lidar_to_pointcloud]
  │                                                  │
  │                                          /lidar/pointcloud
  │                                                  │
  ├── /odom ──→ [ros_gz_bridge] ──→ /odom ──→ [dijkstra_path_planner]
  │                                    │              │
  │                            [imu_odometry]  /cmd_vel ──→ [ros_gz_bridge] ──→ Gazebo
  │                                           /map ──→ RViz
  │                                           /path ──→ RViz
  └── /imu ──→ [ros_gz_bridge] ──→ [imu_odometry]
```

---

## Bekende beperkingen

| Beperking | Uitleg | Mogelijke verbetering |
|-----------|--------|-----------------------|
| Geen SLAM | De `odom` frame heeft drift bij lange ritten | Integreer `slam_toolbox` |
| Statische kaart per scan | De kaart wordt elke scan opnieuw gebouwd, geen geheugen | Voeg een rolling window toe |
| Geen dynamische obstakels | Bewegende objecten worden niet apart behandeld | Gebruik een kostmap met decay |
| Vereenvoudigde TF | LiDAR frame is robot-relatief maar statisch gelabeld | Gebruik echte TF-chain via `robot_state_publisher` |
| Geen herstelgedrag | Bij blokkade stopt de robot | Voeg rotatiegedrag toe als pad mislukt |

---

## Bronbestanden

| Bestand | Beschrijving |
|---------|-------------|
| `ros2/tonk_mapping/src/dijkstra_path_planner.cc` | Hoofdimplementatie |
| `ros2/tonk_mapping/CMakeLists.txt` | Bouwconfiguratie |
| `ros2/tonk_mapping/launch/mapping.launch.py` | Lanceerscript |
| `ros2/tonk_mapping/rviz/mapping.rviz` | RViz visualisatie-instellingen |
