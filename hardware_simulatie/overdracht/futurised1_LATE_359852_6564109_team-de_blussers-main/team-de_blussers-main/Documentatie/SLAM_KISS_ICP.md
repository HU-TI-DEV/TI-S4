# 3D SLAM met KISS-ICP - Tonk (Waterblus Robot)

## Inhoudsopgave
1. [Systeemoverzicht](#systeemoverzicht)
2. [Waarom SLAM? - het probleem met wiel-odometrie](#waarom-slam)
3. [Stap 1 - LiDAR voorbewerken (front-end filter)](#stap1)
4. [Stap 2 - Localisatie met KISS-ICP (scan-matching)](#stap2)
5. [Stap 3 - Persistente kaart opbouwen (map_accumulator)](#stap3)
6. [Stap 4 - Pathfinding op de SLAM-kaart](#stap4)
7. [TF-tree en frames](#tf-tree)
8. [Topics overzicht](#topics)
9. [Installatie van het `kiss_icp`-pakket](#installatie)
10. [Bouwen en draaien](#draaien)
11. [Tuning](#tuning)
12. [Bekende beperkingen](#beperkingen)
13. [Bronbestanden](#bronbestanden)
14. [Bronnen / Research](#bronnen)

---

## Systeemoverzicht <a name="systeemoverzicht"></a>

De launch `full_system.launch.py` (de complete alles-in-één launch) vervangt de
wiel-odometrie + per-frame kaart door **echte 3D LiDAR-SLAM**. In plaats van te
vertrouwen op hoeveel de wielen
gedraaid hebben, bepaalt de robot zijn positie door opeenvolgende LiDAR-scans
op elkaar te leggen (*scan-matching*). De kaart blijft daarbij staan, ook als de
robot verder rijdt.

```
┌─────────────────────────────────────────────────────────────────┐
│                          SENSOR                                 │
│                  LiDAR (360°)  /lidar/points                    │
└───────────────────────────────┬─────────────────────────────────┘
                                 ▼
                   ┌───────────────────────────┐
                   │   lidar_to_pointcloud     │  vloer/plafond/ruis filteren
                   │   → /lidar/pointcloud     │  + static TF base_link→lidar
                   └─────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                                      ▼
   ┌───────────────────────┐            ┌───────────────────────────┐
   │       KISS-ICP        │            │     map_accumulator       │
   │  scan-matching        │            │  punten → TF → 2D-grid    │
   │  → TF odom→base_link  │  ── TF ──▶ │  → PERSISTENTE /map       │
   └───────────────────────┘            └─────────────┬─────────────┘
              │ (waar ben ik?)                         │ (hoe ziet de wereld eruit?)
              └──────────────────┬─────────────────────┘
                                 ▼
                   ┌───────────────────────────┐
                   │   dijkstra_path_planner   │  use_external_map = true
                   │   leest /map + pose (TF)  │  → /cmd_vel, /path
                   └───────────────────────────┘
```

De klassieke modus blijft beschikbaar als `full_system_classic.launch.py` (planner in klassieke
modus: eigen lidar-kaart per scan + `/odom` uit wiel-odometrie).

---

## Waarom SLAM? - het probleem met wiel-odometrie <a name="waarom-slam"></a>

De klassieke navigatie (zie [autonome_navigatie.md](autonome_navigatie.md))
gebruikt **wiel-odometrie**: uit het aantal omwentelingen van de wielen schat de
robot hoe ver hij gereden is. Dat werkt, maar heeft één fundamenteel probleem:

> **Drift.** Elke meetfout (wielslip, oneffenheden, afronding) telt op. Na een
> lange rit - zeker met veel bochten in een parkeergarage - loopt de geschatte
> positie steeds verder uit de pas met de werkelijkheid. De kaart "schuift" mee.

**SLAM** (*Simultaneous Localization And Mapping*) lost dit op door de positie
niet uit de wielen, maar uit de **omgeving zelf** af te leiden: de robot herkent
muren en pilaren die hij eerder zag, en corrigeert daarmee zijn positie. Hij
bouwt tegelijk een kaart *én* lokaliseert zich daarin - vandaar de naam
[[Cadena et al., 2016]](#bronnen).

Wij gebruiken hiervoor **KISS-ICP**: een lichtgewicht, sensor-agnostische
LiDAR-odometrie die bewust minimalistisch is gehouden en toch nauwkeurig presteert
[[Vizzo et al., 2023]](#bronnen).

---

## Stap 1 - LiDAR voorbewerken (front-end filter) <a name="stap1"></a>

De ruwe LiDAR uit Gazebo (`/lidar/points`) bevat punten die de SLAM alleen maar
in de war brengen: de vloer, het plafond en ruis vlak voor de sensor. De node
`lidar_to_pointcloud` filtert die weg en publiceert het resultaat op
`/lidar/pointcloud`.

| Filter | Waarde | Reden |
|--------|--------|-------|
| `RANGE_MIN` | 0,5 m | Punten dichter dan 50 cm = ruis/eigen behuizing |
| `Z_MIN` | −0,75 m | Vloer-hits weggooien (LiDAR staat op 0,8 m hoogte) |
| `Z_MAX` | +1,2 m | Plafond / volgende verdieping weggooien |

De Z-waarden zijn in het **sensor-frame**: de LiDAR zit 0,8 m boven het rijvlak,
dus de vloer ligt op z ≈ −0,8 m.

Daarnaast zendt deze node een **statische transform** uit van `base_link` naar
`lidar` (0,8 m omhoog). Zo weet de rest van het systeem precies waar de sensor
op de robot zit.

```
base_link ──(z = +0,8 m)──▶ lidar
```

---

## Stap 2 - Localisatie met KISS-ICP (scan-matching) <a name="stap2"></a>

KISS-ICP neemt elke nieuwe puntenwolk en zoekt de verschuiving + rotatie waarmee
die het best op de **vorige scans** past. Die verschuiving *is* de beweging van de
robot. Het algoritme publiceert het resultaat als TF `odom → base_link`.

De naam staat voor **K**eep **I**t **S**mall and **S**imple. De auteurs laten zien
dat klassieke **point-to-point ICP** verrassend goed werkt zonder zware extra's,
mits je vier eenvoudige onderdelen goed doet [[Vizzo et al., 2023]](#bronnen):

**1. Bewegingscompensatie (deskewing)**
Een draaiende LiDAR meet niet alle punten op hetzelfde moment; tijdens een scan
beweegt de robot al. KISS-ICP kan dit corrigeren met per-punt-tijdstempels.

> ⚠️ In onze simulatie staat dit **uit** (`data.deskew = false`): de Gazebo-cloud
> heeft geen per-punt timestamps, dus er valt niets te corrigeren.

**2. Voxel-subsampling**
De puntenwolk wordt opgedeeld in een 3D-raster van kubusjes (*voxels*) en per
voxel blijft één punt over. Dat maakt de matching veel sneller en robuuster tegen
verschillen in puntdichtheid. Dit is een standaardtechniek uit de
puntenwolk-verwerking [[Rusu & Cousins, 2011]](#bronnen).

**3. Point-to-point ICP met robuuste kernel**
ICP (*Iterative Closest Point*, [[Besl & McKay, 1992]](#bronnen)) herhaalt twee
stappen tot convergentie:

```
1. KOPPEL    elk scanpunt aan zijn dichtstbijzijnde buur in de bestaande kaart
2. VERSCHUIF zoek de transformatie die de afstand over alle koppels minimaliseert
   ↺ herhaal tot de verschuiving klein genoeg is
```

Een **robuuste kernel** zorgt dat uitschieters (een fout gekoppeld punt) de
oplossing niet domineren.

**4. Adaptieve drempel + constante-snelheidsmodel**
Welke koppels in stap 1 mogen meedoen, hangt af van een afstandsdrempel. KISS-ICP
schat die drempel **adaptief** uit hoeveel de robot net bewogen heeft - geen
handmatig getune per omgeving. Als startgok voor de ICP gebruikt het een
**constante-snelheidsmodel**: "neem aan dat de robot net zo doorbeweegt als bij
de vorige stap".

Het netto resultaat: een goede positie-schatting zonder dat we wiel-odometrie of
een IMU nodig hebben.

---

## Stap 3 - Persistente kaart opbouwen (map_accumulator) <a name="stap3"></a>

Waar de klassieke planner elke scan een **nieuwe** kaart bouwde en die meteen weer
wiste, **accumuleert** `map_accumulator` de kaart over de tijd. Hij abonneert op
`/lidar/pointcloud` en doet per binnenkomende wolk:

1. **Transformeren** - haal via TF de transform op van het globale frame (`odom`,
   geleverd door KISS-ICP) naar het sensor-frame, en zet elk punt om naar
   wereldcoördinaten. *Hierdoor blijven de punten stil staan in de wereld terwijl
   de robot rijdt.* Loopt de SLAM-TF even achter, dan valt de node terug op de
   laatst bekende transform.
2. **Hoogte-filter** - gooi punten weg onder `z_min` (0,1 m, vloer) of boven
   `z_max` (2,5 m, plafond), nu gemeten in het **globale** frame.
3. **Projecteren** - reken het punt om naar een cel in een 2D-raster en markeer die
   als bezet (`100`).

De kaart wordt elke **500 ms** gepubliceerd op `/map`.

| Gridparameter | Waarde | Toelichting |
|---------------|--------|-------------|
| Resolutie | 0,2 m/cel | Nauwkeurigheid van de kaart |
| Breedte | 450 cellen | 90 m horizontaal |
| Hoogte | 300 cellen | 60 m verticaal |
| Oorsprong | (−45, −30) | Linksonder in het `odom`-frame |
| `z_min` / `z_max` | 0,1 m / 2,5 m | Vloer- en plafondfilter (globaal frame) |

De grid wordt **ruw** gepubliceerd (alleen 0 = vrij, 100 = obstakel). De
obstakel-inflatie gebeurt bewust pas in de planner, zodat *mapping* en *planning*
gescheiden blijven en los te tunen zijn.

---

## Stap 4 - Pathfinding op de SLAM-kaart <a name="stap4"></a>

De `dijkstra_path_planner` draait in deze modus met `use_external_map = true`:

- Hij **bouwt zelf geen kaart** meer, maar leest de persistente `/map`.
- Zijn eigen positie haalt hij uit **TF** (`odom → base_link`), niet uit `/odom`.
- De rest - obstakel-inflatie, Dijkstra-zoektocht, P-regelaar voor het volgen van
  waypoints - is identiek aan de klassieke modus. Zie
  [dijkstra_pathfinding.md](dijkstra_pathfinding.md) voor de details van het
  algoritme.

### De inflatie-costmap (de "heatmap")

De ruwe `/map` is binair (0 = vrij, 100 = bezet). Voordat Dijkstra zoekt, vergroot
de planner elk obstakel met `inflateObstacles()` tot een **costmap met
kostgradient** - de heatmap die je als kleuroverloop rond muren ziet:

| Zone | Afstand tot obstakel | Celwaarde | Betekenis |
|------|----------------------|-----------|-----------|
| **Hard** | 0 - 2,0 m (`INFLATE_RADIUS`) | `100` | Onpasseerbaar (robot is 1,6 m breed) |
| **Zacht** | 2,0 - 2,6 m (`+ COST_RADIUS` 0,6 m) | `90 → 5` | Passeerbaar maar duur: hoe dichterbij, hoe duurder |
| **Vrij** | verder weg | `0` | Vrij rijden |

```
Obstakel:  ████
Hard:      ░░░░████████          (2,0 m, waarde 100, onpasseerbaar)
Zacht:     ▒▒▒▒░░░░████████      (nog 0,6 m, waarde 90→5, duurder)
                ↑ heatmap-gradient (kleuroverloop in RViz)
```

Dijkstra telt deze celkost bij de afstandskost op, waardoor de route **vanzelf
ruim om muren en pilaren** buigt in plaats van er rakelings langs.

> ⚠️ **SLAM-specifiek:** de planner gebruikt deze heatmap intern voor het plannen,
> maar **publiceert hem niet** in SLAM-modus - `/map` is en blijft de ruwe kaart
> van de `map_accumulator`. In de klassieke `full_system`-modus is de geïnflateerde
> heatmap juist *wél* de zichtbare `/map`. In RViz zie je onder SLAM dus zwart-witte
> muren; de kostgradient bestaat alleen in het geheugen van de planner.

Zo profiteert de bestaande navigatie automatisch van de driftvrije SLAM-positie
en de opgebouwde kaart.

---

## TF-tree en frames <a name="tf-tree"></a>

```
map ──(identity)──▶ odom ──(KISS-ICP)──▶ base_link ──(static, +0,8 m)──▶ lidar
```

| Transform | Bron | Betekenis |
|-----------|------|-----------|
| `map → odom` | `static_transform_publisher` (identity) | Conventioneel net frame bovenaan de tree |
| `odom → base_link` | **KISS-ICP** | De daadwerkelijke localisatie (scan-matching) |
| `base_link → lidar` | `lidar_to_pointcloud` (static) | Sensorpositie op de robot |

> De `map → odom` transform is hier de **identiteit** (alles op 0). In een SLAM
> *mét* loop-closure zou juist deze transform de globale correctie dragen op het
> moment dat de robot een eerder bezochte plek herkent. KISS-ICP heeft geen
> loop-closure, dus blijft die correctie nul - zie [Beperkingen](#beperkingen).

---

## Topics overzicht <a name="topics"></a>

| Topic | Richting | Type | Inhoud |
|-------|----------|------|--------|
| `/lidar/points` | ← input (Gazebo) | `sensor_msgs/PointCloud2` | Ruwe LiDAR uit de simulatie |
| `/lidar/pointcloud` | ↔ intern | `sensor_msgs/PointCloud2` | Gefilterde LiDAR (frame `lidar`) |
| `/kiss/local_map` | → output | `sensor_msgs/PointCloud2` | KISS-ICP's eigen 3D-kaart (RViz) |
| `/map` | → output | `nav_msgs/OccupancyGrid` | Persistente 2D-kaart (frame `odom`) |
| `/path` | → output | `nav_msgs/Path` | Geplande route (RViz) |
| `/cmd_vel` | → output | `geometry_msgs/Twist` | Rijcommando's naar DiffDrive |
| `/person_marker` | → output | `visualization_msgs/Marker` | Gedetecteerde persoon (RViz) |
| `/tf` | ↔ | `tf2_msgs/TFMessage` | `map → odom → base_link → lidar` |

> Naast de SLAM-keten start `full_system.launch.py` ook de `fire_navigator`
> (vuurdetectie via de thermische camera), de `hose_controller` (blusslang-turret)
> en de `person_detector` (YOLO-persoonsdetectie op `/camera/image_raw`, marker op
> `/person_marker`). Die staan los van de SLAM maar
> draaien in dezelfde launch mee; zie [autonome_navigatie.md](autonome_navigatie.md)
> voor de vuurdetectie.

---

## Installatie van het `kiss_icp`-pakket <a name="installatie"></a>

De SLAM-integratiecode (`map_accumulator`, de planner-aanpassing en
`full_system.launch.py`) zit in `tonk_mapping` en komt via git mee. Alleen het externe
**`kiss_icp` ROS 2-pakket** moet per omgeving aanwezig zijn op het ROS-pad.

### Docker / Ubuntu-teamgenoten (automatisch, from source)

> ⚠️ **Er is GEEN `ros-jazzy-kiss-icp` apt-pakket** - KISS-ICP zit niet in de
> Jazzy rosdistro. Het wordt daarom (ook in Docker) from source gebouwd.

Dit is geregeld via `postCreateCommand` → `.devcontainer/setup-kiss-icp.sh`, dat na
een **"Dev Containers: Rebuild Container"** automatisch draait. Dat script:

1. cloned `kiss-icp` naar een container-lokale workspace `~/kiss_icp_ws`
   (bewust **buiten** de `/workspace` bind-mount → snelle build, schone repo);
2. bouwt het pakket met `colcon build --packages-select kiss_icp`;
3. voegt `source ~/kiss_icp_ws/install/setup.bash` toe aan `~/.bashrc`.

Open daarna een **nieuwe** terminal (zodat de overlay gesourcet wordt) en launch.
Op Ubuntu-jazzy is de tf2-patch hieronder **niet** nodig. Handmatig opnieuw
draaien kan altijd met `bash .devcontainer/setup-kiss-icp.sh`.

### Native (Arch / Eden)

KISS-ICP is niet gepackaged voor Arch, dus from source in de workspace:

```bash
cd ~/ros2_ws/src
git clone --depth 1 https://github.com/PRBonn/kiss-icp.git
cd ~/ros2_ws
colcon build --packages-select kiss_icp --cmake-args -DCMAKE_BUILD_TYPE=Release
```

KISS-ICP fetcht zelf zijn deps (Eigen 3.4.0, Sophus, robin-map); systeem-`tbb`
wordt gebruikt. Het systeem-Eigen (5.x) wordt zo niet geraakt.

> ⚠️ **Patch nodig op oudere ROS-snapshots** (zoals de AUR `ros2-jazzy` van Eden):
> die heeft nog `tf2_ros/*.h` i.p.v. `*.hpp`. De build faalt dan op
> `fatal error: tf2_ros/buffer.hpp`. Fix:
> ```bash
> cd ~/ros2_ws/src/kiss-icp/ros/src
> sed -i -E 's|<tf2_ros/([a-z_]+)\.hpp>|<tf2_ros/\1.h>|g' OdometryServer.hpp OdometryServer.cpp
> ```
> Daarna opnieuw `colcon build`. (Op Ubuntu-jazzy is dit níet nodig.)

---

## Bouwen en draaien <a name="draaien"></a>

```bash
cd ~/ros2_ws
colcon build --packages-select tonk_mapping
source install/setup.zsh        # of setup.bash
ros2 launch tonk_mapping full_system.launch.py
```

### In RViz
- **Fixed Frame**: `map`
- **Map** op `/map` → loopt vol met muren terwijl de robot rijdt (blijft staan!)
- **TF** → keten `map → odom → base_link → lidar`
- **PointCloud2** op `/kiss/local_map` → KISS-ICP's eigen 3D-kaart

### Debuggen

```bash
# Komt er TF uit KISS-ICP?
ros2 run tf2_ros tf2_echo odom base_link

# Wordt de kaart opgebouwd?
ros2 topic echo /map --no-arr | grep -E "width|height|resolution"

# Stop de robot direct
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}"
```

---

## Tuning <a name="tuning"></a>

### KISS-ICP (in `full_system.launch.py`, node `kiss_icp_node`)

| Parameter | Waarde | Effect |
|-----------|--------|--------|
| `data.max_range` | 40 m | Max LiDAR-bereik (= sensor-limiet `<range><max>`) |
| `data.min_range` | 0,5 m | Punten dichterbij negeren |
| `data.deskew` | `false` | Auto uit: sim-cloud heeft geen per-punt timestamps |
| `mapping.voxel_size` | `max_range/100` | Kleiner = gedetailleerder maar zwaarder |
| `lidar_odom_frame` | `odom` | Moet gelijk zijn aan `global_frame` van de accumulator |

### map_accumulator

| Parameter | Waarde | Effect |
|-----------|--------|--------|
| `global_frame` | `odom` | **Moet** gelijk zijn aan KISS-ICP's `lidar_odom_frame` |
| `z_min` / `z_max` | 0,1 / 2,5 m | Vloer- en plafondfilter |
| `resolution` / `width` / `height` | 0,2 / 450 / 300 | Kaartgrootte (90×60 m) |

---

## Bekende beperkingen <a name="beperkingen"></a>

| Beperking | Uitleg | Mogelijke verbetering |
|-----------|--------|-----------------------|
| Geen loop-closure | KISS-ICP is LiDAR-**odometrie**: het herkent geen eerder bezochte plek. Bij rondjes in de garage kan de kaart op den duur licht "uitsmeren" | **RTAB-Map** met loop-closure [[Labbé & Michaud, 2019]](#bronnen) |
| Geen deskewing in sim | Gazebo-cloud heeft geen per-punt timestamps; bij snelle bewegingen kan dit ICP licht storen | Per-punt timestamps publiceren vanuit de sim |
| Statische `map → odom` | Zonder loop-closure blijft deze identiteit; globale fouten worden niet gecorrigeerd | Volgt automatisch uit een SLAM met back-end |
| Geen dynamische obstakels | Bewegende objecten worden permanent in de kaart gebrand | Kostmap met decay / tijdsfilter |

**Vervolg:** voor een globaal consistente kaart + loop-closure is **RTAB-Map** de
logische volgende stap (`apt install ros-jazzy-rtabmap-ros` op Ubuntu; op Arch
eerst PCL/GTSAM/g2o + rtabmap-core from source, en de protobuf-pin opheffen - zie
issues vanuit 2026-06-15, vgl. [[arch_pacman_gz_soname_break]]).

---

## Bronbestanden <a name="bronbestanden"></a>

| Bestand | Beschrijving |
|---------|-------------|
| `ros2/tonk_mapping/launch/full_system.launch.py` | Complete launch (KISS-ICP + accumulator + planner + vuur + slang + persoon) |
| `ros2/tonk_mapping/src/lidar_to_pointcloud.cc` | Front-end filter + static TF `base_link→lidar` |
| `ros2/tonk_mapping/src/map_accumulator.cc` | Persistente 2D-kaart uit de SLAM-cloud |
| `ros2/tonk_mapping/src/dijkstra_path_planner.cc` | Pathfinding (`use_external_map`-modus) |
| `ros2/tonk_mapping/rviz/mapping.rviz` | RViz-visualisatie-instellingen |
| extern: `kiss_icp` | Scan-matching / LiDAR-odometrie ([PRBonn/kiss-icp](https://github.com/PRBonn/kiss-icp)) |

---

## Bronnen / Research <a name="bronnen"></a>

1. **KISS-ICP** - I. Vizzo, T. Guadagnino, B. Mersch, L. Wiesmann, J. Behley en
   C. Stachniss, *"KISS-ICP: In Defense of Point-to-Point ICP - Simple, Accurate,
   and Robust Registration If Done the Right Way,"* IEEE Robotics and Automation
   Letters (RA-L), vol. 8, nr. 2, pp. 1029-1036, 2023.
   doi: [10.1109/LRA.2023.3236571](https://doi.org/10.1109/LRA.2023.3236571) ·
   [PDF (Uni Bonn)](https://www.ipb.uni-bonn.de/pdfs/vizzo2023ral.pdf) ·
   [code](https://github.com/PRBonn/kiss-icp)
   *De methode die wij gebruiken voor de localisatie.*

2. **ICP (origineel)** - P. J. Besl en N. D. McKay, *"A Method for Registration of
   3-D Shapes,"* IEEE Transactions on Pattern Analysis and Machine Intelligence
   (TPAMI), vol. 14, nr. 2, pp. 239-256, 1992.
   doi: [10.1109/34.121791](https://doi.org/10.1109/34.121791)
   *Het Iterative-Closest-Point-algoritme waar KISS-ICP op voortbouwt.*

3. **SLAM-overzicht** - C. Cadena, L. Carlone, H. Carrillo, Y. Latif,
   D. Scaramuzza, J. Neira, I. Reid en J. J. Leonard, *"Past, Present, and Future
   of Simultaneous Localization and Mapping: Toward the Robust-Perception Age,"*
   IEEE Transactions on Robotics, vol. 32, nr. 6, pp. 1309-1332, 2016.
   doi: [10.1109/TRO.2016.2624754](https://doi.org/10.1109/TRO.2016.2624754)
   *Achtergrond bij wat SLAM is en waarom drift een probleem is.*

4. **RTAB-Map** - M. Labbé en F. Michaud, *"RTAB-Map as an Open-Source Lidar and
   Visual Simultaneous Localization and Mapping Library for Large-Scale and
   Long-Term Online Operation,"* Journal of Field Robotics, vol. 36, nr. 2,
   pp. 416-446, 2019.
   doi: [10.1002/rob.21831](https://doi.org/10.1002/rob.21831)
   *Het voorgestelde vervolg met loop-closure.*

5. **Voxel-/puntenwolkverwerking** - R. B. Rusu en S. Cousins, *"3D is here: Point
   Cloud Library (PCL),"* IEEE International Conference on Robotics and Automation
   (ICRA), 2011.
   doi: [10.1109/ICRA.2011.5980567](https://doi.org/10.1109/ICRA.2011.5980567)
   *Achtergrond bij voxel-subsampling van puntenwolken.*

6. **ROS 2** - S. Macenski, T. Foote, B. Gerkey, C. Lalancette en W. Woodall,
   *"Robot Operating System 2: Design, architecture, and uses in the wild,"*
   Science Robotics, vol. 7, nr. 66, 2022.
   doi: [10.1126/scirobotics.abm6074](https://doi.org/10.1126/scirobotics.abm6074)
   *Het framework waarin alle nodes draaien.*
</content>
</invoke>
