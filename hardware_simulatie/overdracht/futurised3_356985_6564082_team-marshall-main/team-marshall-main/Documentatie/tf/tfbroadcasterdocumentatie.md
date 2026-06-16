# Technische Documentatie: TFBroadcasterNode

## 1. Systeemoverzicht

De `TFBroadcasterNode` is een lichtgewicht ROS 2-node die verantwoordelijk is voor het publiceren van de TF-transformatieboom van robot Flip. Zonder een correcte TF-boom kunnen RViz en andere navigatienodes de sensordata niet correct in de ruimte plaatsen.

De node publiceert twee soorten transformaties:

- **Dynamische transformatie** (`odom` → `base_link`): wordt bij elke odometriemeting bijgewerkt en beschrijft de actuele positie van de robot in de wereld.
- **Statische transformatie** (`base_link` → `Flip/front_block/gpu_lidar`): beschrijft de vaste montageplaats van de LiDAR-sensor ten opzichte van het robotlichaam en wordt elke seconde opnieuw gepubliceerd.

---

## 2. Architectuur & ROS 2 Interface

### Dataflow Diagram

```
/odom (Odometry)  -->  odom_callback()  -->  TransformBroadcaster
                                              (odom --> base_link, dynamisch)

timer (1.0s)      -->  publish_static_transforms()  -->  StaticTransformBroadcaster
                                                         (base_link --> gpu_lidar, statisch)
```

### ROS 2 Interfaces

**Subscriptions:**

| Topic | Type | Beschrijving |
|---|---|---|
| `/odom` | `nav_msgs/msg/Odometry` | Ontvangt de huidige positie en oriëntatie van de robot |

**TF-publicaties:**

| Van | Naar | Type | Frequentie |
|---|---|---|---|
| `odom` | `base_link` | Dynamisch | Op elke odometriemeting |
| `base_link` | `Flip/front_block/gpu_lidar` | Statisch | Elke 1.0 seconde |

---

## 3. Transformaties

### Dynamische transformatie: `odom` → `base_link`

Deze transformatie wordt gepubliceerd telkens wanneer een nieuw odometriebericht binnenkomt. De positie en rotatie worden direct overgenomen uit het bericht:

```
translation.x = msg.pose.pose.position.x
translation.y = msg.pose.pose.position.y
translation.z = 0.0
rotation      = msg.pose.pose.orientation  (quaternion)
```

**Belangrijk:** de tijdstempel wordt gezet via `self.get_clock().now()` (wandklok) in plaats van `msg.header.stamp` (berichttijdstempel). Dit voorkomt TF-fouten bij tijdsverschillen tussen de simulatie en de TF-boom.

### Statische transformatie: `base_link` → `Flip/front_block/gpu_lidar`

Deze transformatie beschrijft de montageplaats van de LiDAR-sensor ten opzichte van het zwaartepunt van de robot:

```
translation.x = 0.0
translation.y = 0.0
translation.z = 0.1   # sensor zit 10 cm boven base_link
rotation.w    = 1.0   # geen rotatie (identiteitsquaternion)
```

De statische transformatie wordt elke seconde opnieuw gepubliceerd via een timer. Hoewel een `StaticTransformBroadcaster` normaal eenmalig publiceert, zorgt de herhaaldelijke publicatie ervoor dat de transformatie beschikbaar blijft na een herstart van andere nodes.

---

## 4. Ontwerpkeuze: Wandklok vs. Simulatietijd

De node is bewust geconfigureerd **zonder** `use_sim_time`. Dit is een kritische keuze: TF-transformaties die worden gepubliceerd met simulatietijdstempels kunnen verouderd lijken ten opzichte van de wandklok van RViz of andere nodes, wat resulteert in de foutmelding:

```
TF_OLD_DATA: Ignoring data from the past
```

Door de wandklok (`get_clock().now()`) te gebruiken voor de tijdstempel van de transformaties, blijft de TF-boom altijd actueel en compatibel met alle consumers, ongeacht of `use_sim_time` elders is ingeschakeld.

---

## 5. Conclusie & Ontwerpverantwoording

De `TFBroadcasterNode` is een minimale maar essentiële schakel in de navigatiestack van Flip. Zonder deze node kunnen de LiDAR-puntenwolk, de occupancy grid en de robotpositie niet correct worden gecombineerd in RViz of door navigatienodes.

De twee centrale ontwerpkeuzes zijn:

- **Wandklok voor TF-tijdstempels:** het gebruik van `get_clock().now()` in plaats van de berichttijdstempel voorkomt TF-synchronisatieproblemen die optreden wanneer simulatietijd en systeemtijd niet gelijk lopen.

- **Periodieke heruitgave van de statische transformatie:** door de sensor-naar-robot transformatie elke seconde opnieuw te sturen blijft de TF-boom consistent na herstart van nodes, zonder dat hiervoor een aparte latch-mechanisme nodig is.