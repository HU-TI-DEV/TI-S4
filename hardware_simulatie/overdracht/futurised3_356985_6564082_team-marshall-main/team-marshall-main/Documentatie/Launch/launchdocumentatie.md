# Documentatie: `launch.py` — Futurised ROS2 Launch File

## Overzicht

Dit launch-bestand start een complete SLAM-pipeline op in combinatie met Gazebo-simulatie. Het doet het volgende in volgorde:

1. Start een ROS↔Gazebo bridge (topics doorgeven)
2. Start een TF broadcaster (coördinaatframes publiceren)
3. Start SLAM Toolbox (asynchroon, met vertraging)
4. Configureert en activeert SLAM via lifecycle-commando's
5. Start een autonome explorer
6. Start RViz voor visualisatie

---

## Componenten

### `bridge` — ROS-Gazebo Bridge
```python
Node(package='ros_gz_bridge', executable='parameter_bridge', ...)
```
Verbindt Gazebo-topics met ROS2. Leest de topicmapping uit `bridge.yaml`.

| Parameter | Waarde |
|-----------|--------|
| `config_file` | `/workspace/Futurised/bridge.yaml` |
| `lazy` | `False` — alle topics meteen verbinden |

---

### `tf_node` — TF Broadcaster
```python
ExecuteProcess(cmd=['python3', '/workspace/Futurised/tf_broadcaster.py', ...])
```
Publiceert de transformaties tussen frames (`base_link`, `odom`, `map`, etc.). Gebruikt simulatietijd via `use_sim_time:=true`.

---

### `slam` — SLAM Toolbox (na 5 seconden)
```python
TimerAction(period=5.0, actions=[Node(package='slam_toolbox', ...)])
```
Start de asynchrone SLAM-node. Wacht 5 seconden om de bridge en TF eerst op te starten.

Belangrijke parameters:

| Parameter | Waarde | Betekenis |
|-----------|--------|-----------|
| `scan_topic` | `/scan` | Laser-scan input |
| `base_frame` | `base_link` | Robotframe |
| `odom_frame` | `odom` | Odometryframe |
| `map_frame` | `map` | Kaartframe |
| `resolution` | `0.05` | Kaartresolutie in meters |
| `max_laser_range` | `10.0` | Maximaal laserbereik |
| `transform_timeout` | `2.0` | Wachttijd op TF-transforms |
| `tf_buffer_duration` | `30.0` | TF-historielengte |

---

### `configure_slam` — Lifecycle: Configure (na 12 seconden)
```python
TimerAction(period=12.0, actions=[ExecuteProcess(cmd=['ros2', 'lifecycle', 'set', '/slam_toolbox', 'configure'])])
```
Zet de SLAM-node in de `configured`-staat. Moet gebeuren voordat `activate` wordt aangeroepen.

---

### `activate_slam` — Lifecycle: Activate (na 15 seconden)
```python
TimerAction(period=15.0, actions=[ExecuteProcess(cmd=['ros2', 'lifecycle', 'set', '/slam_toolbox', 'activate'])])
```
Activeert de SLAM-node zodat hij daadwerkelijk gaat mappen.

---

### `explorer` — Autonome Verkenner (na 20 seconden)
```python
TimerAction(period=20.0, actions=[ExecuteProcess(cmd=['python3', '/workspace/Futurised/explorer.py', ...])])
```
Start het autonome navigatiescript pas als SLAM actief is.

---

### `rviz` — Visualisatie (na 10 seconden)
```python
TimerAction(period=10.0, actions=[Node(package='rviz2', executable='rviz2', ...)])
```
Laadt RViz met een vooraf ingestelde configuratie voor SLAM-visualisatie.

---

### `room_detector` — Kamerdetectie (uitgeschakeld)
```python
# room_detector = TimerAction(...)
```
Uitgecommentarieerd. Was bedoeld om na 20 seconden te starten naast de explorer.

---

## Tijdlijn

```
t=0s   → bridge + tf_node starten tegelijk
t=5s   → slam_toolbox node start
t=10s  → rviz start
t=12s  → slam lifecycle: configure
t=15s  → slam lifecycle: activate
t=20s  → explorer start
```

---

## Bekende Fouten en Oplossingen

### 1. SLAM lifecycle configure/activate mislukt
**Symptoom:** `Failed to call service /slam_toolbox/change_state`  
**Oorzaak:** De SLAM-node is nog niet volledig opgestart na 12 seconden, of de node-naam klopt niet.  
**Oplossing:**
- Vergroot `period` in `configure_slam` naar `15.0` en `activate_slam` naar `18.0`
- Controleer de exacte node-naam met `ros2 node list` tijdens de run
- Zorg dat de SLAM-node als lifecycle node is geregistreerd (dit is standaard zo in slam_toolbox)

---

### 2. TF-fouten: "Could not find a connection between 'map' and 'base_link'"
**Symptoom:** SLAM of navigator klaagt over ontbrekende TF-frames  
**Oorzaak:** `tf_broadcaster.py` publiceert de verkeerde frames, of start te laat  
**Oplossing:**
- Controleer of `tf_broadcaster.py` de frames `odom → base_link` en `map → odom` publiceert
- Voeg een kleine `TimerAction` toe zodat de bridge eerst volledig verbonden is
- Gebruik `ros2 run tf2_tools view_frames` om de frameboom te debuggen

---

### 3. `/scan`-topic komt niet aan bij SLAM
**Symptoom:** De kaart wordt niet opgebouwd  
**Oorzaak:** `bridge.yaml` mapt de Gazebo lasertopic niet correct naar `/scan`  
**Oplossing:**
- Controleer `bridge.yaml` op een regel als:
  ```yaml
  - ros_topic_name: "/scan"
    gz_topic_name: "/lidar"
    ros_type_name: "sensor_msgs/msg/LaserScan"
    gz_type_name: "gz.msgs.LaserScan"
    direction: GZ_TO_ROS
  ```
- Verifieer met `ros2 topic echo /scan`

---

### 4. Simulatietijd problemen (`use_sim_time`)
**Symptoom:** Nodes lopen achter of TF heeft verkeerde timestamps  
**Oorzaak:** Sommige nodes gebruiken wall clock in plaats van `/clock` van Gazebo  
**Oplossing:**
- Zorg dat **alle** nodes `use_sim_time: True` hebben
- Controleer of Gazebo de `/clock`-topic publiceert via de bridge
- Voeg aan `bridge.yaml` toe:
  ```yaml
  - ros_topic_name: "/clock"
    gz_topic_name: "/clock"
    ros_type_name: "rosgraph_msgs/msg/Clock"
    gz_type_name: "gz.msgs.Clock"
    direction: GZ_TO_ROS
  ```

---

### 5. RViz laadt niet of crasht
**Symptoom:** RViz start maar toont niets, of sluit meteen  
**Oorzaak:** Het `.rviz`-bestand mist topics die nog niet bestaan, of het pad klopt niet  
**Oplossing:**
- Controleer of `/workspace/Futurised/slam_rviz.rviz` bestaat
- Stel in RViz handmatig de juiste topics in en sla opnieuw op
- Voeg `--allow-external-libs` toe als RViz plugins mist

---

### 6. Explorer start maar robot beweegt niet
**Symptoom:** `explorer.py` draait maar de robot navigeert niet  
**Oorzaak:** Nav2 of de actionserver is niet actief, of de kaart is nog leeg  
**Oplossing:**
- Zorg dat SLAM actief (`activated`) is vóór de explorer start
- Vergroot `period` van `explorer` naar `25.0` als dat niet zeker is
- Controleer of de navigator (`nav2`) apart gestart moet worden

---

## Iets Toevoegen

### `room_detector` weer inschakelen

Verwijder de commentaarstekens (`# `) van het `room_detector`-blok én de regel in `LaunchDescription`:

```python
# Verwijder # voor de volgende regels:
room_detector = TimerAction(
    period=20.0,
    actions=[ExecuteProcess(
        cmd=['python3', '/workspace/Futurised/room_detector.py',
             '--ros-args', '-p', 'use_sim_time:=true'],
        output='screen'
    )]
)

# En in LaunchDescription:
return LaunchDescription([
    ...
    room_detector,  # ← toevoegen
    ...
])
```
Het belangrijkste voor room_detector is dat hij door heeft waar 'hot spots liggen' bijvoorbeeld POI (point of interest). Waarom? Omdat de robot moet kunnen weten waar belangrijke punten liggen

---

## Tips

- Gebruik `ros2 node list` en `ros2 topic list` om te controleren wat er draait
- Gebruik `ros2 lifecycle list /slam_toolbox` om de staat van SLAM te zien
- Als timings problemen geven, vergroot dan de `period`-waarden stap voor stap (met 2–3 seconden per keer)
- Zet `output='screen'` op alle nodes om foutmeldingen direct te zien