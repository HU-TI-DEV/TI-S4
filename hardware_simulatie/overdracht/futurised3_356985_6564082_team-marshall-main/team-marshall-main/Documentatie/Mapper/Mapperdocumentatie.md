# Technische Documentatie: LiDAR Mapper

## 1. Systeemoverzicht

De LiDAR Mapper is een zelfstandig Python-script ontworpen voor gebruik met de Gazebo-simulatieomgeving. Het script leest ruwe LiDAR-sensordata van een Gazebo-topic, verwerkt deze met een probabilistisch occupancy-grid algoritme, en visualiseert het resultaat real-time als een 2D-plattegrond via OpenCV. Tegelijkertijd verwerkt het optioneel odometriedata om de positie en oriëntatie van de robot bij te houden.

Het script is ontworpen als een standalone tool: er is geen ROS 2-installatie vereist. Alle communicatie met Gazebo verloopt via het commandoregelgereedschap `gz topic`, waarbij de uitvoer als JSON-datastream wordt verwerkt.

---

## 2. Architectuur & Dataflow

### Dataflow Diagram

```
gz topic /lidar  -->  lidar_callback()  -->  update_map_from_scan()  -->  log_odds[][]
                                                                               |
gz topic /odom   -->  parse_odom_json() -->  robot_x / robot_y / robot_yaw    |
                                                 (positie-correctie)           |
                                                                               v
                                            render_map()  -->  OpenCV venster
```

### Threading Model

Het script maakt gebruik van drie parallelle threads om blokkering te voorkomen:

- **Thread 1 — LiDAR subscriber:** leest continu de LiDAR-topic en roept `lidar_callback()` aan.
- **Thread 2 — Odom subscriber:** leest continu de odometrietopic en werkt de robotpositie bij.
- **Thread 3 — Hoofdthread (main):** verwerkt de OpenCV-weergave en toetsenbordinvoer met 10 Hz.

Gedeeld geheugen (`log_odds[][]`, `robot_x`, `robot_y`, `robot_yaw`) wordt beschermd door een `threading.Lock()` om race conditions te voorkomen.

---

## 3. Configuratie & Opstartprocedure

### Systeemvereisten

- Python 3
- `opencv-python` (cv2)
- `numpy`
- Gazebo met actieve simulatie en `gz`-commandoregeltools

### Opstarten

```bash
# Standaard gebruik
python3 mapper.py

# Met opslaan ingeschakeld (druk 's' in venster)
python3 mapper.py --save

# Aangepaste odometrietopic
python3 mapper.py --odom /model/MijnRobot/odometry

# Zonder odometrie (robot blijft op oorsprong)
python3 mapper.py --no-odom
```

### Commandoregelopties

| Parameter | Waarde / Beschrijving |
|---|---|
| `--lidar <topic>` | Gazebo LiDAR-topic (standaard: `/lidar`) |
| `--odom <topic>` | Gazebo odometrietopic (standaard: `/model/Flip/odometry`) |
| `--save` | Maakt opslaan mogelijk via de `s`-toets |
| `--no-odom` | Schakelt odometrie uit; robot blijft op coördinaat (0, 0) |

### Kaartconfiguratie

| Parameter | Waarde / Beschrijving |
|---|---|
| `MAP_SIZE_M` | 40.0 m — totale breedte/hoogte van de kaart in meters |
| `RESOLUTION` | 0.05 m/cel — ruimtelijke resolutie van het grid |
| `MAP_CELLS` | 800 × 800 cellen (afgeleid: `MAP_SIZE_M / RESOLUTION`) |
| `ORIGIN` | Cel (400, 400) — robot start in het midden van het grid |
| `LO_OCC` | +2.0 — log-odds opgeteld bij een 'hit'-cel |
| `LO_FREE` | −0.1 — log-odds afgetrokken per doorgaande straal |
| `LO_MAX / MIN` | +10.0 / −5.0 — begrenzing om extremen te voorkomen |

---

## 4. Het Algoritme

### Pipeline overzicht

```
gz topic JSON  -->  parse_lidar_json()  -->  update_map_from_scan()
                                               |
                                  Stap 1: Lidar-positie berekenen
                                               |
                                  Stap 2: Per straal hoek berekenen
                                               |
                                  Stap 3: Eindpunt berekenen
                                               |
                                  Stap 4: Bresenham ray-cast
                                               |
                          vrije cellen: LO_FREE  |  hit-cel: LO_OCC
```

### Stap 1: JSON-parsing (`parse_lidar_json`)

De raw uitvoer van `gz topic -e --json-output` wordt regel voor regel als JSON verwerkt. Omdat Gazebo oneindig grote waarden als de string `"Infinity"` serialiseert in plaats van als een numerieke waarde, converteert de parser elk bereik expliciet via `float()`. Velden die worden uitgelezen zijn: `angleMin`, `angleStep`, `ranges` en optioneel `worldPose`.

### Stap 2: Lidar-positiecorrectie

De LiDAR-sensor is gemonteerd 1.45 meter voor het draaipunt van het robotmodel. Omdat de odometrie de positie van het modelursprong rapporteert, wordt de werkelijke scanpositie in wereldcoördinaten berekend via:

```
scan_x = robot_x + 1.45 * cos(robot_yaw)
scan_y = robot_y + 1.45 * sin(robot_yaw)
```

### Stap 3: Ray-casting per straal

Voor elke straal `i` in de scan wordt de absolute hoek in de wereld bepaald door de robotoriëntatie (`robot_yaw`) op te tellen bij de relatieve sensorhoek:

```
angle = robot_yaw + angle_min + i * angle_increment
```

Onbepaalde waarden worden als volgt afgehandeld:

- `NaN` of waarden ≤ 0.08 m: overgeslagen (ongeldige meting).
- `inf`: afgekapt op 9.5 m zodat vrije ruimte toch gemarkeerd wordt, maar geen bezette cel.

### Stap 4: Bresenham ray-cast & occupancy update

Het eindpunt van de straal wordt omgezet naar gridcoördinaten via `world_to_grid()`. Vervolgens bepaalt het Bresenham-lijnalgoritme alle gridcellen op het pad van de sensor naar het eindpunt:

- **Vrije cellen** (alle cellen op het pad, behalve de laatste 3): `log_odds += LO_FREE`
- **Hit-cel** (eindpunt bij een echte meting): `log_odds += LO_OCC`

De log-odds waarden worden begrensd tussen `LO_MIN` (−5.0) en `LO_MAX` (+10.0). De hoge bovengrens zorgt ervoor dat muren niet snel worden gewist door doorgaande stralen, terwijl vrije ruimte geleidelijk toch kan worden bijgewerkt.

### Stap 5: Odometrie-verwerking (`parse_odom_json`)

De robotoriëntatie wordt opgeslagen als quaternion in de Gazebo-odometrieberichten. De yaw-hoek wordt herleid uit de z- en w-componenten:

```
raw_yaw  = atan2(2 * (qw * qz), 1 - 2 * (qz * qz))
robot_yaw = -raw_yaw - radians(167.7)
```

De negatie en offset van 167.7 graden compenseren het verschil in rotatieconventie tussen de odometriesensor en de LiDAR-frame, zodat de voorwaartse richting van de robot correct uitgelijnd is met de kaart.

---

## 5. Coördinatenstelsel & Gridconversie

### `world_to_grid()`

Wereldcoördinaten (in meters) worden omgezet naar gridindices. De Y-as wordt gespiegeld omdat OpenCV-beeldcoördinaten van boven naar beneden lopen, terwijl het Gazebo-wereldstelsel van onderen naar boven loopt:

```
gx = int(ORIGIN + wx / RESOLUTION)
gy = int(ORIGIN - wy / RESOLUTION)   # Y gespiegeld voor beeldcoördinaten
```

---

## 6. Visualisatie & Feedback

### Kleurcodering van de kaart

| Kleur | Betekenis |
|---|---|
| Grijs (128, 128, 128) | Onbekende cel — `log_odds` ≈ 0 (nog niet bezocht) |
| Lichtgrijs (240, 240, 240) | Vrije cel — `log_odds` < −0.1 |
| Donkergrijs (30, 30, 30) | Bezette cel — `log_odds` > +0.1 |
| Blauwe stip + pijl | Huidige positie van de LiDAR-sensor en rijrichting |

### Statusbalk

Linksonder in het venster wordt continu de status weergegeven:

```
Robot: (x, y)  yaw: <graden>deg  scan age: <seconden>s
```

Als de odometrie meer dan 0.5 seconden verouderd is, slaat het script de binnenkomende scan over en toont een waarschuwing in de terminal.

### Toetsenbordinvoer

| Toets | Functie |
|---|---|
| `s` | Sla de huidige kaart op als `map.png` (alleen actief met `--save`) |
| `r` | Reset de volledige kaart (alle log-odds terug naar 0) |
| `q` | Sluit het programma en het OpenCV-venster |

---

## 7. Conclusie & Ontwerpverantwoording

De LiDAR Mapper biedt een lichtgewicht en zelfstandige oplossing voor real-time kaartvorming in een Gazebo-simulatieomgeving. Door direct gebruik te maken van `gz topic`-uitvoer in plaats van een ROS 2-middleware, is het script eenvoudig op te starten en te debuggen zonder een volledige ROS 2-installatie.

De twee belangrijkste ontwerpkeuzes zijn:

- **Probabilistische occupancy grid met log-odds:** in plaats van een binaire bezet/vrij-kaart worden log-odds waarden bijgehouden. Dit maakt de kaart robuust tegen incidentele foute metingen en stelt het systeem in staat om muren geleidelijk te bevestigen over meerdere scans. De asymmetrie tussen `LO_OCC` (+2.0) en `LO_FREE` (−0.1) zorgt ervoor dat muren snel worden herkend, maar langzaam worden uitgewist.

- **Stabiele LiDAR-positiebepaling via odometrie:** omdat de odometrie de oorsprong van het robotmodel rapporteert en de LiDAR fysiek 1.45 meter verder gemonteerd is, wordt de werkelijke scanpositie per frame herberekend. Gecombineerd met de yaw-correctie van 167.7 graden levert dit een nauwkeurig uitgelijnde kaart op, ongeacht de oriëntatie van de robot in de simulatie.