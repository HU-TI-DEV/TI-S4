# Technische Documentatie: `botsing_detectie.cc` — Veiligheidsfilter (Botsingdetectie)

## 1. Doel van de node
`botsing_detectie` is een **gz-transport programma in C++** dat als
**veiligheidsfilter** tussen de pathfinding en de robot **Flip** zit. De pathfinding
([`explorer.py`](Explorer_Navigatie_Documentatie.md)) blijft gewoon rijden; deze node
**remt alleen af** wanneer de lidar ziet dat de robot ergens tegenaan zou rijden.

Concreet:

1. Hij leest continu de **lidar** en bepaalt of er een obstakel **vóór** of **achter**
   de robot zit (binnen instelbare marges).
2. Hij vangt het rijcommando van de pathfinding op (`/cmd_vel_nav`), en geeft dat
   **ongewijzigd door** naar de robot (`/cmd_vel`)…
3. …**behalve** als de robot een richting op wil waar een obstakel zit: dan zet hij de
   **lineaire snelheid op 0** (remmen), maar **laat hij het draaien wél door** — zo kan
   de pathfinding nog om het obstakel heen sturen.

> **Kernidee (veto-patroon):** de botsingdetectie *bedenkt zelf geen route*. Hij heeft
> alleen een vetorecht op "vooruit/achteruit" als dat onveilig is. De intelligentie
> blijft bij de pathfinding; dit is puur een vangnet.

### In/uit (topics)
Let op: dit zijn **Gazebo-topics** (gz-transport), niet de ROS-topics. De koppeling
met ROS loopt via de `ros_gz_bridge` (zie [§2](#2-architectuur--keuzeonderbouwing)).

| Richting | gz-topic | Type | Wat |
|---|---|---|---|
| In | `/lidar` | `gz.msgs.LaserScan` | Lidar van Gazebo, voor obstakeldetectie |
| In | `/cmd_vel_nav` | `gz.msgs.Twist` | Gewenste snelheid van de pathfinding |
| Uit | `/cmd_vel` | `gz.msgs.Twist` | Veilig (eventueel afgeremd) commando → robot |

## 2. Architectuur & keuzeonderbouwing

### Waarom een aparte C++ node en niet in `explorer.py`?
De botsingdetectie was er al als losstaand **gz-transport** programma (oorspronkelijk een
keyboard-teleop met lidar-beveiliging). In plaats van die logica over te schrijven naar
Python/ROS, hergebruiken we hem **as-is** en schuiven we hem als filter in de keten. Zo
blijft bestaande, geteste code intact en hoeft de pathfinding niets van remmen te weten.

### De keten (waar zit de filter?)
De truc zit in de bridge-configuratie: de pathfinding publiceert "gewoon" naar ROS
`/cmd_vel`, maar de bridge stuurt dat **niet** rechtstreeks naar de robot. Het gaat eerst
door de filter heen:

```
explorer.py
   │  publiceert ROS /cmd_vel
   ▼
ros_gz_bridge  ──(ROS /cmd_vel  →  gz /cmd_vel_nav)──►  botsing_detectie
                                                            │  filtert / remt
   Gazebo-lidar ──(gz /lidar)──────────────────────────────┤
                                                            ▼
                                              gz /cmd_vel  ►  robot Flip (Gazebo)
```

Zonder de filter zou de pathfinding direct op `/cmd_vel` rijden. Door in
[`bridge.yaml`](../../src/Futurised/bridge.yaml) het doel om te zetten naar
`/cmd_vel_nav`, dwingen we elk rijcommando **eerst** langs de botsingdetectie. Die is dus
de **enige** schrijver van het echte `/cmd_vel`.

### Waarom "draaien altijd doorlaten"?
Als we bij een obstakel **alles** zouden blokkeren (ook draaien), staat de robot stil en
kan de pathfinding niet wegsturen → hij zit muurvast. Door alleen de **lineaire** as te
vetoën en het **draaien** door te laten, kan de robot ter plekke wegdraaien van het blok
en daarna weer vooruit. Het is een rem, geen handrem.

## 3. Code-documentatie

### 3.1 Parameters (bovenin het bestand)
| Parameter | Waarde | Betekenis |
|---|---|---|
| `LIMIT_FRONT` | `1.0` m | Obstakel binnen deze afstand **vóór** → remmen bij vooruit rijden. |
| `LIMIT_REAR` | `3.0` m | Obstakel binnen deze afstand **achter** → remmen bij achteruit rijden. |

> De achter-marge is ruimer omdat de robot achteruit "blind" is en lang is (1.55 m):
> liever vroeg remmen dan de achterkant ergens intikken.

### 3.2 `lidarCallback(LaserScan)` — obstakeldetectie
Wordt elke lidar-scan aangeroepen. Hij loopt door alle metingen (`ranges`) en verdeelt
ze in **sectoren op basis van de array-index**:

- **Vóór** = het midden van de array (index ≈ `0.4·N` t/m `0.6·N`).
- **Achter** = begin én eind van de array (index `< 0.15·N` of `> 0.85·N`).

Per sector houdt hij de **dichtstbijzijnde afstand** bij. Staat die onder de limiet, dan
gaat de bijbehorende vlag aan:

```cpp
front_blocked = danger_front;   // iets binnen LIMIT_FRONT vóór de robot
rear_blocked  = danger_rear;    // iets binnen LIMIT_REAR achter de robot
```

Metingen `< 0.05 m` worden genegeerd (ruis / de robot zelf).

**Debug-uitvoer** (toegevoegd om te kunnen zien dát hij leeft):
- Elke ~20 scans een **heartbeat**: `[status] lidar voor=…m achter=…m`.
- Een **randmelding** zodra een sector van vrij→geblokkeerd (of omgekeerd) wisselt:
  `>> LIDAR: obstakel VOOR gedetecteerd (< 1.0m)` / `   LIDAR: voor weer vrij`.

> De **sector-indexering** gaat ervan uit dat index 0 achter ligt en het midden vóór.
> Klopt dat niet met de oriëntatie van jullie lidar, dan moeten alleen de
> index-grenzen in deze functie worden bijgesteld — de rest van de logica blijft gelijk.

### 3.3 `cmdVelNavCallback(Twist)` — het filter zelf
Het hart van de integratie. Voor elk pathfinding-commando:

1. **Draaien** (`angular.z`) → altijd ongewijzigd doorgeven.
2. **Vooruit** (`linear.x > 0`) én `front_blocked` → `linear.x = 0` (remmen).
3. **Achteruit** (`linear.x < 0`) én `rear_blocked` → `linear.x = 0` (remmen).
4. Anders → de pathfinding-snelheid ongewijzigd doorgeven.
5. Publiceer het resultaat op `/cmd_vel`.

```cpp
out.mutable_angular()->set_z(ang);            // draaien altijd doorlaten
if      (lin > 0.0 && front_blocked) out.mutable_linear()->set_x(0.0);  // rem vooruit
else if (lin < 0.0 && rear_blocked)  out.mutable_linear()->set_x(0.0);  // rem achteruit
else                                 out.mutable_linear()->set_x(lin);  // vrij baan
```

Een **randmelding** print het begin en einde van een noodstop (niet elke 0.1 s spammen):
`########## NOODSTOP: botsingdetectie REMT de pathfinding af! ##########` en
`---------- Vrij baan: pathfinding rijdt weer door. ----------`.

### 3.4 `main()` — twee modi
| Start | Modus | Gedrag |
|---|---|---|
| *(geen argument)* | **Veiligheidsfilter** (standaard) | Abonneert op `/lidar` + `/cmd_vel_nav`, filtert, en wacht (`waitForShutdown()`). Dit is hoe de launch hem start. |
| `--teleop` | **Handmatige besturing** | Keyboard-teleop (W/S/A/D/spatie/Q) met dezelfde lidar-beveiliging. Voor losse tests. |

De filter-modus is bewust de **standaard**, omdat de node onder `ros2 launch` draait
(geen terminal/TTY). De oude teleop-modus las van het toetsenbord en gaf onder de launch
fouten (`tcsetattr: Inappropriate ioctl`); daarom is teleop nu opt-in via een argument.

### 3.5 Plek in de launch
In [`launch.py`](../../src/Futurised/launch.py) start het binary als `ExecuteProcess`
met een `TimerAction` (na ~8 s, zodat Gazebo en de bridge al draaien):

```python
botsing_detectie = TimerAction(period=8.0, actions=[ExecuteProcess(
    cmd=['/workspace/src/RobotFlip_cc/build/botsing_detectie'],
    output='screen')])
```

## 4. Bouwen & draaien

Het binary moet **vóór het launchen gebouwd zijn** (de launch start het binary, hij
compileert het niet). Bouwen in de container:

```bash
cd /workspace/src/RobotFlip_cc && cmake --build build
```

Controleer dat de laatste code echt in het binary zit (anders draai je een oude build —
zie *Problemen & Fixes #3*):

```bash
strings build/botsing_detectie | grep -c "status] lidar"   # moet ≥ 1 zijn
```

Daarna start alles via het normale opstartscript ([`run_flip.sh`](../../src/Futurised/run_flip.sh)).
In de log hoor je dan o.a.:

```
[botsing_detectie-4] Limiet VOOR: 1m | Limiet ACHTER: 3m
[botsing_detectie-4] Veiligheidsfilter actief: pathfinding rijdt, ik rem bij obstakels.
[botsing_detectie-4] [status] lidar  voor=2.3m  achter=1.1m   (rem voor<1m, achter<3m)
```

### Diagnose-commando's (gz-transport)
Werkt de keten? Draai dit in een tweede terminal terwijl de sim loopt:

```bash
gz topic -i -t /lidar      # publisher = Gazebo, subscribers = bridge + botsing_detectie
gz topic -i -t /cmd_vel    # publisher = botsing_detectie, subscriber = de robot (Gazebo)
gz topic -l | grep -i lidar # exacte topicnaam controleren
```

Staat botsing_detectie als subscriber bij `/lidar` én als publisher bij `/cmd_vel`, dan
is de bedrading correct.

## 5. Problemen & Fixes (de weg naar werkend)

> Net als bij de pathfinding: elk probleem was zichtbaar gedrag met een concrete oorzaak.

**#1 — De robot reed niet (na de eerste integratie).**
Het oude binary draaide nog (niet herbouwd) én startte in keyboard-teleop-modus, die
onder `ros2 launch` faalde met `tcsetattr: Inappropriate ioctl` omdat er geen terminal
is. **Fix:** filter-modus als standaard, teleop alleen via `--teleop`; en herbouwen.

**#2 — Conflict om `/cmd_vel`.**
Als zowel de pathfinding als de filter rechtstreeks naar `/cmd_vel` schrijven, vechten ze
om de besturing. **Fix:** de bridge stuurt de pathfinding naar `/cmd_vel_nav`; de filter
is de **enige** schrijver van `/cmd_vel`.

**#3 — Geen enkele debug-melding, terwijl de robot wél reed.**
Symptoom: `Veiligheidsfilter actief` verscheen, de robot bewoog, maar er kwam geen
enkele `[status] lidar`- of `NOODSTOP`-regel. Met `gz topic -i -t /lidar` bleek de
subscription wél correct verbonden — dus de bedrading klopte. De oorzaak was simpel: het
**draaiende binary was een oude build** zónder de heartbeat/debug-code
(`strings … | grep "status] lidar"` gaf `0`). **Fix:** opnieuw bouwen met
`cmake --build build`, daarna verscheen alles. **Les:** de launch compileert niet — na
elke codewijziging eerst herbouwen en met `strings` verifiëren.

**#4 — Onzekerheid of de detectie écht werkte.**
Omdat de robot zelden ergens tegenaan reed, was niet te zien of de rem ooit afging.
**Fix:** een **heartbeat** (elke ~20 scans de gemeten voor/achter-afstand) plus
**randmeldingen** bij elke vrij↔geblokkeerd-wissel en bij elke noodstop. Zo zie je live
wat de lidar meet en wanneer er geremd wordt.

## 6. Bekende beperkingen / vervolg
- De **sector-indexering** in `lidarCallback` is afgestemd op de aanname dat het midden
  van de lidar-array recht vooruit kijkt. Wijkt dat af, dan moeten alleen de index-grenzen
  worden bijgesteld.
- De filter remt **hard** (snelheid → 0) i.p.v. geleidelijk afremmen. Voor de demo is dat
  voldoende; soepeler zou kunnen door de snelheid evenredig met de afstand te schalen.
- De marges (`LIMIT_FRONT` / `LIMIT_REAR`) zijn vaste waarden; ze houden geen rekening met
  de actuele rijsnelheid. Bij hogere snelheden zou een grotere remafstand veiliger zijn.
- De pathfinding ([`explorer.py`](Explorer_Navigatie_Documentatie.md)) heeft daarnaast
  zijn **eigen** lidar-uitwijking. Deze filter is een extra vangnet daar bovenop, geen
  vervanging.
