# Opstarten simulatie
build: source /opt/ros/jazzy/setup.bash && cd /workspace/ros2 && colcon build --packages-select tonk_mapping 2>&1

run:
source /opt/ros/jazzy/setup.bash && source /workspace/ros2/install/setup.bash && ros2 launch tonk_mapping mapping.launch.py



## Terminal 1 - Simulatie + RViz

```bash
source /opt/ros/jazzy/setup.bash
cd /workspace
colcon build --packages-select tonk_mapping --symlink-install
source install/setup.bash
ros2 launch tonk_mapping mapping.launch.py
```

## Terminal 2 - WASD besturing

Open een tweede terminal in de container:

```bash
docker exec -it -e DISPLAY=:1 gg bash
```

Dan de wasd binary builden (alleen de eerste keer, of na een code wijziging):

```bash
cd /workspace/Gazebo/models/makeTonksGreat
rm -rf build && mkdir build && cd build
cmake .. && make
```

Daarna starten:

```bash
./wasd_control
```

## Bediening

| Toets | Actie |
|-------|-------|
| W | Vooruit |
| S | Achteruit |
| A | Links draaien |
| D | Rechts draaien |

## Eigen script publiceren naar /cmd_vel

```bash
# Testen via terminal (Gazebo transport):
gz topic pub /cmd_vel gz.msgs.Twist "linear: {x: 2.0}, angular: {z: 1.5}"

# Of via ROS2:
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}, angular: {z: 1.5}}"
```
