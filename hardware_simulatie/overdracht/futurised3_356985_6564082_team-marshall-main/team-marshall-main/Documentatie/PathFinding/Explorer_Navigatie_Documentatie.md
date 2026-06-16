# Technische Documentatie: `explorer.py` — A\* Navigatie & Verkenning

## 1. Doel van de node
`explorer.py` laat de robot **Flip** zelfstandig een gebouw verkennen met het
**A\*-algoritme**:

1. Hij bouwt uit de SLAM-kaart (`/map`) een **costmap** (waar mag het midden van de
   robot komen, en hoe "duur" is het om vlak langs een muur te rijden).
2. Hij kiest automatisch een **opening naar onontdekt gebied** (een frontier — meestal
   een deuropening naar de volgende kamer). Je kunt ook **zelf een doel klikken** in
   RViz met de *2D Nav Goal*-knop.
3. Hij plant met **A\*** een pad daarheen en **tekent dat pad als groene lijn** in RViz
   (`nav_msgs/Path` op `/planned_path`).
4. Hij **volgt** het pad (pure pursuit) en **wijkt uit** voor obstakels via de lidar.

### In/uit (topics)
| Richting | Topic | Type | Wat |
|---|---|---|---|
| In | `/map` | `OccupancyGrid` | SLAM-kaart (van slam_toolbox) |
| In | `/odom` | `Odometry` | Positie van de robot (odom-frame) |
| In | `/scan` | `LaserScan` | Lidar, voor uitwijken |
| In | `/goal_pose` | `PoseStamped` | Handmatig doel uit RViz |
| Uit | `/cmd_vel` | `Twist` | Stuurcommando (snelheid + draai) |
| Uit | `/planned_path` | `Path` | Het geplande pad → lijn in RViz |

## 2. Architectuur & keuzeonderbouwing

### Waarom A\*?
A\* zoekt het goedkoopste pad van A naar B. Anders dan Dijkstra (die "blind" in alle
richtingen zoekt) gebruikt A\* een **heuristiek** — een schatting van de resterende
afstand — waardoor het veel minder cellen verkent en sneller een pad vindt:

```
Dijkstra: f(n) = g(n)            (alleen afgelegde weg)
A*:       f(n) = g(n) + h(n)     (afgelegde weg + geschatte afstand tot doel)
```

### Waarom een costmap met "inflatie"?
De robot is **0.75 m breed en 1.55 m lang**. Bij een kaartresolutie van 0.05 m is dat
~15 cellen breed. Als A\* gewoon over elke vrije cel zou plannen, plant hij paden
*vlak langs muren* waar de robot fysiek niet past of tegenaan botst. Daarom blazen we
obstakels op met de **robotstraal** (`ROBOT_RADIUS`): het pad houdt automatisch genoeg
afstand. De echte deuren in de wereld zijn ~2.9 m breed, dus die blijven prima
begaanbaar.

### De vier bouwstenen
- **`MinHeap`** — een zelfgeschreven binaire min-heap (prioriteitswachtrij). Zorgt dat
  A\* steeds de meest kansrijke cel als eerste pakt, zonder telkens de hele lijst te
  sorteren.
- **`Costmap`** — zet de `OccupancyGrid` om naar (a) *welke cellen berijdbaar zijn* en
  (b) *een kostengradiënt* die het midden van doorgangen aanmoedigt.
- **`astar()`** — het eigenlijke padzoeken op de costmap.
- **`AStarNavigator`** (de ROS-node) — kiest doelen, plant, tekent het pad en rijdt.

> **Implementatie keuze uitleg:** we hebben de prioriteitswachtrij zelf geschreven om te begrijpen hoe
> padvinden op datastructuur-niveau werkt.

## 3. Code-documentatie

### 3.1 Parameters (bovenin het bestand)
| Parameter | Waarde | Betekenis |
|---|---|---|
| `ROBOT_RADIUS` | `0.40` m | Inflatie: hoever obstakels worden "opgeblazen". Net genoeg dat de 0.75 m brede robot past; laag genoeg om smalle doorgangen open te houden. |
| `SOFT_RADIUS` | `0.35` m | Extra zone *buiten* de inflatie met aflopende kosten. |
| `SOFT_WEIGHT` | `4.0` | Hoe sterk de robot muren mijdt (hoger = meer in het midden van de doorgang). |
| `UNKNOWN_PENALTY` | `2.0` | Strafkosten voor rijden door onverkend gebied (mag wel, maar bekend = voorkeur). |
| `GOAL_TOL` | `0.5` m | Doel geldt als bereikt binnen deze afstand. |
| `LOOKAHEAD` | `1.0` m | Pure-pursuit: hoe ver vooruit op het pad de robot mikt. |
| `MAX_SPEED` | `0.65` m/s | Maximale rijsnelheid. |
| `LIDAR_SAFE` | `0.5` m | Onder deze afstand vóór de robot → uitwijken. |
| `ASTAR_MAX_ITER` | `120000` | Veiligheidslimiet op A\*-expansies (faalt snel i.p.v. vast te lopen). |

### 3.2 Klasse `MinHeap`
Beheert de "open set" van A\*. `push(priority, value)` voegt toe en herstelt de
heap-volgorde naar boven (`_sift_up`); `pop()` haalt het kleinste element en herstelt
naar beneden (`_sift_down`). `__len__` maakt `while len(open_heap):` mogelijk — een
detail dat in de oude versie misging (zie *Problemen & Fixes #1*).

### 3.3 Klasse `Costmap`
Wordt elke planronde opnieuw gebouwd uit de laatste `/map`. Stappen:
1. **Inflatie (lethal):** alle bezette cellen (`>50`) worden `ROBOT_RADIUS`/resolutie
   keer "gedilateerd" (verbreed). Resultaat: zone waar het robotmiddelpunt **niet** mag
   komen.
2. **Zachte kosten:** ringen *buiten* de lethal-zone krijgen aflopende kosten (1 → 0).
   Hierdoor verkiest A\* het midden van een gang boven vlak langs de muur.
3. **Berijdbaar = `~lethal`.** Belangrijk: **onbekende cellen mogen óók** (met
   `UNKNOWN_PENALTY`), zodat de robot naar nog-onverkende doelen kan rijden.

Hulpfuncties:
- **`world_to_grid` / `grid_to_world`** — vertalen tussen meters (wereld) en
  cel-indexen (raster), op basis van de resolutie en de kaart-origin.
- **`is_free(x,y)`** — binnen de kaart én berijdbaar?
- **`snap_to_free(x,y)`** — vind de dichtstbijzijnde berijdbare cel. **Klemt het punt
  eerst binnen de kaartgrenzen**, zodat een doel net buiten de kaart naar de rand wordt
  getrokken i.p.v. te falen.

### 3.4 Functie `astar(costmap, start, goal)`
1. Reken start en doel om naar celcoördinaten en **snap** beide naar een berijdbare cel.
2. 8-richtingen-zoektocht (recht = kosten 1.0, diagonaal = 1.414).
3. De stapkosten worden **verhoogd met de zachte kosten** rond muren
   (`step * (1 + SOFT_WEIGHT * cost)`), zodat het pad afstand houdt.
4. Heuristiek = euclidische afstand tot het doel.
5. Geeft een lijst wereld-coördinaten terug, of `None` als er geen pad is (of de
   iteratielimiet bereikt is).

`smooth_path()` verdunt het pad (houd elke 3e punt + het eindpunt) zodat de padvolger
soepeler loopt.

### 3.5 Klasse `AStarNavigator` (de node)

**Positie in de juiste frame (`on_odom` + TF).** De costmap staat in de **map-frame**,
maar `/odom` geeft de positie in de **odom-frame**. Omdat SLAM de positie corrigeert,
lopen deze frames uit elkaar. We rekenen daarom de odom-positie om naar de map-frame met
de `map→odom`-transform (via TF):
```
robot_map = map→odom  ∘  odom_positie
```
Zonder dit denkt de robot dat hij ergens anders staat dan op de kaart → hij ontwijkt
"lucht" en botst tegen het echte obstakel (zie *Problemen & Fixes #9*).

**`plan_loop` (2 Hz):**
1. Bouw de costmap opnieuw.
2. Doel bereikt? → loslaten.
3. **Stuck-detectie:** geen voortgang in 8 s → doel op de **blacklist**, kies een ander.
4. Geen doel? → `find_frontier()`.
5. Plan met A\*. Lukt het niet: een frontier wordt meteen losgelaten; een **handmatig
   doel** wordt na 4 mislukte pogingen opgegeven (anders blijft hij spammen).
6. Publiceer het pad op `/planned_path`.

**`find_frontier()` — kies de beste opening:**
1. **Frontier** = vrije cel die grenst aan onbekend gebied, én berijdbaar.
2. **Bereikbaarheid:** een flood-fill (BFS) vanaf de robot houdt alleen frontiers over
   waar hij echt kan komen.
3. **Clustering:** verbonden frontier-cellen worden geclusterd. Een **grote cluster =
   brede opening = waarschijnlijk een deur** naar een grote ruimte.
4. **Scoren:** `score = grootte·0.5 − afstand·0.5 + vooruit·8` (en een extra straf als de
   opening achter de robot ligt). "Vooruit" wordt bepaald door de **rijrichting**
   (gemiddeld over recente beweging), niet de momentane draai — zo blijft hij rechtdoor
   de volgende kamer in gaan i.p.v. om te draaien.

**`drive_loop` (10 Hz) — pure pursuit + uitwijken:**
- **Uitwijken:** is er iets binnen `LIDAR_SAFE` vóór de robot, dan draait hij naar de
  meest open kant **tot het front vrij is** (draairichting wordt vastgezet zodat hij
  niet heen-en-weer oscilleert).
- **Pure pursuit:** mik op een punt ~`LOOKAHEAD` meter vooruit op het pad; stuur op de
  hoekfout; rij langzamer naarmate er minder ruimte recht vooruit is.

**`obstacle_info()`** verdeelt de lidar in sectoren: front (±50°), links en rechts.

## 4. Problemen & Fixes (de weg van origineel → werkend)

> Dit is de kern van wat we hebben opgelost. Elk probleem was zichtbaar gedrag, met een
> concrete oorzaak en fix.

**#1 — Robot draaide alleen rondjes, vond nooit een pad.**
Drie bugs tegelijk: (a) de uitwijk-timer werd elke 0.1 s opnieuw gezet zolang er iets
vóór de robot was → eindeloos draaien; (b) `find_path` gebruikte ongedefinieerde
variabelen (`startX`/`goalX` i.p.v. `start_x`/`goal_x`) → A\* crashte elke keer; (c)
`while openSet:` op een wachtrij zonder lengte → oneindige lus/crash.
**Fix:** uitwijken alleen starten als hij nog niet bezig is; correcte variabelen; een
nette `MinHeap` met `__len__`.

**#2 — Robot kreeg tegenstrijdige commando's.**
Zowel `explorer.py` als `room_detector.py` publiceerden naar `/cmd_vel` en vochten om de
besturing. **Fix:** `room_detector` rijdt niet meer — die doet alleen detectie + markers.

**#3 — "Geen A\*-pad" naar doelen aan de rand van de kaart.**
A\* zag onbekende cellen als muur, dus je kon alleen binnen al-verkend gebied navigeren.
**Fix:** onbekende cellen zijn berijdbaar (met strafkosten), het doel wordt naar de
kaartrand geklemd, en de snap-zoekstraal is groter.

**#4 — Reed dwars door muren / botste.**
De inflatie stond verkeerd afgesteld op de robotgrootte. Te weinig → botsen; te veel →
doorgangen sloten dicht ("geen pad"). **Fix:** inflatie als aparte costmap-laag,
afgestemd op de robot; een te grote `is_valid`-buffer (die alles blokkeerde) verwijderd.

**#5 — Mini-stapjes, traag kiezen.**
De robot pakte telkens het *dichtstbijzijnde* frontier (0.4 m verderop) en kroop zo
vooruit. **Fix:** **frontier-clustering** — kies de grootste opening (echte deur) i.p.v.
losse ruis-cellen.

**#6 — Draaide om na een doel, terwijl er rechtdoor ruimte was.**
De "vooruit"-voorkeur gebruikte de *momentane* oriëntatie, die bij aankomst niet meer
klopte. **Fix:** "vooruit" = de **rijrichting** (gemiddeld over beweging), met een
sterke voorkeur en een straf voor openingen achter de robot.

**#7 — Bleef vastzitten vóór een blok.**
De uitwijking draaide een vaste tijd en flipte dan van richting → oscillatie. **Fix:**
uitwijken **tot het front vrij is** met vastgezette draairichting, plus **stuck-detectie
+ blacklist** (na 8 s geen voortgang → ander doel).

**#8 — Te traag en hangend op onbereikbare doelen.**
Een te zware inflatie (0.60 m) sloot doorgangen → mislukte A\*-zoekacties hamerden elke
0.5 s op een grote kaart → hapering. **Fix:** inflatie terug naar 0.40 m (doorgangen
open, A\* ~instant), hogere `MAX_SPEED`, lagere `ASTAR_MAX_ITER`, en een handmatig doel
opgeven na 4 mislukte pogingen.

**#9 — Robotpositie op de kaart kwam niet overeen met Gazebo.**
We gebruikten de ruwe `/odom`-positie, maar SLAM corrigeert de positie waardoor `map` en
`odom` uit elkaar lopen. De robot "ontweek" daardoor obstakels op de verkeerde plek.
**Fix:** de positie omrekenen naar de **map-frame** via de `map→odom`-transform (één
hop, sim-tijd) — zo klopt de robot op de kaart weer met de werkelijkheid.

**#10 — We wilden het pad zien in RViz.**
**Fix:** het geplande pad publiceren als `nav_msgs/Path` op `/planned_path`, met een
*Path*-display (groene lijn) en de *2D Nav Goal*-tool toegevoegd aan de RViz-config.

## 5. Bekende beperkingen / vervolg
- De fijne **botsing-afhandeling** is inmiddels als apart veiligheidsfilter samengevoegd
  met de pathfinding (zie [Botsingdetectie_Documentatie.md](Botsingdetectie_Documentatie.md)):
  die remt de robot af bij obstakels, waardoor de inflatie omlaag en de snelheid omhoog mocht.
- Verkenning over meerdere kamers werkt, maar is nog te verbeteren in snelheid en in het
  consequent doorpakken naar verre kamers en nog het ontwijken van muren want hij rijdt soms nog de muur in.
- De `map↔odom`-correctie leunt op de TF van slam_toolbox; valt die even weg bij het
  opstarten, dan valt de node veilig terug op `map == odom`.
