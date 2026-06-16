# IMU & Odometry Sensor Implementation

## Overzicht
Dit document beschrijft de implementatie van IMU (Inertial Measurement Unit) en Odometry sensoren voor de Tonk robot in Gazebo.

## Implementatie Details

### 1. Gazebo Model (tonk.sdf)

#### IMU Sensor
- **Link**: `imu` (gepositioneerd op z=0.3m, midden op de robot)
- **Type**: IMU sensor
- **Update Rate**: 100 Hz
- **Output Topic**: `/imu`
- **Noise Model**: Gaussian noise op lineaire acceleratie en hoeksnelheid
  - Angular velocity noise: σ = 0.001 rad/s
  - Linear acceleration noise: σ = 0.01 m/s²

**Metingen**:
- Angular velocity (x, y, z) in rad/s
- Linear acceleration (x, y, z) in m/s²
- Orientation quaternion (x, y, z, w)

#### Odometry Plugin
- **Plugin Type 1**: `gz-sim-diff-drive-system`
  - Controleert wielbeweging via `/cmd_vel` topic
  - Publiceert odometry data naar `/odom` topic
  - Publish frequency: 50 Hz
  
- **Plugin Type 2**: `gz-sim-odometry-publisher-system`
  - Aanvullende odometry publisher voor 3D dimensies

**Odometry Output**:
- Positie (x, y, z) in meters
- Oriëntatie als quaternion
- Lineaire snelheid (vx, vy, vz) in m/s
- Hoeksnelheid (ωx, ωy, ωz) in rad/s

### 2. ROS2 Node: imu_odometry_node.cc

#### Functionaliteit
Dit is een centrale verwerkingsnode die:

1. **IMU Data Verwerking**:
   - Ontvangt raw IMU data van `/imu`
   - Berekent roll, pitch, yaw van quaternion
   - Publiceert verwerkte IMU data naar `/imu/processed`
   - Debug logging voor alle IMU metingen

2. **Odometry Verwerking**:
   - Ontvangt odometry data van `/odom` (Gazebo)
   - Filtert/verifieert de data
   - Voegt covariance matrices toe (onzekerheidsgegevens)
   - Publiceert gefilterde odometry naar `/odom/filtered`

3. **Transform Publishing**:
   - Publiceert TF transformatie van `odom` frame naar `base_link` frame
   - Essentieel voor RViz visualisatie en path planning

#### Topics
```
Input:
  /imu           - sensor_msgs/Imu (van Gazebo)
  /odom          - nav_msgs/Odometry (van Gazebo DiffDrive plugin)

Output:
  /imu/processed         - sensor_msgs/Imu (verwerkt)
  /odom/filtered         - nav_msgs/Odometry (gefilterd)
  /tf                    - geometry_msgs/TransformStamped
```

### 3. Launch File Configuratie

De launch file (`mapping.launch.py`) bevat nu:

```python
# ROS-Gazebo Bridge (nieuw: IMU en Odometry bridging)
bridge = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '/lidar/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
        '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',           # NIEUW
        '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',   # NIEUW
        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
    ],
)

# Nieuwe IMU & Odometry verwerkingsnode
imu_odometry = Node(
    package='tonk_mapping',
    executable='imu_odometry_node',
)
```

### 4. Dependencies Toegevoegd

**package.xml**:
- `nav_msgs` - Voor Odometry message type

**CMakeLists.txt**:
- Link met `imu_odometry_node` executable
- Dependencies: rclcpp, sensor_msgs, nav_msgs, geometry_msgs, tf2_ros, tf2

## Bouwen en Testen

### Build
```bash
cd /workspace/ros2
colcon build --packages-select tonk_mapping
source install/setup.bash
```

### Lanceren
```bash
ros2 launch tonk_mapping mapping.launch.py
```

### Monitoren
In een nieuw terminal:
```bash
# IMU data
ros2 topic echo /imu/processed

# Odometry data
ros2 topic echo /odom/filtered

# Beschikbare transforms
ros2 run tf2_tools static_transform_publisher
```

## Sensor Kalibratie

### IMU Calibratie
- **Accelerometer offset**: Gazebo gebruikt realistisch model
- **Gyroscope bias**: Gaussian noise (σ = 0.001 rad/s)
- In praktijk: IMU moet gekalibreerd worden op stationair platform

### Odometry Calibratie
- **Wheel Radius**: 0.25 m (gedefinieerd in tonk.sdf)
- **Wheel Separation**: 1.6 m (afstand tussen wielen)
- **Accuraatheid**: Afhankelijk van diff-drive model accuracy

## Integratie met Andere Componenten

1. **Mapping (LiDAR)**:
   - IMU helpt met tilt-correctie van LiDAR data
   - Odometry geeft coarse pose estimate voor mapping

2. **Navigation**:
   - Odometry is essentieel voor autonome navigatie
   - IMU helpt met slipdetectie en zwaartekrachtfiltering

3. **Localization**:
   - Kan later uitgebreid worden met EKF (Extended Kalman Filter)
   - Fusie van IMU + Odometry + LiDAR voor betere pose estimate

## Toekomstige Verbeteringen

1. **Sensor Fusion** - EKF of UKF implementatie
2. **IMU Calibratie** - Automatic bias estimation
3. **Wheel Slip Detection** - Compare IMU heading met odometry heading
4. **Dead Reckoning** - Backup navigatie zonder LiDAR
5. **Magneometer** - Absolute heading reference (niet in Gazebo)

## Bestandswijzigingen Samenvatting

| Bestand | Wijziging | Reden |
|---------|-----------|-------|
| tonk.sdf | IMU link + sensor + joint toegevoegd | IMU data collection |
| tonk.sdf | Odometry plugins geconfigureerd | Wheel odometry berekening |
| imu_odometry_node.cc | NIEUW bestand | Sensor data verwerking |
| package.xml | nav_msgs dependency | Odometry message type |
| CMakeLists.txt | imu_odometry_node build config | Compilatie van nieuwe node |
| mapping.launch.py | IMU/Odometry bridge topics | ROS-Gazebo communicatie |
| mapping.launch.py | imu_odometry_node launcher | Node startup in launch file |

---
**Status**: ✅ Volledige implementatie gereed
**Testdatum**: 2026-05-12
**Versie**: 1.0
