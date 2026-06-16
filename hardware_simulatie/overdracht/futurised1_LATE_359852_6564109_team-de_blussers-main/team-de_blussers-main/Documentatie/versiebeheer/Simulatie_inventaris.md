# Gazebo Simulatie - Inventaris

Dit document geeft een overzicht van alle componenten die gebruikt worden in de Gazebo simulatie voor het project van De Blussers, een autonome brandbestrijdingsrobot. Het is gebaseerd op de bestaande documentatie en code in de repository.

---

## Project Overzicht

**Doel**: Simulatie van een autonome brandbestrijdingsrobot met vuurdetectie, navigatie, obstakelvermijding en blussing.

**Belangrijke Eisen**:
- Vuurdetectie en differentiatie (>400°C)
- Autonome kanonpositionering en beweging
- Obstakelvermijding tussen waypoints
- Zelflokalisatie en oriëntatiebewustzijn

---

## 1. Simulatieomgeving

- **Gazebo versie**: 10.0.0
- **Docker image**: s4_2026
- **Host OS / WSL versie**: Linux

---

## 2. World-instellingen

- **World bestand**: parking_garage.world (SDF versie 1.6)
- **Physics engine**: gz-sim-physics-system
- **Gravity (x y z)**: Standaard (-9.81 in z-richting)
- **Real-time factor doel**: Niet gespecificeerd

### Tijdstappen
- **Max step size**: Niet gespecificeerd
- **Real-time update rate**: Niet gespecificeerd

---

## 3. Robotmodel

- **Model type**: SDF (versie 1.10)
- **Basis frame (`base_link`) gedefinieerd**: Ja

---

## 4. Sensors (basis)

| Sensor | Update rate | Noise model | Opmerkingen | Geïmplementeerd |
|--------|-------------|-------------|-------------|-----------------|
| LiDAR | 10 Hz | Niet gespecificeerd | 360 samples, bereik 0.1-10m, topic /lidar | Ja |
| Thermal Camera Sensor | Niet geïmplementeerd | Niet gespecificeerd | Voor vuurdetectie | ja |
| Camera | 30 Hz | Niet gespecificeerd | 640×480, FoV 60°, topic /camera/image_raw (alleen in tank_with_cam) | Ja (variant) |
| IMU | Niet geïmplementeerd | Niet gespecificeerd | Voor oriëntatie | Nee |
| Odometry | Niet geïmplementeerd | Niet gespecificeerd | Voor positie | Nee |

---

## 5. Plugins & koppelingen

- **Gebruikte Gazebo plugins**: gz-sim-physics-system, gz-sim-user-commands-system, gz-sim-scene-broadcaster-system, gz-sim-sensors-system (render_engine: ogre2), gz-sim-diff-drive-system
- **ROS ↔ Gazebo bridge**: ros_gz_bridge voor berichten tussen ROS2 en Gazebo

---

## 6. Rendering & uitvoering

- **GUI gebruikt**: Ja
- **Headless modus**: Ja (mogelijk voor remote uitvoering)

---

## Gazebo Modellen

### makeTonksGreat (Primaire robot)
- **Bestand**: tonk.sdf
- **Afmetingen**: 1.8m × 1.4m × 0.6m
- **Massa**: 40 kg
- **Spawn pose**: (0, 0, 0.35m)
- **Aandrijving**: Differentiële aandrijving, 4 wielen (straal 0.25m, afstand 1.6m)
- **Sensoren**: GPU LiDAR (360 samples, 10 Hz, bereik 0.1-10m)
- **Controle**: /cmd_vel topic

### tank_with_cam (Variant met camera)
- **Bestand**: tonk.sdf
- **Extra sensor**: RGB Camera (640×480, 30 Hz, FoV 60°, pose 0.9, 0, 0.4)

### heated_object (Vuur simulatie)
- **Bestand**: model.sdf
- **Type**: Thermisch doelobject (1×1×1m rode kubus)
- **Doel**: Detecteerbaar door thermische sensoren

### fire_tank (Placeholder)
- **Bestand**: model.sdf
- **Status**: Leeg, voor toekomstige brandtank model

---

## Werelden

### parking_garage.world
- **Afmetingen**: 32m × 18m × 3.05m hoogte
- **Terrain**: Betonnen vloer met parkeerstroken
- **Verlichting**: 1 richtinggevend zonlicht, 6 puntlichten
- **Statische structuren**: Muren, pilaren, plafond, parkeerplaatsen
- **Obstakels**: 6 geparkeerde auto's (verschillende modellen)
- **Doel**: Navigatietest met obstakels

---

## ROS2 Integratie

### Package: tonk_mapping
- **Locatie**: ros2/tonk_mapping/
- **Versie**: 0.1.0
- **Taal**: C++17
- **Afhankelijkheden**: rclcpp, sensor_msgs, geometry_msgs, laser_geometry, tf2_ros, tf2
- **Executables**:
  - lidar_to_pointcloud: Converteert LaserScan naar PointCloud2, publiceert /lidar/pointcloud

### Launch File: mapping.launch.py
- **Componenten**:
  - Gazebo Sim met tonk.sdf
  - ROS-Gazebo Bridge voor /lidar en /cmd_vel
  - LiDAR naar PointCloud converter
  - RViZ2 voor visualisatie

---

## Bestanden Opbouw

De simulatie gebruikt SDF (Simulation Description Format) bestanden voor modellen en werelden.

- **Model bestanden** (bijv. tonk.sdf): Bevatten modeldefinitie, links, joints, sensoren, plugins.
- **Wereld bestanden** (bijv. parking_garage.world): Bevatten wereldinstellingen, modellen via <include> tags, lichten, physics.

Voorbeeld: parking_garage.world includeert modellen zoals auto's via <include><uri>model://car</uri></include>.

ROS2 packages volgen standaard structuur: src/, launch/, rviz/, CMakeLists.txt, package.xml.

---

## Communicatie Architectuur

```mermaid
graph TD
    A[Keyboard Input WASD] --> B[wasd_control.cc]
    B --> C[/cmd_vel gz::msgs::Twist]
    C --> D[DiffDrive Plugin]
    D --> E[Robot Beweging]
    F[GPU LiDAR Sensor] --> G[/lidar gz.msgs.LaserScan]
    G --> H[ros_gz_bridge]
    H --> I[/lidar sensor_msgs/LaserScan]
    I --> J[lidar_to_pointcloud]
    J --> K[/lidar/pointcloud sensor_msgs/PointCloud2]
    K --> L[RViZ2 Visualisatie]
```

---

## Build Instructies

### Voor Gazebo modellen (C++ programma's)
```bash
cd Gazebo/models/makeTonksGreat
cmake ..
make
./wasd_control  # of ./cmd_vel_publisher / ./lidar_subscriber
```

### Voor ROS2 packages
```bash
cd ros2/tonk_mapping
colcon build
source install/setup.bash
ros2 launch tonk_mapping mapping.launch.py
```

### Start simulatie
```bash
gz sim -r Gazebo/worlds/parking_garage.world
```

---

Dit document dient als centrale referentie. Voor meer details, zie de bronbestanden in de repository.