a# De Blussers - Autonome Brandblus-Robot Simulatie

> **Projectperiode:** maart - juni 2026  
> **Opdrachtgever:** Futurised  
> **Opleiding:** HBO-ICT, Hogeschool Utrecht - semester 4  
> **Team:** Dave Havelaar · Thor Oudejans · Eden Knapp · Tess Jansen

---

## Inhoudsopgave

1. [Projectbeschrijving](#1-projectbeschrijving)
2. [Wat is er gebouwd](#2-wat-is-er-gebouwd)
3. [Architectuur](#3-architectuur)
4. [Robotmodel - Tonk](#4-robotmodel--tonk)
5. [Simulatieomgeving - Parkeergarage](#5-simulatieomgeving--parkeergarage)
6. [ROS2 Nodes](#6-ros2-nodes)
7. [ROS2 Topics overzicht](#7-ros2-topics-overzicht)
8. [Installatie en opstarten](#8-installatie-en-opstarten)
9. [Manuele besturing (WASD)](#9-manuele-besturing-wasd)
10. [Requirements en realisatie](#10-requirements-en-realisatie)
11. [Projectverloop - Sprints](#11-projectverloop--sprints)
12. [Leerdoelen en wat we hebben geleerd](#12-leerdoelen-en-wat-we-hebben-geleerd)
13. [Advies voor verdere ontwikkeling](#13-advies-voor-verdere-ontwikkeling)
14. [Mappenstructuur](#14-mappenstructuur)

---

## 1. Projectbeschrijving

> **Volledige projectdocumentatie en demo's:** [deblussers.com](https://deblussers.com)  
> **APA bronvermelding:** de volledige literatuurlijst in APA-stijl is te vinden op [deblussers.com](https://deblussers.com)

**De Blussers** is een robotica-simulatieproject voor Futurised. Het doel is een autonome brandblus-robot te simuleren die:

- Vuur detecteert via een thermische camera
- Personen detecteert via een RGB camera + YOLOv8 model (finetuned op Gazebo-data)
- Zichzelf op de kaart localiseert via wiel-odometrie en IMU
- Obstakels in kaart brengt via een 3D LiDAR-sensor
- Automatisch een optimaal pad naar het vuur berekent (Dijkstra)
- Tot op een veilige afstand (2 m) voor het vuur rijdt
- De blusslang automatisch richt op het vuur via ballistische berekening

De simulatie draait volledig in **Gazebo Sim** (Gazebo Harmonic / gz-sim 10) en is gekoppeld aan **ROS2 Jazzy** via de `ros_gz_bridge`. De visualisatie verloopt via **RViz2**.

De robot - intern "Tonk" genaamd - rijdt op vier wielen (differential drive) door een gesimuleerde parkeergarage met geparkeerde auto's, obstakels en één brandende auto als doel.

---

## 2. Wat is er gebouwd

| Component | Beschrijving |
|-----------|-------------|
| **Gazebo world** | Parkeergarage (32×18 m) met muren, pilaren, parkeerlijnen, 6 gewone auto's, 1 brandende auto (carrosserie 673 K, vlammen tot 1373 K), 1 staande persoon, afvalbakken, betonblokken en verkeerskegels |
| **Robotmodel (SDF)** | 4-wielig voertuig (40 kg) met Differential Drive plugin, IMU (100 Hz), 3D LiDAR (360°×16 lagen, 40 m bereik, 10 Hz), RGB camera (640×480 px, 60° FOV, 30 Hz) en thermische camera (320×240 px, 60° FOV, 30 Hz, L8 formaat) |
| **Blusslang turret** | 2-assige turret (pan 360° + tilt 0-90°) gemonteerd bovenop de robot; aangedreven via Gazebo JointPositionController (PID) |
| **lidar_to_pointcloud** | ROS2 C++ node: filtert ruwe 3D-puntenwolk (grond, plafond, nabijheid), publiceert schone puntenwolk op `/lidar/pointcloud` |
| **imu_odometry_node** | ROS2 C++ node: verwerkt IMU + wiel-odometrie, publiceert gefilterde odometrie en TF-transform `odom → base_link` |
| **dijkstra_path_planner** | ROS2 C++ node: bouwt per LiDAR-scan een 2D occupancy grid (450×300 cellen, 0,2 m/cel), berekent kortste pad via Dijkstra, volgt pad via proportionele regelaar op 20 Hz |
| **fire_navigator** | ROS2 C++ node: detecteert vuur via thermische camera (gewogen zwaartepunt), bepaalt afstand via LiDAR, publiceert doel 2 m voor het vuur op `/goal_pose` en vuurpositie op `/fire_marker` |
| **hose_controller** | ROS2 C++ node: ontvangt vuurpositie, berekent ballistische pan/tilt-hoeken (kwadratische vergelijking, V₀=8 m/s), stuurt blusslang-turret aan op 10 Hz; publiceert waterstraal-boog als blauwe LINE_STRIP in RViz |
| **person_detection** | ROS2 Python package: YOLOv8 finetuned op custom Gazebo-dataset (10 000+ beelden, Roboflow + screenshots); detecteert personen op `/camera/image_raw`, publiceert geannoteerd beeld op `/person_detection/image` |
| **person avoidance** | robot neemt bewust een andere route als er niet veilig om de persoon heen gereden kan worden |
| **vision/** | Trainingsinfrastructuur: `train.py`, `data.yaml`, `dataset/` (images + labels in YOLO-formaat), getrainde gewichten `best1.pt` |
| **WASD besturing** | C++ programma (Gazebo transport) voor handmatig rijden tijdens ontwikkeling |
| **Dev Container** | Docker-gebaseerde ontwikkelomgeving (image `s4_2026`) voor uniform werken op alle machines |

---

## 3. Architectuur

> **Volledige uitleg navigatiepijplijn:** [Documentatie/autonome_navigatie.md](Documentatie/autonome_navigatie.md)

### Systeemoverzicht

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                GAZEBO SIM                                    │
│                                                                              │
│  /lidar/points  /imu  /odom  /clock  /thermal_camera_8bit/image             │
│  /camera/image_raw   /hose_pan_cmd  /hose_tilt_cmd                          │
└──────────────────────────────────────────────────────────────────────────────┘
                              │
                     [ros_gz_bridge]
                              │
         ┌──────────┬─────────┼───────────────┬────────────────┐
         ▼          ▼         ▼               ▼                ▼
[lidar_to_pc] [imu_odom]  [fire_navigator] [person_detector] [hose_controller]
         │          │            │               │                │
 /lidar/pointcloud  │      /fire_marker    /person_detection/    /hose_pan_cmd
         │    /odom/filtered  /goal_pose      image             /hose_tilt_cmd
         │        /tf              │                            /water_arc
         └──────────┬─────────────┘
                    ▼
        [dijkstra_path_planner]
                    │
              /cmd_vel (Twist)
                    │
         [ros_gz_bridge] → Gazebo DiffDrive
                    │
            /map   /path
                    │
                  RViz2
```

### Automatische werking (tijdlijn)

```
t=0s   Robot spawnt links in de garage (x=−14, y=0)
       LiDAR en thermische camera starten op

t=1s   fire_navigator detecteert vuur in camerabeeld
       → berekent positie brandende auto (~13,5 m, 7,5 m)
       → publiceert doel op (11,5 m, 5,5 m) via /goal_pose

t=1s   dijkstra_path_planner ontvangt doel
       → bouwt occupancy grid uit LiDAR-scan
       → Dijkstra berekent pad (~142 waypoints, ~28 m)
       → begint rijden (max 1 m/s)

t=30s  Onderweg: LiDAR-kaart wordt elke scan vernieuwd
       Obstakels worden omgereden via padherberekening

t=55s  Robot bereikt doel: 2 m voor de brandende auto
       → "Doel bereikt!" in de ROS2-log
       → hose_controller berekent ballistische hoeken (pan + tilt)
       → blusslang-turret richt zich op het vuur
       → waterstraal-boog verschijnt als blauwe parabool in RViz
```

---

## 4. Robotmodel - Tonk

Gedefinieerd in [Gazebo/models/makeTonksGreat/tonk.sdf](Gazebo/models/makeTonksGreat/tonk.sdf)

| Eigenschap | Waarde |
|-----------|--------|
| Massa | 40 kg |
| Afmetingen (carrosserie) | 1,8 × 1,4 × 0,6 m |
| Wielradius | 0,25 m |
| Wielbasis (separation) | 1,6 m |
| Aandrijving | Differential Drive (4 wielen, 2 per zijde) |
| Max koppel per wiel | 100 Nm |
| IMU update rate | 100 Hz |
| IMU noise | σ angular vel = 0,001 rad/s, σ accel = 0,01 m/s² |
| LiDAR type | GPU LiDAR (3D) |
| LiDAR horiz. bereik | 360° (360 samples) |
| LiDAR vert. bereik | −15° tot +15° (16 lagen) |
| LiDAR max afstand | 40 m |
| LiDAR update rate | 10 Hz |
| Thermische camera | 320×240 px, 60° FOV (1,047 rad), L8 (8-bit grijswaarden) |
| Camera temp. bereik | 253 K (−20°C) tot 673 K (+400°C) |
| Camera update rate | 30 Hz |
| RGB camera | 640×480 px, 60° FOV (1,05 rad), gemonteerd op voorzijde (x=0,9 m) |
| RGB camera update rate | 30 Hz |
| Blusslang - pan joint | `hose_pan_joint`: revolute om Z-as, bereik −180° tot +180° (360°) |
| Blusslang - tilt joint | `hose_tilt_joint`: revolute om −Y-as, bereik 0,05-1,57 rad (0°-90°) |
| Blusslang - PID | `JointPositionController`: p=3,0, d=0,2, i=0 (beide joints) |

**Spawn locatie in de wereld:** x=−14, y=0, z=0,35 (linkerkant van de garage)

---

## 5. Simulatieomgeving - Parkeergarage

Gedefinieerd in [Gazebo/worlds/parking_garage.world](Gazebo/worlds/parking_garage.world)

| Element | Details |
|---------|---------|
| Afmetingen vloer | 32 × 18 m |
| Muren | Noord, Zuid, Oost (3 m hoog), West heeft rijopening |
| Plafond | 3 m hoogte |
| Pilaren | 8 stuks (0,4×0,4 m) langs de wanden |
| Parkeerlijnen | 2 rijen van 7 vakken (rij A en rij B) |
| Gewone auto's | 6 stuks (blauw sedan, rode sedan, witte SUV, zilveren sedan, groene sedan, zwarte sedan) |
| Brandende auto | 1 stuks op positie (13,5, 7,5) - carrosserie 673 K, vlammen 973-1373 K |
| Obstakels rijstrook | 2 afvalbakken, 1 pallet + dozen, 2 betonblokken, 2 verkeerskegels |
| Verlichting | 6 plafondarmaturen + oranje brandgloed bij brandende auto |
| Physics engine | DARTSim (Bullet-Featherstone) |
| Thermisch systeem | Gazebo Thermal plugin - temperaturen aan objecten gekoppeld |
| Persoon | 1 staand persoon (`person_standing` model) als slachtofferscenario |

De obstakels in de rijstrook zijn bewust geplaatst als zigzag-parcours, zodat de Dijkstra pathfinder gedwongen is om te navigeren in plaats van rechtdoor te rijden.

---

## 6. ROS2 Nodes

### 6.1 lidar_to_pointcloud

**Bestand:** [ros2/tonk_mapping/src/lidar_to_pointcloud.cc](ros2/tonk_mapping/src/lidar_to_pointcloud.cc)

Filtert de ruwe 3D puntenwolk van Gazebo:

- Gooit grondreflecties weg (z < −0,75 m)
- Gooit plafondreflecties weg (z > 1,2 m)
- Gooit nabije ruis weg (range < 0,5 m)
- Publiceert statische TF-transform: `base_link → lidar` (z = 0,8 m)

**Resultaat:** schone, 2D-bruikbare puntenwolk met alleen relevante obstakels.

---

### 6.2 imu_odometry_node

**Bestand:** [ros2/tonk_mapping/src/imu_odometry_node.cc](ros2/tonk_mapping/src/imu_odometry_node.cc)  
**Documentatie:** [Documentatie/IMU_ODOMETRY_IMPLEMENTATION.md](Documentatie/IMU_ODOMETRY_IMPLEMENTATION.md)

Verwerkt sensordata voor localisatie:

- Ontvangt ruwe IMU-data (`/imu`) en berekent roll/pitch/yaw via quaternion-decompose
- Ontvangt wiel-odometrie (`/odom`) van de Gazebo DiffDrive plugin
- Voegt covariance matrices toe (positie: 0,01, snelheid: 0,05)
- Publiceert gefilterde odometrie op `/odom/filtered`
- Publiceert TF-transform `odom → base_link` voor RViz en path planner

**Toekomstige uitbreiding:** sensor fusion via Extended Kalman Filter (IMU + odometrie)

---

### 6.3 dijkstra_path_planner

**Bestand:** [ros2/tonk_mapping/src/dijkstra_path_planner.cc](ros2/tonk_mapping/src/dijkstra_path_planner.cc)  
**Documentatie:** [Documentatie/dijkstra_pathfinding.md](Documentatie/dijkstra_pathfinding.md) · [Documentatie/autonome_navigatie.md](Documentatie/autonome_navigatie.md)  
**Onderzoek:** [Documentatie/pathFinding.md](Documentatie/pathFinding.md) - onderzoek naar Nav2 en alternatieve pathfinding-aanpakken

Het hart van de autonome navigatie. Werkt in drie stappen:

#### Stap 1 - Occupancy Grid bouwen

Bij elke LiDAR-scan wordt een 2D rasterkaart gebouwd:

```
Grid: 450 × 300 cellen @ 0,2 m/cel = 90 × 60 m totale kaart
Oorsprong: (−45, −30) in odom-frame
```

LiDAR-punten (robot-relatief) worden getransformeerd naar het odom-frame:

```
wx = cos(yaw) × lx − sin(yaw) × ly + robot_x
wy = sin(yaw) × lx + cos(yaw) × ly + robot_y
```

Daarna worden obstakels geïnfleerd:

| Zone | Afstand | Celwaarde | Betekenis |
|------|---------|-----------|-----------|
| Harde zone | 0 - 1,0 m | 100 | Onpasseerbaar |
| Zachte zone | 1,0 - 1,6 m | 5 - 90 | Passeerbaar maar duur |
| Vrij | > 1,6 m | 0 | Vrij rijden |

De robotbreedte is 1,6 m, dus de 1,0 m harde inflatiezone zorgt dat het pad altijd veilig langs obstakels loopt.

#### Stap 2 - Dijkstra pathfinding

- Priority queue (min-heap) op kost
- 8-connectiviteit (ook diagonaal): diagonaal kost √2 × 0,2 m, recht kost 0,2 m
- Celkost dicht bij obstakels: extra penalty zodat het pad automatisch een ruimere route kiest
- Pad wordt teruggetraceerd via `prev[]`-array

#### Stap 3 - Pad volgen (P-regelaar, 20 Hz)

```
Hoekfout      = atan2(dy, dx) − robot_yaw    (genormaliseerd op [−π, π])
angular.z     = 2,0 × hoekfout               (proportioneel bijsturen)
linear.x      = 1,0 × max(0, cos(hoekfout))  (langzamer bij scherpe bochten)
```

- Schakelt naar volgend waypoint bij afstand < 0,4 m
- Doel bereikt bij afstand < 0,5 m
- Watchdog: als LiDAR > 1 s uitblijft (bv. Gazebo reset), wordt de kaart geleegd

---

### 6.4 fire_navigator

**Bestand:** [ros2/tonk_mapping/src/fire_navigator.cc](ros2/tonk_mapping/src/fire_navigator.cc)  
**Documentatie:** [ros2/tonk_mapping/src/README.md](ros2/tonk_mapping/src/README.md) - uitleg thermische camera en vuurdetectie

Detecteert vuur en stuurt de dijkstra_path_planner aan:

#### Stap 1 - Vuurdetectie in camerabeeld

- Drempel: pixelwaarde > 180 → temperatuur > ~276°C → vuur
- Berekent gewogen zwaartepunt van hete pixels:
  ```
  gewicht = pixelwaarde − 180   (heter = zwaarder)
  cx = Σ(pixel_x × gewicht) / Σgewicht
  ```

#### Stap 2 - Hoekbepaling

```
bearing_offset = (160 − cx) / 320 × 1,047 rad
```
(160 = horizontaal midden van de 320-brede camera)

#### Stap 3 - Afstandsbepaling via LiDAR

Zoekt in de gecachede LiDAR-scan het dichtstbijzijnde punt binnen ±8,6° van `bearing_offset`. Zo krijgen we de werkelijke afstand tot het brandende object.

#### Stap 4 - Doel berekenen

```
fire_bearing = robot_yaw + bearing_offset
fire_x = robot_x + dist × cos(fire_bearing)
fire_y = robot_y + dist × sin(fire_bearing)

goal_x = fire_x − 2,0 × cos(fire_bearing)   ← 2 m voor het vuur
goal_y = fire_y − 2,0 × sin(fire_bearing)
```

Publiceert het doel op `/goal_pose` → dijkstra_path_planner rijdt ernaartoe.

**Anti-spam:** nieuw doel alleen gestuurd als vuurpositie > 0,5 m verschoven is. Als robot al < 2,4 m van vuur: geen nieuw doel.

**RViz marker:** oranje bol + "VUUR" tekst op de vuurpositie (verdwijnt na 3 s zonder update).

---

### 6.5 hose_controller

**Bestand:** [ros2/tonk_mapping/src/hose_controller.cc](ros2/tonk_mapping/src/hose_controller.cc)  
**Documentatie:** [Documentatie/hose_controller.md](Documentatie/hose_controller.md)

Beheert de 2-assige blusslang-turret en visualiseert de waterstraal als een ballistische boog in RViz. Werkt op **10 Hz**.

#### Werking

1. **Vuurpositie ontvangen:** luistert op `/fire_marker` (sphere-marker, id=0) van `fire_navigator`
2. **Pan berekenen:** `pan_cmd = atan2(dy, dx) − robot_yaw` (richting van robot naar vuur, gecorrigeerd voor robotoriëntatie)
3. **Tilt berekenen** via exacte projectielbewegingsvergelijking:

```
Doelstelling: water gelanceerd op hoogte h₀=0,82 m met V₀=8,0 m/s
              moet landen op hoogte h_doel=0,5 m op afstand R

Substitutie u = tan(θ):
  A · u² − R · u + (A + ΔH) = 0
  A = g·R² / (2·V₀²)     ΔH = h_doel − h₀

Lage-hoek oplossing (directe schoot) = standaard brandweerslang-profiel
```

4. **Commando's publiceren:** `pan_pub_` → `/hose_pan_cmd`, `tilt_pub_` → `/hose_tilt_cmd` (Float64 → ros_gz_bridge → Gazebo PID)
5. **Waterstraal visualiseren:** 22 punten langs de exacte parabool p(t) = nozzle + v⃗·t − ½g·t², gepubliceerd als blauwe LINE_STRIP op `/water_arc`
6. **Timeout:** geen vuur gezien voor 5 s → parkeerstand (tilt=0,10 rad), boog-marker verwijderd

| Parameter | Waarde | Betekenis |
|-----------|--------|-----------|
| `V₀` | 8,0 m/s | Beginsnelheid waterstraal |
| `NOZZLE_H` | 0,82 m | Hoogte nozzle-tip boven grond |
| `FIRE_AIM_H` | 0,50 m | Richtpunt (basis vlammen) |
| `TILT_PARK` | 0,10 rad | Parkeerstand |
| `TILT_FALLBACK` | 0,35 rad | Als ballistisch niet lukt (V₀ te laag) |
| `ARC_SAMPLES` | 22 | Punten langs de parabool in RViz |

---

### 6.6 person_detector

**Bestand:** [ros2/person_detection/person_detection/detector.py](ros2/person_detection/person_detection/detector.py)  
**Documentatie:** [vision/README.md](vision/README.md) · [ros2/person_detection/README.md](ros2/person_detection/README.md)  
**Onderzoek:** [vision/personDetection.md](vision/personDetection.md) - onderzoek naar Faster R-CNN, YOLO en CNN-aanpakken

ROS2 Python node die via YOLOv8 personen detecteert in het live RGB-camerabeeld.

#### Model en dataset

Het model is finetuned bovenop de pretrained YOLOv8 (COCO-dataset) met een eigen dataset van 10 000+ beelden:
- Screenshots van de Gazebo-simulatie (parkeergarage, verschillende hoeken en afstanden)
- Aanvullende data van Roboflow
- Gelabeld in Roboflow (bounding boxes, class `person`)
- Dataset-structuur in `vision/dataset/` (YOLO-formaat: `images/train`, `images/val`, `labels/train`, `labels/val`)

Origineel model (`best.pt`) werd ook vervangen door `best1.pt` omdat de eerste versie de brandende auto ten onrechte als persoon classificeerde.

#### Werking

- Luistert op `/camera/image_raw` (RGB, 640×480, 30 Hz)
- Runt YOLOv8 inference (conf=0,5, enkel class 0 = person)
- Publiceert geannoteerd beeld met bounding boxes op `/person_detection/image`
- Logt confidence-score per detectie

### 6.7 person avoidance
Er wordt een dynamische gevarenzone gemaakt rondom de gedetecteerde persoon, waardoor de persoon niet in gevaar wordt gebracht.

- Hard radius (0.8m): wordt gemarkeerd als onpasseerbaar obstakel. de robot houdt hier afstand van.
- cost gradient(1.5): een extra zone rondom de harde grens. hoe dichter bij de persoon hoe hoger de cost.

#### Werking
Dijstra ziet de zones als duur en kiest hierdoor bij voorkeur een andere route. Als er geen andere weg is, dan kan de robot door de zachte zone rijden, maar de robot probeerd wel zo veel mogelijk afstand te houden. Detecties verlopen na 2 seconden zodat de robot niet gehinderd wordt door spook obstakels.

---

## 7. ROS2 Topics overzicht

| Topic | Type | Richting | Beschrijving |
|-------|------|----------|-------------|
| `/lidar/points` | `sensor_msgs/PointCloud2` | Gazebo → bridge | Ruwe 3D LiDAR data |
| `/lidar/pointcloud` | `sensor_msgs/PointCloud2` | lidar_to_pc → planners | Gefilterde puntenwolk |
| `/imu` | `sensor_msgs/Imu` | Gazebo → bridge | Ruwe IMU data |
| `/odom` | `nav_msgs/Odometry` | Gazebo → bridge | Wiel-odometrie (50 Hz) |
| `/odom/filtered` | `nav_msgs/Odometry` | imu_node → planners | Gefilterde odometrie + covariance |
| `/thermal_camera_8bit/image` | `sensor_msgs/Image` | Gazebo → bridge | 8-bit thermisch camerabeeld |
| `/clock` | `rosgraph_msgs/Clock` | Gazebo → bridge | Simulatietijd |
| `/cmd_vel` | `geometry_msgs/Twist` | planner → Gazebo | Rijcommando's (linear.x, angular.z) |
| `/goal_pose` | `geometry_msgs/PoseStamped` | fire_nav / RViz → planner | Doellocatie |
| `/map` | `nav_msgs/OccupancyGrid` | planner → RViz | 2D costmap |
| `/path` | `nav_msgs/Path` | planner → RViz | Geplande route |
| `/fire_marker` | `visualization_msgs/Marker` | fire_nav → RViz / hose_controller | Oranje vuurmarker (id=0 = sphere) |
| `/camera/image_raw` | `sensor_msgs/Image` | Gazebo → bridge | RGB camerabeeld (640×480, 30 Hz) |
| `/hose_pan_cmd` | `std_msgs/Float64` | hose_controller → Gazebo | Pan-joint doelhoek [rad] |
| `/hose_tilt_cmd` | `std_msgs/Float64` | hose_controller → Gazebo | Tilt-joint doelhoek [rad] |
| `/water_arc` | `visualization_msgs/Marker` | hose_controller → RViz | Ballistische waterstraal-boog (LINE_STRIP) |
| `/person_detection/image` | `sensor_msgs/Image` | person_detector → RViz | RGB beeld met YOLO bounding boxes |
| `/tf` | `tf2_msgs/TFMessage` | imu_node → RViz | `odom → base_link` transform |
| `/tf_static` | `tf2_msgs/TFMessage` | lidar_node → RViz | `base_link → lidar` transform |

---

## 8. Installatie en opstarten

### Vereisten

- Docker Desktop (Windows: WSL2 backend ingeschakeld) of Docker Engine (Linux)
- Docker image `s4_2026` (of `tonk_snapshot:jazzy` bij de devcontainer variant)
- X-server voor GUI (Windows: MobaXterm of VcXsrv; Linux: ingebouwd)

### Container starten

```bash
# Stap 1: start de container (naam 'gg')


### Bouwen

```bash
# In de container terminal:
source /opt/ros/jazzy/setup.bash
cd /workspace/ros2
colcon build --packages-select tonk_mapping person_detection --symlink-install
source install/setup.bash
```

### Simulatie starten

```bash
ros2 launch tonk_mapping mapping.launch.py
```

Dit start automatisch:
1. Gazebo Sim met de parkeergarage
2. WASD-besturing in een apart terminalvenster (als beschikbaar)
3. `ros_gz_bridge` (koppelt Gazebo aan ROS2, inclusief hose_pan_cmd/hose_tilt_cmd)
4. `lidar_to_pointcloud` node
5. `imu_odometry_node`
6. Statische TF publisher (`map → odom`)
7. `dijkstra_path_planner`
8. `fire_navigator`
9. `hose_controller` (richt blusslang automatisch op vuur)
10. `person_detector` (YOLO persoonsdetectie op RGB camera)
11. RViz2 met vooraf geconfigureerde visualisatie

### Handmatig een doel instellen (optioneel)

In RViz: klik op de **"2D Nav Goal"** knop in de toolbar en klik op de kaart.

```bash
# Via terminal:
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped \
  "{header: {frame_id: 'odom'}, pose: {position: {x: 5.0, y: 3.0}, orientation: {w: 1.0}}}"
```

### Debugcommando's

```bash
# Thermische camera wat ziet
ros2 topic echo /thermal_camera_8bit/image --no-arr

# Rijcommando's monitoren
ros2 topic echo /cmd_vel

# Robot direct stoppen
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}"

# Kaartgrootte bekijken
ros2 topic echo /map --no-arr | grep -E "width|height|resolution"

# Pad bekijken
ros2 topic echo /path
```

---

## 9. Manuele besturing (WASD)

De WASD-binary maakt gebruik van de Gazebo transport library (niet ROS2) en stuurt direct op het `/cmd_vel` Gazebo-topic. De implementatie gebruikt exponentiële afvlakking (α = 0,2) voor vloeiende acceleratie en een automatische stop na 0,7 s zonder invoer.

### Bouwen (eenmalig)

```bash
cd /workspace/Gazebo/models/makeTonksGreat
rm -rf build && mkdir build && cd build
cmake .. && make
```

### Starten

```bash
# In tweede containerterminal:
docker exec -it -e DISPLAY=:1 gg bash
./wasd_control
```

| Toets | Actie |
|-------|-------|
| W | Vooruit |
| S | Achteruit |
| A | Links draaien |
| D | Rechts draaien |

---

## 10. Requirements en realisatie

De volledige requirements, use cases (UC01-UC02), activity diagrammen en ontwerpbeslissingen staan in het [ontwikkeldocument](Documentatie/ontwikkelDocument.md).

### Functionele Requirements

| ID | Requirement | Status | Toelichting |
|----|------------|--------|-------------|
| F01 | Robot detecteert warmte van vuur en onderscheidt dit van andere warmtebronnen | ✅ Gerealiseerd | Thermische camera + drempel 180/255 L8 (≈276°C). Vuur in sim is 673-1373 K, ver boven omgevingstemperatuur |
| F02 | Waterkanon kan zelfstandig bewegen | ✅ Gerealiseerd | Blusslang-turret in `tonk.sdf` (2 revolute joints, pan 360° + tilt 0-90°); `hose_controller` node stuurt turret automatisch aan via ballistische berekening |
| F03 | Robot navigeert tussen obstakels | ✅ Gerealiseerd | Dijkstra op occupancy grid met obstakelontwijk. Getest in garage met zigzag-parcours |
| F04 | Robot rijdt autonoom naar vuur en positioneert zich | ✅ Gerealiseerd | fire_navigator + dijkstra_path_planner: rijdt zelfstandig naar 2 m voor het vuur |
| F05 | Robot weet zijn eigen positie | ✅ Gerealiseerd | Wiel-odometrie (DiffDrive, 50 Hz) + IMU (100 Hz) + TF-chain |

### Niet-Functionele Requirements

| ID | Requirement | Status | Toelichting |
|----|------------|--------|-------------|
| NF01 | Robot detecteert warmte van 1000°C | ✅ Gerealiseerd | Vlammen in simulatie bereiken 1373 K (1100°C). Camera verzadigt maar detecteert correct |
| NF02 | Robot houdt veilige afstand tijdens blussen | ✅ Gerealiseerd | Robot stopt op 2,0 m voor het vuur (STOP_DISTANCE parameter) |
| NF03 | Robot kan over obstakels van max 50 cm heen rijden | ❌ Niet gerealiseerd | Simulatie gebruikt flat-ground differential drive; obstakeloverrijding vereist ander rijderprofiel |
| NF04 | Waterkanon draait 180° horizontaal en verticaal | ✅ Gerealiseerd | Pan-joint draait 360°, tilt-joint draait 0°-90°; beide aangedreven via Gazebo JointPositionController met PID (p=3,0) |

---

## 11. Projectverloop - Sprints

Het project liep van **2 maart 2026 tot 15 juni 2026** in 7 sprints van 2-3 weken.

| Sprint | Periode | Doel | Resultaat | Verslag |
|--------|---------|------|-----------|---------|
| Sprint 1 | 02/03 - 11/03 | Repo opzetten, kennismaking, eerste proof of concept, gesprek opdrachtgever | Dev container werkend, Git-afspraken gemaakt, eerste Gazebo-test | [Sprint 1](https://github.com/2025-TICT-TV2SE4-24-3-V/team-de_blussers/blob/main/Documentatie/sprints/Sprint1.md) |
| Sprint 2 | 16/03 - 26/03 | Proof of concept uitwerken, LiDAR sensor, camera, documentatie | LiDAR subscriber, thermische camera op tank, eerste schets simulatiewereld | [Sprint 2](https://github.com/2025-TICT-TV2SE4-24-3-V/team-de_blussers/blob/main/Documentatie/sprints/Sprint2.md) |
| Sprint 3 | 30/03 - 09/04 | Componenten samenvoegen, documentatie uitbreiden | IMU toegevoegd, odometrie gekoppeld, componenten geïntegreerd, parkeergarage world opgebouwd | [Sprint 3](https://github.com/2025-TICT-TV2SE4-24-3-V/team-de_blussers/blob/main/Documentatie/sprints/Sprint3.md) |
| Sprint 4 | 13/04 - 23/04 | Componenten afmaken, robot bestuurbaar (WASD) | WASD geblokkeerd door Gazebo transport integratie; garage geoptimaliseerd | [Sprint 4](https://github.com/2025-TICT-TV2SE4-24-3-V/team-de_blussers/blob/main/Documentatie/sprints/Sprint4.md) |
| Sprint 5 | 04/05 - 14/05 | Pathfinding, visuele componenten, complexiteit toevoegen | Dijkstra pathfinder gebouwd, 3D LiDAR puntenwolk, WASD blokkade opgelost, visuele componenten | [Sprint 5](https://github.com/2025-TICT-TV2SE4-24-3-V/team-de_blussers/blob/main/Documentatie/sprints/Sprint5.md) |
| Sprint 6 | 18/05 - 28/05 | Pathfinding + visuele componenten afronden, fire_navigator | fire_navigator gebouwd, volledige autonome pijplijn werkend, brandende auto met thermische lagen | [Sprint 6](https://github.com/2025-TICT-TV2SE4-24-3-V/team-de_blussers/blob/main/Documentatie/sprints/Sprint6.md) |
| Sprint 7 | 02/06 - 11/06 | Laatste puntjes op de i, overdrachtsvoorbereiding en documentatie | Blusslang-turret + `hose_controller` geïmplementeerd, `person_detection` (YOLO) afgerond, volledige documentatie voor overdracht | [Sprint 7](https://github.com/2025-TICT-TV2SE4-24-3-V/team-de_blussers/blob/main/Documentatie/sprints/Sprint7.md) |

### Feedback ontvangen van begeleiders

- **Bart (25/03):** Quotes weghalen ontwikkeldocument, requirements preciezer formuleren (meetbare eenheden), "digitale ontwikkeling" is geen keydriver
- **Opdrachtgever (09/04):** Pathfinding implementeren, scenario bouwen, waterkanon als volgende stap
- **Bart (22/04):** Complexiteit vereist; keuze mapping vs. objectherkenning; SLAM overwegen
- **Hassan (06/05):** Meer voortgang nodig, kaartjes kleiner maken, betere planning opstellen
- **Bart (einde project):** "Overduidelijk goede inhaalslag gemaakt en goede vooruitgang. Gaat de goede kant op. Zet deze trend door."

---

## 12. Leerdoelen en wat we hebben geleerd

### ROS2 (Robot Operating System 2)

We zijn gestart zonder voorkennis van ROS2 en hebben het volgende geleerd:

- **Node architectuur:** hoe nodes via topics communiceren (publisher/subscriber pattern)
- **Launch files:** Python-gebaseerde launch files voor het starten van meerdere nodes tegelijk
- **ros_gz_bridge:** koppeling tussen Gazebo transport en ROS2 middleware
- **TF2 transforms:** frame-to-frame transformaties voor sensor- en wereldcoördinaten
- **C++17 ROS2 nodes:** `rclcpp`, timers, callbacks, shared pointers
- **colcon build system:** CMake-gebaseerde bouw van ROS2 packages

### Gazebo Sim (gz-sim)

- **SDF formaat:** beschrijven van robots (links, joints, sensors, plugins) in XML/SDF
- **Physics plugins:** DiffDrive, OdometryPublisher, Thermal, Sensors
- **Thermische simulatie:** temperaturen koppelen aan geometrie, thermische camera configureren
- **World building:** complete omgeving bouwen met lichten, muren, modellen en obstakels
- **Gazebo transport:** directe topic-communicatie buiten ROS2

### Algoritmen en wiskunde

- **Dijkstra's algoritme:** kortste pad in gewogen graaf, implementatie met priority queue (min-heap), 8-connectiviteit, pad terugtracing via prev-array
- **Occupancy Grid Mapping:** 2D rasterkaart bouwen uit sensordata, obstakelinflatie, costmap concepten
- **Coördinatensystemen en rotaties:** sensor-frame naar world-frame transformatie via rotatiematrix, quaternion decompose naar roll/pitch/yaw
- **Proportionele regelaar (P-regelaar):** hoekfout berekenen en omzetten naar stuurcommando's
- **Gewogen zwaartepunt:** vuurlokalisatie in camerabeeld
- **Projectiele beweging / ballistiek:** kwadratische vergelijking in tan(θ) voor lanceerhoek waterstraal; lage/hoge-hoek oplossing, vluchttijdberekening

### Sensorintegratie

- **3D LiDAR:** PointCloud2 verwerking, z-filtering, range filtering, punt-naar-grid transformatie
- **Thermische camera:** L8 pixelwaarden interpreteren als temperatuur, drempeldetectie
- **IMU:** quaternion → Euler hoeken, acceleratie en hoeksnelheid verwerken
- **Sensorfusie concept:** LiDAR (afstand) + thermische camera (richting) combineren voor vuurlocalisatie

### Machine Learning en Computer Vision

- **YOLOv8 (Ultralytics):** pretrained object detection model finetunen op custom dataset
- **Dataset samenstellen:** screenshots verzamelen, handmatig labelen in Roboflow (bounding boxes, YOLO-formaat)
- **Transfer learning:** waarom finetuning op 10 000+ beelden effectiever is dan training from scratch
- **OpenCV / cv_bridge:** ROS2 Image-berichten omzetten naar OpenCV-formaat voor real-time inferentie
- **Modelkeuze onderbouwen:** Faster R-CNN vs. YOLO vs. CNN vergeleken en YOLO gekozen op basis van snelheid en beschikbare pretrained gewichten

### Software engineering

- **Git workflow:** feature branches, pull requests, code reviews binnen het team
- **Docker / Dev Container:** reproduceerbare ontwikkelomgeving, cross-platform werken
- **CMake + ament_python:** C++17 en Python ROS2 packages tegelijk bouwen en installeren
- **Scrum / Agile:** sprint planning, daily scrums, reviews, retrospectives, backlog beheer via GitHub Projects
- **Documentatie:** ontwikkeldocument, use cases, SVD (Stakeholder Value Diagram), sprint verslagen, technische docs

### Teamwork

- Werken met een opdrachtgever (Futurised) en begeleiders (Bart, Hassan)
- Constructieve peer assessments per sprint
- Omgaan met blokkades (WASD-issue) door samen te zoeken naar een fix
- Taakverdeling: Dave + Thor (pathfinding), Eden + Dave (3D LiDAR), Tess + Eden (visuele componenten)

---

## 13. Advies voor verdere ontwikkeling

Dit hoofdstuk is opgesteld ten behoeve van de overdracht aan Futurised en eventuele opvolgende teams. Het beschrijft concrete verbeterpunten, geordend op prioriteit en impact.

---

### 13.1 Persoonsherkenning uitbreiden

**Huidige situatie:** De `person_detector` node detecteert personen via YOLOv8 (finetuned op Gazebo-data) op het RGB-camerabeeld. Het systeem werkt voor **staande** personen. Andere houdingen - sittend, liggend, kruipend - zijn ondervertegenwoordigd in de huidige trainingsdataset en worden minder betrouwbaar gedetecteerd. Dit is een realistisch knelpunt: bij brand liggen slachtoffers juist dikwijls bewusteloos op de vloer.

**Aanbeveling:**
- Breidt de trainingsdataset uit met Gazebo-renders van het bestaande `person_standing` model in liggende, zittende en kruipende poses (pas het SDF-model aan of voeg nieuwe person-modellen toe)
- Herbenoem of voeg extra Roboflow-data toe met gelabelde personen in niet-staande houdingen
- Hertraineer `best1.pt` met het uitgebreide dataset via het bestaande `vision/train.py` script
- Overweeg om de thermische camera als tweede detectiekanaal te gebruiken: menselijk lichaam (~37°C = ~310 K) onderscheidt zich thermisch ook bij rook

---

### 13.2 Simulatiefysica verbeteren

**Huidige situatie:** De robot gebruikt een vereenvoudigd physics-model (flat-ground differential drive). Wrijving en wielslip zijn beperkt geconfigureerd, het rijgedrag bij obstakels is soms onnatuurlijk en de robot kan geen terreinverschillen verwerken.

**Aanbeveling:**
- Verfijn de wrijvingsparameters per wiel in `tonk.sdf`: de huidige `mu=1.5 / mu2=0.3` zijn een eerste schatting; kalibreer op basis van gemeten slip bij scherpe bochten
- Voeg botsrespons toe voor kleine objecten (bijv. verkeerskegels): die worden nu genegeerd als ze buiten het LiDAR-bereik liggen
- Overweeg een tracked vehicle plugin (rupsband) als vervanging van de differential drive, zodat de robot ook over drempels en puin kan rijden - relevant voor realistische brandweerscenario's
- De DARTSim physics engine biedt ondersteuning voor zachte contactmodellen; dit kan de realisme van het rijgedrag op ongelijke ondergronden aanzienlijk verbeteren

---

### 13.3 SLAM-integratie voor betrouwbaardere localisatie

**Huidige situatie:** De robot localiseert zich uitsluitend via wiel-odometrie, die bij langere ritten drift vertoont. Er is geen kaartgeheugen: bij elke LiDAR-scan wordt de kaart volledig opnieuw gebouwd.

**Aanbeveling:**
- Integreer **KISS-ICP** - de library is al gecloned in `kiss_icp/`. Het is een LiDAR-odometrie pipeline die zonder parametertuning werkt op de meeste omgevingen:
  ```bash
  ros2 launch kiss_icp odometry.launch.py topic:=/lidar/pointcloud
  ```
- Combineer KISS-ICP met `slam_toolbox` voor een volledige SLAM-implementatie: KISS-ICP levert nauwkeurige pose-schattingen, slam_toolbox bouwt een persistente kaart
- Dit lost ook het probleem op dat de robot bij een Gazebo-reset de kaart kwijtraakt

---

### 13.4 Blusoperatie vervolledigen

**Huidige situatie:** De blusslang-turret is geïmplementeerd (`hose_controller`, 2 revolute joints in `tonk.sdf`) en richt zich automatisch op het vuur via ballistische berekening. De waterstraal wordt als blauwe parabool gevisualiseerd in RViz. Het daadwerkelijk **doven** van het vuur is echter nog niet gesimuleerd.

**Aanbeveling:**
- Voeg een water particle system toe in Gazebo Sim dat emit vanuit de nozzle-tip (Gazebo ondersteunt ParticleEmitter via SDF `<particle_emitter>`)
- Modelleer het "doven" door de temperatuur van het brandende auto-model te verlagen via een Gazebo service call of door een custom plugin die op `/water_hit` berichten reageert
- Koppel een stopsignaal aan de `dijkstra_path_planner`: als de robot op positie is én de blusslang actief richt, hoeft de robot niet meer te rijden

---

### 13.5 Overige verbeterpunten

| Punt | Uitleg | Aanpak |
|------|--------|--------|
| Herstelgedrag bij blokkade | Robot stopt als Dijkstra geen pad vindt | Voeg rotatie-recovery toe: draai 360° en herplan |
| Dynamische obstakels | Bewegende mensen/voertuigen worden niet verwerkt | Costmap met time-decay (obstakels verdwijnen als LiDAR ze niet meer ziet) |
| Meerdere scenario's | Simulatie is één vaste garage | Maak de wereld configureerbaar via launch-argumenten; voeg alternatieve worlds toe (magazijn, kantoor) |
| ROS2 teleop | WASD vereist een aparte Gazebo-transport binary | Vervang door `ros2 run teleop_twist_keyboard teleop_twist_keyboard` voor standaard ROS2-besturing |
| Meerdere robots | Systeem ondersteunt nu één Tonk | Schaal op naar multi-robot door namespacing toe te voegen aan alle topics en nodes |

---

## 14. Mappenstructuur

```
team-de_blussers/
├── .devcontainer/
│   ├── devcontainer.json          VS Code Dev Container configuratie
│   └── Dockerfile                 Container definitie (leeg - gebruikt bestaand image)
│
├── Documentatie/
│   ├── autonome_navigatie.md      Uitleg over het volledige navigatiesysteem
│   ├── dijkstra_pathfinding.md    Technische uitleg Dijkstra implementatie
│   ├── hose_controller.md         Technische uitleg blusslang-turret + ballistiek
│   ├── IMU_ODOMETRY_IMPLEMENTATION.md  IMU + odometrie implementatiedocument
│   ├── ontwikkelDocument.md       Formeel ontwikkeldocument (requirements, use cases)
│   ├── SVD.md                     Stakeholder Value Diagram
│   ├── team_contract.md           Teamafspraken en contactgegevens
│   ├── feedback/                  Vergaderverslagen met docenten en opdrachtgever
│   ├── sprints/                   Sprint verslagen 1-7
│   ├── diagrams/                  PlantUML use case diagrammen
│   ├── doelen/                    Pathfinding doelen notities
│   └── presentaties/              Pitch presentatie (Futurised)
│
├── Gazebo/
│   ├── models/
│   │   ├── makeTonksGreat/        Hoofdrobot model
│   │   │   ├── tonk.sdf           Robot definitie (links, joints, sensoren, plugins)
│   │   │   ├── wasd_control.cc    Handmatige besturing via Gazebo transport
│   │   │   ├── lidar_subscriber.cc  Test: LiDAR data printen
│   │   │   ├── thermal_camera_test.cc  Test: thermische camera output
│   │   │   ├── publisher.cc       Test: velocity publisher
│   │   │   ├── CMakeLists.txt     Build voor Gazebo plugins/tools
│   │   │   └── model.config       Gazebo model metadata
│   │   ├── thermal_camera/        Losse thermische camera test setup
│   │   ├── tank_with_cam/         Alternatief tank model (vroeg prototype)
│   │   ├── fire_tank/             Vuurmodel voor losstaand gebruik
│   │   └── heated_object/         Verwarmde objecten test
│   └── worlds/
│       └── parking_garage.world   Hoofdsimulatie: volledige parkeergarage
│
├── ros2/
│   ├── tonk_mapping/              ROS2 C++ package (5 nodes)
│   │   ├── src/
│   │   │   ├── dijkstra_path_planner.cc   Autonome navigatie node
│   │   │   ├── fire_navigator.cc          Vuurdetectie + doelpublicatie node
│   │   │   ├── hose_controller.cc         Blusslang-turret controller (ballistisch)
│   │   │   ├── imu_odometry_node.cc       IMU + odometrie verwerkingsnode
│   │   │   └── lidar_to_pointcloud.cc     LiDAR filter node
│   │   ├── launch/
│   │   │   ├── mapping.launch.py          Hoofd-lanceerscript (alle nodes)
│   │   │   └── full_system.launch.py      Alternatief lanceerscript (met person_detector)
│   │   ├── rviz/
│   │   │   └── mapping.rviz               RViz visualisatieconfiguratie
│   │   ├── CMakeLists.txt                 Build configuratie
│   │   └── package.xml                    Package metadata en dependencies
│   └── person_detection/          ROS2 Python package (YOLOv8 persoonsdetectie)
│       ├── person_detection/
│       │   ├── detector.py                YOLOv8 inference node
│       │   └── thermal_relay.py           Thermische camera relay (hulpscript)
│       ├── launch/detection.launch.py     Launch voor persoonsdetectie
│       ├── README.md                      Uitleg vision module
│       └── setup.py                       Python package configuratie
│
├── vision/                        Trainingsinfrastructuur YOLOv8
│   ├── train.py                   Finetuning script (PyTorch + Ultralytics)
│   ├── data.yaml                  YOLO dataset configuratie (paden + classes)
│   ├── dataset/                   Trainingsdataset (YOLO-formaat)
│   │   ├── images/train/          Trainingsafbeeldingen
│   │   ├── images/val/            Validatieafbeeldingen
│   │   ├── labels/train/          YOLO-labels training
│   │   └── labels/val/            YOLO-labels validatie
│   └── README.md                  Uitleg trainingsproces en modelkeuze
│
├── kiss_icp/                      Externe SLAM-library (KISS-ICP, gecloned voor onderzoek)
│                                  Niet actief geïntegreerd; verkend als verbetering voor odometriedrift
│
├── devcontainer_README.md         Setup-handleiding Dev Container (Windows/Mac)
├── OPSTARTEN.md                   Snelle opstartcommando's
├── ros2_command.md                Veelgebruikte ROS2 commando's
├── start_container.sh             Script om de Docker container te starten
├── start_gz.sh                    Script dat het volledige systeem opstart (build + full_system.launch.py)
└── README.md                      Dit document
```

---

## Team

| Naam | Studentnummer | Bijdrage |
|------|--------------|---------|
| Dave Havelaar | 1882008 | Git beheer, pathfinding (Dijkstra), 3D LiDAR integratie, fire_navigator, documentatie, feedback sprint reviews |
| Thor Oudejans | 1876289 | Dev Container, componenten integratie, pathfinding (Dijkstra), fire_navigator, blusslang-turret (hose_controller), documentatie |
| Eden Knapp | 1876133 | LiDAR sensor, parkeergarage world, 3D LiDAR puntenwolk, visuele componenten, oplevering website (deblussers.com), documentatie |
| Tess Jansen | 1884367 | Thermische camera, functionele requirements, visuele componenten, WASD, persoonsherkenning (person_detection / YOLO), vision module, person avoidance, documentatie |

**Opdrachtgever:** Futurised  
**Begeleiders:** Bart Bozon, Hassan  
**Opleiding:** HBO-ICT, Hogeschool Utrecht - TV2SE4, semester 4, 2025-2026
