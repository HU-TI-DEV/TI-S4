# Autonome Navigatie - Tonk Waterblus Robot

## Inhoudsopgave
1. [Systeemoverzicht](#systeemoverzicht)
2. [Hoe de robot rijdt - Dijkstra pathfinding](#dijkstra)
3. [Hoe de robot vuur vindt - Fire Navigator](#fire-navigator)
4. [De twee systemen samenwerken](#samenwerking)
5. [Topics overzicht](#topics)
6. [Opstarten](#opstarten)

---

## Systeemoverzicht <a name="systeemoverzicht"></a>

De Tonk heeft twee ROS2 nodes die samenwerken voor autonome navigatie:

```
┌─────────────────────────────────────────────────────────────────┐
│                        SENSOREN                                 │
│                                                                 │
│  Thermische camera      LiDAR (360°)        Odometrie (wielen) │
│  /thermal_camera_8bit   /lidar/pointcloud   /odom              │
│         │                    │   │               │              │
└─────────┼────────────────────┼───┼───────────────┼──────────────┘
          │                    │   │               │
          ▼                    ▼   │               ▼
  ┌───────────────┐    ┌───────────────────────────────┐
  │ fire_navigator│    │    dijkstra_path_planner       │
  │               │    │                               │
  │ 1. Detecteer  │    │ 1. Bouw occupancy grid         │
  │    vuur in    │    │    (kaart met obstakels)       │
  │    camerabeeld│    │                               │
  │               │    │ 2. Zoek kortste pad            │
  │ 2. Bereken    │    │    (Dijkstra algoritme)        │
  │    vuurpositie│    │                               │
  │    in de wereld    │ 3. Volg het pad                │
  │               │    │    (P-regelaar)               │
  │ 3. Stuur doel │───▶│                               │
  │    op 2m voor │    │                               │
  │    het vuur   │    └──────────────┬────────────────┘
  └───────────────┘                   │
                                      ▼
                               /cmd_vel (Twist)
                                      │
                                      ▼
                            DiffDrive controller
                            (4 wielen, skid steer)
```

---

## Hoe de robot rijdt - Dijkstra pathfinding <a name="dijkstra"></a>

### Stap 1 - De kaart bouwen (Occupancy Grid)

Bij elke LiDAR-scan bouwt de robot een 2D kaart van zijn omgeving.

**Wat is een occupancy grid?**  
Een raster van 450×300 cellen, elke cel is 20×20 cm groot (totaal 90×60 meter).  
Elke cel heeft een waarde:

| Waarde | Betekenis |
|--------|-----------|
| `0` | Vrij - de robot kan hier rijden |
| `5-90` | Gevaarlijk - dicht bij een obstakel (hogere kost) |
| `100` | Bezet - muur, auto of pilaar |

**Hoe worden LiDAR-punten op de kaart gezet?**

De LiDAR geeft punten terug in het *robot-frame* (relatief aan de robot zelf). Om ze op de wereldkaart te plaatsen, gebruikt de robot zijn eigen positie uit de odometrie:

```
wx = cos(yaw) × lx − sin(yaw) × ly + robot_x
wy = sin(yaw) × lx + cos(yaw) × ly + robot_y
```

Elke punt wordt daarna omgezet naar een gridcel en als bezet gemarkeerd.

**Obstakel-inflatie**

De robot is 1,6 m breed. Als we alleen de exacte obstakelpunten markeren, zou het berekende pad te dicht langs muren lopen. Daarom worden obstakels vergroot:

- **Harde zone** (0-1,0 m van obstakel): cel waarde 100 → **onpasseerbaar**
- **Zachte zone** (1,0-1,6 m van obstakel): cel waarde 90→5 → **passeerbaar maar duur**

```
Obstakel:  ████
Hard:      ████████████   (1,0 m, onpasseerbaar)
Zacht:     ░░░░████████████  (nog eens 0,6 m, duurder maar rijdbaar)
```

In RViz is de gradient zichtbaar als kleuroverloop in de costmap.

---

### Stap 2 - Het kortste pad zoeken (Dijkstra)

Dijkstra's algoritme zoekt het **goedkoopste pad** van de huidige robotpositie naar het doel.

**Hoe werkt het?**

1. Start bij de cel waar de robot staat. Kost = 0.
2. Bekijk alle 8 buren (ook diagonaal). Diagonale stap kost √2 × 0,2 m ≈ 0,28 m. Rechte stap kost 0,2 m.
3. Voeg ook de *celkost* toe: cellen dicht bij obstakels kosten extra.
4. Sla het goedkoopste pad op en ga door totdat het doel bereikt is.
5. Traceer het pad terug via de `prev[]`-array.

```
Voorbeeld: Start (S) naar Doel (D), muur (█)

  · · · · · · · ·
  · S · · █ · · ·     Dijkstra vindt:
  · · · · █ · D ·
  · · · · █ · · ·     S → · → · → · → · → D
  · · · · · · · ·          (pad buigt om de muur)
```

**Waarom geen A\*?**  
Dijkstra werkt prima voor deze ruimte (parking garage ≈ 32×18 m). A* zou sneller zijn voor grote open omgevingen, maar voor dit project is het verschil verwaarloosbaar.

---

### Stap 3 - Het pad volgen (P-regelaar)

De regelloop draait op **20 Hz** en volgt de waypoints één voor één.

**Hoe stuurt de robot?**

```
1. Bereken hoekfout:
   target_yaw = atan2(waypoint_y − robot_y, waypoint_x − robot_x)
   yaw_error  = target_yaw − robot_yaw   (genormaliseerd naar [−π, π])

2. Stuurcommando:
   angular.z = 2.0 × yaw_error        (hoe groter de fout, hoe harder bijsturen)

3. Rijsnelheid (daalt bij scherpe bochten):
   linear.x  = 1.0 × cos(yaw_error)   (bij 90° hoekfout: alleen draaien, niet rijden)
```

De robot schakelt naar het volgende waypoint zodra hij binnen **0,4 m** is. Het doel wordt als bereikt beschouwd bij **0,5 m**.

---

## Hoe de robot vuur vindt - Fire Navigator <a name="fire-navigator"></a>

De `fire_navigator` node combineert twee sensoren om de positie van het vuur in de wereld te berekenen.

### Stap 1 - Vuur detecteren in de camera

De thermische camera (320×240 pixels, 60° FOV, 30 Hz) geeft een 8-bit grijswaardebeeld terug. Elke pixel stelt een temperatuur voor:

```
pixel 0   → −20°C (253 K)   ← kouds
pixel 255 → 400°C (673 K)   ← max (alles heter verzadigt ook naar 255)

Drempel: pixel > 180 → temperatuur > ~276°C → VUUR
```

De node berekent het **gewogen zwaartepunt** van alle hete pixels. Hetere pixels trekken het zwaartepunt sterker naar zich toe:

```
gewicht  = pixelwaarde − 180      (heter = zwaarder)
cx       = Σ(pixel_x × gewicht) / Σ(gewicht)
```

### Stap 2 - Hoek naar het vuur berekenen

Uit de x-positie van het vuurcentrum in het camerabeeld berekent de node de hoek:

```
           pixel_x=0              pixel_x=319
           (links)   [==CAMERA==]  (rechts)
                          ↑
                     pixel_x=160 = recht vooruit (hoek = 0)

bearing_offset = (160 − cx) / 320 × 1,047 rad

Voorbeeld: cx=80 (links van midden) → bearing_offset = +0,33 rad (+19°)
           De robot moet 19° naar links kijken om het vuur te zien.
```

### Stap 3 - Afstand meten via LiDAR

De thermische camera geeft alleen een **hoek**, geen afstand. De LiDAR geeft wel afstand maar geen temperatuur. Door ze te combineren krijgen we een complete vuurpositie:

```
Zoek in de LiDAR-scan het dichtstbijzijnde punt
binnen ±8,6° van bearing_offset.
Dit is de afstand tot het brandende object.
```

De LiDAR ziet de brandende auto als een fysiek obstakel (het heeft botsingsgeometrie), dus er komen altijd punten terug in die richting.

### Stap 4 - Vuurpositie in de wereld berekenen

```
fire_bearing = robot_yaw + bearing_offset

fire_x = robot_x + afstand × cos(fire_bearing)
fire_y = robot_y + afstand × sin(fire_bearing)
```

### Stap 5 - Doel instellen op 2 meter voor het vuur

```
goal_x = fire_x − 2,0 × cos(fire_bearing)
goal_y = fire_y − 2,0 × sin(fire_bearing)
```

Dit punt ligt precies op de lijn tussen de robot en het vuur, op 2 meter van het vuur. De robot eindigt dus **recht voor** het vuur, op de juiste afstand.

```
[Robot] ──────────────────── [Doel] ── 2m ── [VUUR]
         Dijkstra rijdt hier          robot stopt hier
```

Het doel wordt gepubliceerd op `/goal_pose` → de `dijkstra_path_planner` pakt dit op en rijdt ernaartoe.

### Anti-spam mechanisme

Om te voorkomen dat de planner voortdurend herstart:
- Nieuw doel wordt alleen gestuurd als de vuurpositie **meer dan 0,5 m** verschoven is
- Als de robot al **binnen 2,4 m** van het vuur is, wordt er geen nieuw doel gestuurd

---

## De twee systemen samenwerken <a name="samenwerking"></a>

```
Tijdlijn van een typische run:

t=0s    Robot spawnt in de garage, LiDAR en camera starten op

t=1s    fire_navigator ziet vuur in camerabeeld
        → berekent vuurpositie (~13m, 7m) in wereld
        → publiceert doel op (11m, 6m) via /goal_pose

t=1s    dijkstra_path_planner ontvangt doel
        → bouwt occupancy grid uit LiDAR
        → zoekt pad (142 waypoints, ~28m)
        → begint rijden

t=30s   Robot is onderweg, LiDAR-kaart wordt elke scan vernieuwd
        → pad wordt bijgewerkt als nieuwe obstakels zichtbaar worden
        → fire_navigator stuurt geen nieuw doel (positie onveranderd)

t=55s   Robot bereikt doel (2m voor brandende auto)
        → dijkstra_path_planner: "Doel bereikt!"
        → fire_navigator: "Al op positie, wachten..."
        → robot staat stil, recht voor het vuur
```

---

## Topics overzicht <a name="topics"></a>

### fire_navigator

| Topic | Richting | Type | Inhoud |
|-------|----------|------|--------|
| `/thermal_camera_8bit/image` | ← subscribe | `sensor_msgs/Image` | 8-bit thermisch camerabeeld |
| `/lidar/pointcloud` | ← subscribe | `sensor_msgs/PointCloud2` | Gefilterde LiDAR-punten |
| `/odom` | ← subscribe | `nav_msgs/Odometry` | Robotpositie en -oriëntatie |
| `/goal_pose` | → publish | `geometry_msgs/PoseStamped` | Doel 2m voor het vuur |
| `/fire_marker` | → publish | `visualization_msgs/Marker` | Oranje bol + "VUUR" tekst in RViz |

### dijkstra_path_planner

| Topic | Richting | Type | Inhoud |
|-------|----------|------|--------|
| `/lidar/pointcloud` | ← subscribe | `sensor_msgs/PointCloud2` | LiDAR-punten voor de kaart |
| `/odom` | ← subscribe | `nav_msgs/Odometry` | Robotpositie |
| `/goal_pose` | ← subscribe | `geometry_msgs/PoseStamped` | Doellocatie (van RViz of fire_navigator) |
| `/cmd_vel` | → publish | `geometry_msgs/Twist` | Rijcommando's |
| `/map` | → publish | `nav_msgs/OccupancyGrid` | Occupancy grid (zichtbaar in RViz) |
| `/path` | → publish | `nav_msgs/Path` | Geplande route (zichtbaar in RViz) |

---

## Opstarten <a name="opstarten"></a>

```bash
docker exec gg bash -c "source /opt/ros/jazzy/setup.bash && source /workspace/ros2/install/setup.bash && ros2 launch tonk_mapping mapping.launch.py"
```

Na het opstarten start alles automatisch. Als het vuur in het camerabereik valt, rijdt de robot er automatisch naartoe.

**Handmatig een doel instellen (optioneel):**  
Gebruik de **"2D Nav Goal"** knop in de RViz toolbar en klik op de kaart.

**Debuggen:**
```bash
# Bekijk wat de thermische camera ziet
ros2 topic echo /thermal_camera_8bit/image --no-arr

# Bekijk de vuurdetectie-logs live
ros2 node info /fire_navigator

# Stop de robot direct
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}"
```
