# Technische Documentatie: `room_detector.py` — Openingen detecteren

## 1. Doel van de node
`room_detector.py` zoekt in de SLAM-kaart naar **openingen / doorgangen** (bijv.
deuropeningen tussen kamers) en toont die als **markers in RViz**. Het is puur een
**analyse-/visualisatie-node**: hij **bestuurt de robot niet**. Het rijden en plannen
doet `explorer.py`.

### In/uit (topics)
| Richting | Topic | Type | Wat |
|---|---|---|---|
| In | `/map` | `OccupancyGrid` | SLAM-kaart |
| Uit | `/room_markers` | `MarkerArray` | Bolletjes/cilinders op de gevonden openingen (RViz) |

## 2. Architectuur & keuzeonderbouwing
De gedachte: tussen kamers zitten **smalle vrije plekken naast muren** (doorgangen). Door
die te detecteren krijg je een idee van de structuur van het gebouw en kun je ze in RViz
tonen.

De detectie gebruikt **pure NumPy** (geen extra libraries zoals SciPy), zodat de node
licht en makkelijk te draaien is.

> **Implemenatie keuze uitleg:** detectie en aansturing zijn bewust **gescheiden**. In een eerdere
> versie deed deze node óók pathfinding én sturen — dat botste met `explorer.py` (twee
> nodes die tegelijk `/cmd_vel` stuurden). Eén node die rijdt, één die analyseert, is veel
> stabieler.

## 3. Code-documentatie

### 3.1 Hulpfuncties
- **`simple_dilate(grid, iterations)`** — verbreedt ("dilateert") bezette cellen, zodat
  we de randen langs muren kunnen vinden. Een eigen implementatie zonder SciPy.
- **`find_connected_components(binary_grid)`** — labelt samenhangende clusters van cellen
  met een flood-fill (BFS). Zo tellen losse "randstukjes" als aparte openingen.

### 3.2 Klasse `RoomDetector` (de node)
- **`__init__`** — abonneert op `/map`, maakt de marker-publisher en een timer die elke
  **2 seconden** `detect_openings()` draait. (Geen `/cmd_vel`, geen rij-timer.)
- **`map_callback`** — slaat alleen de laatste kaart op.
- **`detect_openings()`** — het hart:
  1. Maak een masker van **vrije** cellen en van **bezette** cellen.
  2. Dilateer de bezette cellen en pak de **vrije cellen die aan een muur grenzen**
     (de randen/doorgangen).
  3. Cluster die randcellen met `find_connected_components`.
  4. Voor elke cluster groter dan een drempel: bereken het **zwaartepunt** en reken dat
     om naar wereld-coördinaten → dat is een "opening".
  5. Roep `publish_markers()` aan.
- **`publish_markers()`** — stuurt voor elke opening een marker naar `/room_markers`
  (eerst worden oude markers verwijderd, daarna de nieuwe getekend).

## 4. Problemen & Fixes

**#1 — Twee nodes vochten om de besturing.**
De oude `room_detector` had een eigen A\*-pathfinder, reed zelf en publiceerde naar
`/cmd_vel` — net als `explorer.py`. De robot kreeg daardoor tegenstrijdige commando's.
**Fix:** alle rij-logica verwijderd (`cmd_pub`, de rij-timer en `follow_path`). De node
doet nu **alleen detectie + markers**.

**#2 — De node reed op een verkeerde positie.**
De oude rij-logica gebruikte `robot_x/y`, maar de node had **geen `/odom`-abonnement** →
hij dacht altijd op (0,0) te staan. Omdat de node niet meer rijdt, is dit probleem
helemaal weg.

**#3 — Log-spam en onnodig rekenwerk.**
De oude `map_callback` bouwde bij **elke** kaart-update (≈10×/sec) een volledige
pathfinder op en logde "Map received". **Fix:** `map_callback` slaat nu alleen de kaart
op; de detectie draait rustig op 2 Hz.

**#4 — Veel "valse" openingen.**
De detectie markeert eigenlijk elke vrije rand langs een muur, niet alleen echte
deuren — vandaar soms tientallen "openingen". Voor **visualisatie** is dat prima. Voor
**navigatie** vertrouwen we hier daarom niet op: `explorer.py` kiest zelf zijn doelen via
frontier-clustering (zie de Explorer-documentatie). De markers blijven nuttig om in RViz
te zien wat de node "ziet".

## 5. Samenhang met de rest
- `room_detector.py` → toont openingen (`/room_markers`) in RViz.
- `explorer.py` → doet de eigenlijke navigatie (A\*, frontier-keuze, rijden) en tekent
  het geplande pad (`/planned_path`).

Beide draaien naast elkaar, maar alleen `explorer.py` stuurt de robot.
