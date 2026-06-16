# Blusslang Turret Controller - Tonk Waterblus Robot

## Inhoudsopgave
1. [Systeemoverzicht](#systeemoverzicht)
2. [Mechanisch ontwerp in Gazebo](#mechanisch-ontwerp)
3. [Ballistische hoekberekening](#ballistiek)
4. [ROS2 architectuur](#ros2-architectuur)
5. [Visualisatie in RViz](#visualisatie)
6. [Topics overzicht](#topics)
7. [Opstarten](#opstarten)
8. [Bronnen](#bronnen)

---

## Systeemoverzicht <a name="systeemoverzicht"></a>

De `hose_controller` node beheert de blusslang-turret van de Tonk robot. Zodra de `fire_navigator` node een vuurpositie detecteert, richt de turret zich automatisch op het vuur en stuurt een waterstraal in een ballistische boog.

```
┌──────────────────────────────────────────────────────────────┐
│                         INVOER                               │
│                                                              │
│   /fire_marker (vuurpositie)        /odom (robotpositie)     │
│          │                                   │               │
└──────────┼───────────────────────────────────┼───────────────┘
           │                                   │
           ▼                                   ▼
   ┌───────────────────────────────────────────────────┐
   │                  hose_controller                  │
   │                                                   │
   │  1. Bereken PAN-hoek    (richting naar vuur)      │
   │  2. Bereken TILT-hoek   (ballistische booghoek)   │
   │  3. Publiceer jointcommando's naar Gazebo PID     │
   │  4. Publiceer waterstraal-visualisatie in RViz    │
   └───────────┬──────────────────────┬────────────────┘
               │                      │
               ▼                      ▼
   /hose_pan_cmd             /hose_tilt_cmd
   (rotatie linksom/         (kantelhoek omhoog,
    rechtsom, 360°)           0.10 - 1.57 rad)
               │                      │
               ▼                      ▼
   ┌───────────────────────────────────────────────────┐
   │         Gazebo JointPositionController (PID)      │
   │   Stuurt de joint fysiek naar de gevraagde hoek   │
   └───────────────────────────────────────────────────┘
```

---

## Mechanisch ontwerp in Gazebo <a name="mechanisch-ontwerp"></a>

De turret bestaat uit twee joints in `tonk.sdf`:

| Joint            | Type      | As          | Bereik           | Functie                    |
|------------------|-----------|-------------|------------------|----------------------------|
| `hose_pan_joint` | revolute  | Z-as (omhoog) | −π tot +π        | Draait de turret rondom (360°) |
| `hose_tilt_joint`| revolute  | −Y-as       | 0.05 - 1.57 rad  | Kantelt de nozzle omhoog (0° - 90°) |

De tiltas heeft richting `<xyz>0 -1 0</xyz>` (negatieve Y-as). Dit zorgt ervoor dat een positieve hoekwaarde de nozzle **omhoog** kantelt (rechtse-handregel). Met een positieve Y-as zou de nozzle naar beneden hangen.

```
         90° (omhoog)
          │
          │  ← nozzle
    ──────┼──────  0° (horizon) ← minimumgrens is 0.05 rad (~3°)
          │
     (niet toegestaan: < 0°)
```

Elke joint heeft een eigen `JointPositionController` plugin in Gazebo die via PID de joint naar de doelhoek drijft (Open Robotics, 2024a). De PID-versterking is ingesteld op `p_gain=3.0`.

---

## Ballistische hoekberekening <a name="ballistiek"></a>

### Probleemstelling

De nozzle staat op hoogte `h₀ = 0.82 m` boven de grond en op horizontale afstand `R` van het vuur. Het water moet landen op hoogte `h_doel = 0.5 m` (de basis van de vlammen). Gevraagd: de lanceerhoek θ.

### Afleiding

De bewegingsvergelijkingen voor een projectiel zonder luchtweerstand zijn (Serway & Jewett, 2018):

```
x(t) = V₀ · cos(θ) · t
z(t) = h₀ + V₀ · sin(θ) · t − ½ · g · t²
```

Op het doelmoment `t = T` geldt: `x(T) = R` en `z(T) = h_doel`.

Uit de x-vergelijking volgt `T = R / (V₀ · cos θ)`. Na invullen in de z-vergelijking en substitutie `u = tan θ` ontstaat een kwadratische vergelijking:

```
A · u² − R · u + (A + ΔH) = 0

waarbij:
  A  = g · R² / (2 · V₀²)
  ΔH = h_doel − h₀        (negatief, want doel ligt lager dan nozzle)
```

De discriminant `D = R² − 4·A·(A + ΔH)` bepaalt of het doel bereikbaar is:

- `D < 0`: geen oplossing → `V₀` is te laag, fallback-hoek wordt gebruikt
- `D ≥ 0`: twee oplossingen (lage hoek = directe schoot, hoge hoek = lob)

De code kiest altijd de **lage-hoek oplossing** (realistisch voor een brandweerslang):

```cpp
double u_low  = (R - sqrt(D)) / (2 * A);   // lage hoek
double u_high = (R + sqrt(D)) / (2 * A);   // hoge hoek (lob)
double theta  = atan(u_low);               // booghoek in radialen
```

Als de lage hoek onder de horizon valt (θ < 0.05 rad), wordt de hoge hoek geprobeerd. Lukt ook dat niet, dan wordt de fallback-hoek van 0.35 rad (~20°) gebruikt.

### Ingestelde waarden

| Parameter   | Waarde   | Betekenis                                      |
|-------------|----------|------------------------------------------------|
| `V₀`        | 8.0 m/s  | Beginsnelheid waterstraal                      |
| `NOZZLE_H`  | 0.82 m   | Hoogte nozzle-tip boven grond                  |
| `NOZZLE_OFF`| 0.50 m   | Nozzle-tip offset voor robotmidden             |
| `FIRE_AIM_H`| 0.50 m   | Richtpunt op het vuur (halve vlamhoogte)       |
| `TILT_PARK` | 0.10 rad | Parkeerstand (geen vuur zichtbaar)             |
| `TILT_FALLBACK` | 0.35 rad | Noodhoek als ballistisch niet lukt        |

---

## ROS2 architectuur <a name="ros2-architectuur"></a>

De node draait op **10 Hz** via een wall-timer. Bij elke tick:

1. **Timeout-check**: Is het vuur langer dan 5 seconden niet gezien? → parkeerstand, boog-marker verwijderen.
2. **PAN berekenen**: `pan_world = atan2(dy, dx)` (richting van robot naar vuur in wereldcoördinaten). De relatieve hoek t.o.v. de robot: `pan_cmd = pan_world − robot_yaw`.
3. **TILT berekenen**: Nozzle-positie schatten, dan `ballisticTilt(R, nozzle_z)` aanroepen.
4. **Commando's publiceren**: `pan_pub_` en `tilt_pub_` sturen Float64 waarden naar de ros-gz-bridge.
5. **Boog publiceren**: `publishArc()` stuurt een LINE_STRIP marker naar RViz.

```
fireCallback()   ──→  fire_x_, fire_y_, fire_detected_ = true
odomCallback()   ──→  robot_x_, robot_y_, robot_yaw_

controlLoop() [10 Hz]:
  │
  ├── timeout?  → parkeer + DELETE marker
  ├── geen vuur of geen odom? → parkeer
  └── vuur gevonden:
        pan_cmd  = atan2(dy,dx) − robot_yaw
        tilt_cmd = ballisticTilt(R_nozzle, NOZZLE_H)
        publish pan, tilt, arc
```

### Communicatie met Gazebo via ros-gz-bridge

De `JointPositionController` in Gazebo verwacht Gazebo-berichten (`gz.msgs.Double`), niet native ROS2-berichten. De `ros_gz_bridge` vertaalt de `std_msgs/Float64` berichten automatisch (Open Robotics, 2024b):

```
/hose_pan_cmd  [std_msgs/Float64]  →  gz.msgs.Double  →  Gazebo PID
/hose_tilt_cmd [std_msgs/Float64]  →  gz.msgs.Double  →  Gazebo PID
```

Dit is geconfigureerd in `mapping.launch.py`:
```python
'/hose_pan_cmd@std_msgs/msg/Float64]gz.msgs.Double',
'/hose_tilt_cmd@std_msgs/msg/Float64]gz.msgs.Double',
```

---

## Visualisatie in RViz <a name="visualisatie"></a>

De waterstraal wordt als `LINE_STRIP` marker gepubliceerd op `/water_arc`. De boog bestaat uit 22 punten langs de exacte ballistische parabool:

```
p(t) = nozzle_pos + v⃗ · t − ½ · g · t²  (vectorvorm)
```

Hierbij is `T` de vluchttijd tot het doel: de tijd waarna `z(T) = FIRE_AIM_H`. Dit wordt opgelost via dezelfde kwadratische formule.

De lijn heeft dikte `0.07 m` en een helderblauwe kleur (`r=0, g=0.55, b=1.0, a=0.9`). De `lifetime` is 0.35 seconden, zodat de boog automatisch verdwijnt als de node stopt.

Als er geen vuur zichtbaar is, stuurt de node een `DELETE` actie om de boog te verwijderen uit RViz.

---

## Topics overzicht <a name="topics"></a>

| Topic                  | Richting | Type                              | Beschrijving                        |
|------------------------|----------|-----------------------------------|-------------------------------------|
| `/fire_marker`         | Sub      | `visualization_msgs/Marker`       | Vuurpositie (id=0 = sphere)         |
| `/odom`                | Sub      | `nav_msgs/Odometry`               | Robotpositie en oriëntatie          |
| `/hose_pan_cmd`        | Pub      | `std_msgs/Float64`                | Pan-joint doelhoek [rad]            |
| `/hose_tilt_cmd`       | Pub      | `std_msgs/Float64`                | Tilt-joint doelhoek [rad]           |
| `/water_arc`           | Pub      | `visualization_msgs/Marker`       | Ballistische boog (LINE_STRIP)      |

---

## Opstarten <a name="opstarten"></a>

De `hose_controller` wordt automatisch gestart via het launch-bestand:

```bash
# In de Docker container (gg):
cd /workspace
source install/setup.bash
ros2 launch tonk_mapping mapping.launch.py
```

Handmatig starten (voor debuggen):
```bash
ros2 run tonk_mapping hose_controller
```

Debug-output bekijken (pan/tilt/afstand elke 2 seconden):
```bash
ros2 topic echo /hose_pan_cmd
ros2 topic echo /hose_tilt_cmd
```

---

## Bronnen <a name="bronnen"></a>

Open Robotics. (2024a). *Gazebo Harmonic: Joint position controller*. Gazebo Sim. https://gazebosim.org/api/sim/8/classignition_1_1gazebo_1_1systems_1_1JointPositionController.html

Open Robotics. (2024b). *ros_gz_bridge: ROS 2 ↔ Gazebo topic bridging*. GitHub. https://github.com/gazebosim/ros_gz/tree/ros2/ros_gz_bridge

Open Robotics. (2024c). *ROS 2 Jazzy Jalisco: rclcpp API documentation*. https://docs.ros.org/en/jazzy/

Serway, R. A., & Jewett, J. W. (2018). *Physics for scientists and engineers* (10th ed., pp. 79-102). Cengage Learning.

Åström, K. J., & Hägglund, T. (2006). *Advanced PID control* (pp. 1-34). ISA - The Instrumentation, Systems and Automation Society.
