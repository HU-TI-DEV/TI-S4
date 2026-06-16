# World Models & Simulatieomgevingen
Documentatie van de world- en modelbestanden. 

## 1. Structuur van de Repository

De projectstructuur is ingericht volgens in de folder`Futurised`. Dit zorgt ervoor dat de simulator de afzonderlijke modellen en de wereld vlekkeloos kan lokaliseren en inladen.

```text
Futurised/
├── models/
│   ├── Flip/                       # Het robotmodel ("Flip")
│   │   |
│   │   ├── Flip.sdf                # De hoofd-SDF-definitie van de robot
│   │   └── model.config            # Metagegevens van de Flip-robot
│   ├── Huis_met_meubels/           # Terrein Flip
│   │   ├── model.config            # Metagegevens voor de huisomgeving
│   │   └── model.sdf               # Geometrische en visuele definitie van het huis
│   └── terrain/                    # Oud testterrein (obstakels/vormen)
│       ├── model.config            # Metagegevens voor het testterrein
│       └── terrain.sdf             # Geometrische en visuele definitie van het terrein
└── worlds/
    └── robot_world.world           # Het centrale wereldbestand waarin alles samenkomt
```

# Robot_world.world
`robot_world.world` dient als de basisomgeving voor de roboticasimulatie en bevat de basisfysica, essentiële plugins, belichting en statische objecten.

## Basisfysica
- **`max_step_size`**: 1 ms (de tijdstap tussen elke fysica-berekening).
- **`real_time_factor`**: 1.0 (zorgt ervoor dat de simulatie synchroon loopt met de werkelijke tijd).

## Plugins
- **Physics System (`gz::sim::systems::Physics`)** Verantwoordelijk voor het berekenen van de zwaartekracht, botsingen (collisions) en de dynamica van objecten.
- **User Commands (`gz::sim::systems::UserCommands`)** Maakt het mogelijk voor de gebruiker om tijdens de simulatie interactie te hebben met de GUI (zoals het selecteren en verplaatsen van modellen).
- **Scene Broadcaster (`gz::sim::systems::SceneBroadcaster`)** Zorgt ervoor dat de visuele status van de wereld correct wordt uitgezonden naar de GUI/visualisatie-omgeving.
- **Sensors System (`ignition::gazebo::systems::Sensors`)** Activeert de sensorfunctionaliteiten binnen de wereld. Dit systeem maakt gebruik van de Ogre2 render-engine voor visuele sensoren (zoals camera's of LiDAR).

## Omgeving & Belichting

### Sun (licht)
- **Schaduwen**: Ingeschakeld (`<cast_shadows>true</cast_shadows>`).
- **Lichtrichting**: Schijnt diagonaal naar beneden (`direction: [-0.5, 0.1, -0.9]`).
- **Kleur**: Neutraal grijs/wit licht met een gedempte spiegeling (`specular`) om overbelichting te voorkomen.

### Groundplane (Grondvlak)
- **Visueel formaat**: $100 \times 100$ meter.
- **Eigenschappen**: Het vlak is `static` (kan niet bewegen) en heeft een collision-vlak dat loodrecht op de Z-as staat (`normal: [0, 0, 1]`).

## Inbegrepen modellen
De wereld laadt externe modellen in via de `model://` URI. De posities ($X, Y, Z$) en rotaties (Roll, Pitch, Yaw) zijn als volgt gedefinieerd:

- `Flip` *(-11, 5, 2.5, 0, 0, 0)*
- `Huis_met_meubels` *(2, 0, 0.5, 0, 0, 0)*
- `terrain` *(0, 0, 0, 0, 0, 0)* -- **Momenteel gedeactiveerd**

> **Opmerking over `terrain`:** Het terrein is gebruikt als testomgeving voor de LiDAR en is in het bestand behouden als extra testmap. Op dit moment is het model uitgecommentarieerd zodat het niet mee laadt, maar het kan indien nodig eenvoudig weer worden geactiveerd.

# Robot Model Documentatie: `Flip`

Het bestand `flip.sdf` (SDF-versie 1.8) definieert het robotmodel **Flip**. Dit is een acht-wielig aangedreven robotplatform (skid-steer configuratie) uitgerust met zowel een GPU-gebaseerde LiDAR-sensor voor omgevingsscans als een RGB-camera voor visuele detectietaken.

## 1. Algemene Configuratie & Aandrijving
- **Modelnaam:** `Flip`
- **Canonical Link:** `chassis` (de basis-link waar de inertie en positie van het gehele model aan refereren).
- **Model Pose:** `[0, 0, 0, 0, 0, 0]` (start standaard op de oorsprong van de wereld-coördinaten).
- **Totaal Gewicht:** $\approx 9.44\text{ kg}$ (Chassis: $1.144\text{ kg}$, Front Block: $0.3\text{ kg}$, Wielen: $8 \times 1\text{ kg}$). *Opmerking: Deze gewichten zijn computationeel geoptimaliseerd voor de stabiliteit binnen de physics-engine.*

### DiffDrive Aandrijf-Plugin (`gz::sim::systems::DiffDrive`)
Voor de voortbeweging maakt het model gebruik van een differentiaalaandrijving-plugin. Hoewel het fysiek een 8-wielig platform is, wordt het softwarematig aangestuurd als een *skid-steer* voertuig via één centraal commandotopic.

- **Besturingstopic:** `cmd_vel`
- **Wielbasis (Wielscheiding):** $1.7$ meter
- **Wielradius:** $0.4$ meter
- **Odometrie Publicatie Frequentie:** $1$ Hz

#### Gekoppelde Aandrijvingsassen (Joints):
| Links (`<left_joint>`) | Rechts (`<right_joint>`) |
| :--- | :--- |
| `firstLeftWheelJoint` | `firstRightWheelJoint` |
| `secondLeftWheelJoint` | `secondRightWheelJoint` |
| `thirdLeftWheelJoint` | `thirdRightWheelJoint` |
| `fourthLeftWheelJoint` | `fourthRightWheelJoint` |


## 2. Links & Geometrische Opbouw
Het model is opgebouwd uit tien functionele links: het hoofdchassis, een sensorbehuizing aan de voorzijde en acht identieke wielen.

### Hoofdchassis (`chassis`)
De structurele basis van de robot, uitgevoerd als een rechthoekige box.
- **Relatieve Pose:** `[0.5, 0, 0.4, 0, 0, 0]` ten opzichte van `__model__`.
- **Afmetingen ($L \times B \times H$):** $1.55 \times 0.75 \times 1.05$ meter.
- **Massa:** $1.14395$ kg.
- **Inertiematrix:** $I_{xx} = 0.095329$, $I_{yy} = 0.381317$, $I_{zz} = 0.476646$ (cross-termen zijn 0).
- **Visuele Eigenschappen:** Donkerrood (Ambient: `[0.4, 0.08, 0.08]`, Diffuse: `[0.59, 0.13, 0.12]`).

### Sensorblok (`front_block`)
Een behuizing aan de voorzijde van het chassis die fungeert als fysieke drager voor alle ingebouwde sensoren.
- **Relatieve Pose:** `[0.50, 0, 0.70, 0, 0, 0]` ten opzichte van `chassis`.
- **Afmetingen ($L \times B \times H$):** $0.35 \times 0.35 \times 0.35$ meter.
- **Massa:** $0.3$ kg ($I_{xx}, I_{yy}, I_{zz} = 0.01$).
- **Collision Box:** Gedefinieerd als $0.5 \times 0.5 \times 0.5$ meter (iets groter dan de visual box voor een veiligheidsmarge rondom de sensoren).

### Wielen (8 stuks: 4 links, 4 rechts)
Alle wielen hebben identieke mechanische eigenschappen en zijn gemodelleerd als donkergrijze cilinders (`[0.1, 0.1, 0.1]`).
- **Dimensies:** Radius van $0.3$ meter en een lengte/breedte van $0.2$ meter.
- **Massa:** $1.0$ kg per wiel ($I_{xx}, I_{yy} = 0.043333$, $I_{zz} = 0.08$).
- **Oriëntatie:** Over de X-as geroteerd met $-1.5707$ radialen ($-90^\circ$) om de cilinders dwars op het chassis te zetten.
- **Posities (Relatief ten opzichte van `chassis`):**
  - `firstLeftWheel`: `[0.5, 0.45, -0.25]` | `firstRightWheel`: `[0.5, -0.45, -0.25]`
  - `secondLeftWheel`: `[0.15, 0.45, -0.25]` | `secondRightWheel`: `[0.15, -0.45, -0.25]`
  - `thirdLeftWheel`: `[-0.15, 0.45, -0.25]` | `thirdRightWheel`: `[-0.15, -0.45, -0.25]`
  - `fourthLeftWheel`: `[-0.5, 0.45, -0.25]` | `fourthRightWheel`: `[-0.5, -0.45, -0.25]`


## 3. Geïntegreerde Sensoren
Beide sensoren zijn hardcoded ingebouwd binnen de link `<link name='front_block'>`.

### A. GPU LiDAR (`gpu_lidar`)
Gebruikt hardwareversnelling via de grafische kaart voor efficiënte 2D-omgevingsdetectie.
- **Sensor Pose:** Bevindt zich op `[0, 0, 0, 0, 0, 0]` relatief ten opzichte van de `lidar_frame` referentie.
- **Topic:** `lidar`
- **Update Rate:** $10$ Hz
- **Visualisatie:** Ingeschakeld (`true`), sensorstralen zijn zichtbaar in de simulator.
- **Horizontaal Scanbereik:** Volledig $360^\circ$ veld (`min_angle`: $-3.14159$, `max_angle`: $3.14159$ rad) verdeeld over **1000 samples**.
- **Verticaal Scanbereik:** Geconfigureerd als een zuivere 2D-vlakscanner (**1 sample** op $0^\circ$).
- **Bereik (Range):** Harde limieten tussen minimaal $0.08$ meter en maximaal $10.0$ meter, met een meetafwijking/resolutie van $0.01$ meter.

### B. RGB-Camera (`camera`)
Toegevoegd ten behoeve van computervisie (zoals geometrische vorm- en contrastdetectie).
- **Sensor Pose:** Geplaatst op `[0.175, 0, -0.10, 0, 0, 0]` ten opzichte van het sensorblok. Dit plaatst de camera gecentreerd aan de onder/voorzijde van de behuizing.
- **Topic:** `camera`
- **Update Rate:** $30$ Hz (voldoende voor vloeiende video-verwerking).
- **Horizontaal Field of View (FOV):** $1.5708$ radialen (**exact $90^\circ$** breedbeeld).
- **Beeldresolutie:** $640 \times 480$ pixels (VGA-resolutie).
- **Kleurformaat:** `R8G8B8` (24-bit RGB kleurdiepte).
- **Clipping-bereik:** Objecten worden scherp weergegeven vanaf een minimale afstand van $0.1$ meter tot maximaal $100$ meter.
- **Visualisatie:** Ingeschakeld (`true`).


## 4. Gewrichten & Assen (`<joint>`)
De mechanische verbindingen bepalen de bewegingsvrijheid binnen het model. Het model bevat 1 starre verbinding en 8 draaiassen.

### Starre Verbinding (1 stuk)
- **`front_block_fixed_joint` (`type='fixed'`):** Koppelt de `front_block` rigide aan het `chassis`. Er zijn geen vrijheidsgraden; de sensoren bewegen naadloos mee met de bewegingen en trillingen van het chassis.

### Wielassen (8 stuks)
Alle acht wielgewrichten gebruiken een `revolute` type om rotatie rondom een centrale as mogelijk te maken.

- **Parent/Child Dynamica:** Het `chassis` fungeert altijd als *parent*; de individuele wiellink is de *child*.
- **Lokale Pose Referentie:** Elk gewricht heeft de eigenschap `<pose relative_to='[WielNaam]'/>`. Dit dwingt de physics-engine om het rotatie- en scharnierpunt exact in het geometrische middelpunt van de cilinder van het desbetreffende wiel te leggen.
- **Rotatie-as (`<xyz>`):** Gedefinieerd langs de **Y-as** (`0 1 0`). Dankzij de parameter `expressed_in='__model__'` is deze as gekoppeld aan het globale coördinatensysteem van de robot. Dit garandeert dat alle wielen in dezelfde richting draaien bij het aansturen.
- **Rotatielimieten:** Volledig vrijdraaiend zonder mechanische restricties. In de code is dit gewaarborgd door de fysieke limieten in te stellen op negatief oneindig (`-1.79769e+308`) en positief oneindig (`1.79769e+308`).

# Model Documentatie: `Huis_met_meubels`

Bevat de specificaties en architectonische lay-out van de simulatieomgeving `Huis_met_meubels`.

## 1. Algemene Eigenschappen
* **Modelnaam:** `Huis_met_meubels`
* **Type:** Statisch (`<static>true</static>`). De objecten hebben een oneindige massa, zijn niet onderhevig aan zwaartekracht en kunnen niet bewegen door fysieke botsingen.
* **Totale Voetafdruk:** 30 meter (X-as) bij 24 meter (Y-as).
* **Standaard Muurhoogte:** 2.0 meter (Z-as).
* **Standaard Muurdikte:** 0.2 meter.


## 2. Coördinatenstelsel & Lay-out
Het model maakt gebruik van een rechtsdraaiend Cartesisch coördinatenstelsel waarbij de oorsprong `(0, 0, 0)` zich exact in het geometrische middelpunt van de buitenmuren bevindt. 

De omgeving is symmetrisch opgebouwd en verdeeld in vier hoofdcomponenten: de buitenmuren, een horizontale tussenmuur (X-as splitsing op $Y=0$), een verticale tussenmuur (Y-as splitsing op $X=0$), en een reeks obstakels ("meubels") verdeeld over vier kwadranten.


## 3. Componenten Specificatie

### 3.1 Buitenmuren (Rood gekleurd)
De buitenmuren vormen een gesloten rechthoek van $30\text{m} \times 24\text{m}$. Alle buitenmuren hebben een felle rode kleur (`RGB: 1, 0, 0`).

| Modelnaam | Positie `(x y z r p y)` | Afmetingen `(l b h)` | Functie / Locatie |
| :--- | :--- | :--- | :--- |
| `wall_north` | `0, 12, 1, 0, 0, 0` | `30.0 × 0.2 × 2.0` | Noordelijke grens van de simulatie |
| `wall_south` | `0, -12, 1, 0, 0, 0` | `30.0 × 0.2 × 2.0` | Zuidelijke grens van de simulatie |
| `wall_east` | `15, 0, 1, 0, 0, 0` | `0.2 × 24.0 × 2.0` | Oostelijke grens van de simulatie |
| `wall_west` | `-15, 0, 1, 0, 0, 0` | `0.2 × 24.0 × 2.0` | Westelijke grens van de simulatie |

### 3.2 Interne Structuur (Rood gekleurd)
De binnenmuren splitsen de ruimte op in kamers of gangen en behouden dezelfde rode kleurcodering (`RGB: 1, 0, 0`) en hoogte ($2\text{m}$) als de buitenmuren.

#### Horizontale Tussenmuren (Langs de X-as op $Y = 0$)
Deze muren liggen op de centrale X-as, maar bevatten openingen (bijvoorbeeld voor deuropeningen of doorgangen) rond het centrum en de flanken.
* `mid_wall_left_outer`: Gepositioneerd op `(-11, 0, 1)`, lengte 8m (loopt van $X=-15$ tot $X=-7$).
* `mid_wall_left_inner`: Gepositioneerd op `(-2.1, 0, 1)`, lengte 4m (loopt van $X=-4.1$ tot $X=-0.1$).
* `mid_wall_right_inner`: Gepositioneerd op `(2.1, 0, 1)`, lengte 4m (loopt van $X=0.1$ tot $X=4.1$).
* `mid_wall_right_outer`: Gepositioneerd op `(11, 0, 1)`, lengte 8m (loopt van $X=7$ tot $X=15$).

#### Verticale Tussenmuren (Langs de Y-as op $X = 0$)
Deze muren lopen van noord naar zuid over de centrale Y-as en creëren een centrale scheidingslijn.
* `mid_vertical_top`: Gepositioneerd op `(0, 10, 1)`, lengte 4m (loopt van $Y=8$ tot $Y=12$).
* `mid_vertical_upper`: Gepositioneerd op `(0, 3, 1)`, lengte 6m (loopt van $Y=0$ tot $Y=6$).
* `mid_vertical_lower`: Gepositioneerd op `(0, -3, 1)`, lengte 6m (loopt van $Y=-6$ tot $Y=0$).
* `mid_vertical_bottom`: Gepositioneerd op `(0, -10, 1)`, lengte 4m (loopt van $Y=-12$ tot $Y=-8$).

---

### 3.3 Meubels / Obstakels (Grijs gekleurd)
Het model bevat 16 uniforme, grijze blokken (`RGB: 0.5, 0.5, 0.5`) die fungeren als meubels of statische obstakels. Elk blok heeft exact dezelfde afmetingen:
* **Grootte:** $1.0\text{m} \times 1.0\text{m} \times 1.5\text{m}$ (Lengte × Breedte × Hoogte)
* **Z-positie:** `0.75` (waardoor ze perfect op de grond rusten, aangezien de helft van de hoogte $0.75\text{m}$ is).

De obstakels zijn symmetrisch verdeeld over de vier kwadranten van het huis:

#### Noordwest Kwadrant (NW)
* `nw_1`: `(-12, 9, 0.75)` — In de hoek nabij de west- en noordmuur.
* `nw_2`: `(-4, 10, 0.75)` — Nabij de noordmuur en de centrale verticale muur.
* `nw_3`: `(-11, 3, 0.75)` — Centraal-westelijk boven de horizontale scheidingsmuur.
* `nw_4`: `(-7.5, 6, 0.75)` — Centraal in het noordwestelijke kwadrant.

#### Noordoost Kwadrant (NE)
* `ne_1`: `(12, 9, 0.75)` — In de hoek nabij de oost- en noordmuur.
* `ne_2`: `(4, 10, 0.75)` — Nabij de noordmuur en de centrale verticale muur.
* `ne_3`: `(11, 3, 0.75)` — Centraal-oostelijk boven de horizontale scheidingsmuur.
* `ne_4`: `(7.5, 6, 0.75)` — Centraal in het noordoostelijke kwadrant.

#### Zuidwest Kwadrant (SW)
* `sw_1`: `(-12, -9, 0.75)` — In de hoek nabij de west- en zuidmuur.
* `sw_2`: `(-4, -10, 0.75)` — Nabij de zuidmuur en de centrale verticale muur.
* `sw_3`: `(-11, -3, 0.75)` — Centraal-westelijk onder de horizontale scheidingsmuur.
* `sw_4`: `(-7.5, -6, 0.75)` — Centraal in het zuidwestelijke kwadrant.

#### Zuidoost Kwadrant (SE)
* `se_1`: `(12, -9, 0.75)` — In de hoek nabij de oost- en zuidmuur.
* `se_2`: `(4, -10, 0.75)` — Nabij de zuidmuur en de centrale verticale muur.
* `se_3`: `(11, -3, 0.75)` — Centraal-oostelijk onder de horizontale scheidingsmuur.
* `se_4`: `(7.5, -6, 0.75)` — Centraal in het zuidoostelijke kwadrant.

---

## 4. Visualisatie & Materiaal-eigenschappen

Voor zowel de muren als de meubels zijn de visuele (`<visual>`) en botsingselementen (`<collision>`) identiek gedefinieerd. Dit garandeert dat wat een robot 'ziet' via sensoren (zoals LiDAR of camera's) exact overeenkomt met de fysieke interactie (botsingen).

* **Muren:**
    * Ambient & Diffuse kleur: `1 0 0 1` (Mat rood, geen spiegeling).
* **Meubels:**
    * Ambient & Diffuse kleur: `0.5 0.5 0.5 1` (Mat grijs).


# Model Documentatie: `terrain`

Bevat de technische specificaties en de ruimtelijke lay-out van de simulatieomgeving `terrain`. Een oude test map voor het testen van de lidar en camera. 

## 1. Algemene Eigenschappen
* **Modelnaam:** `terrain`
* **Type:** Statisch (`<static>true</static>`). Elementen zijn verankerd in de wereld, hebben een oneindige massa en reageren niet op zwaartekracht of fysieke krachten van buitenaf.
* **Geometrieën:** Het model maakt gebruik van een mix van rechthoekige prisma's (`<box>`) en cilinders (`<cylinder>`).
* **Doel:** Een asymmetrische testomgeving met variërende obstakelhoogtes, muuroriëntaties (inclusief $90^\circ$ rotaties via yaw) en kleurcoderingen.


## 2. Coördinatenstelsel & Rotaties
Het model is gepositioneerd rond de oorsprong `(0, 0, 0)`. Verschillende muren maken gebruik van een rotatie om de Z-as (Yaw) van **1.5708 radialen** ($\approx 90^\circ$). Hierdoor worden muren die standaard langs de X-as georiënteerd zouden zijn, gedraaid zodat ze parallel lopen aan de Y-as (of vice versa, afhankelijk van de initiële definitie van de box-afmetingen).

## 3. Componenten Specificatie

De objecten binnen het terrein zijn hieronder gecategoriseerd op basis van hun type en functie.

### 3.1 Muren & Afschermingen
Deze elementen functioneren als grote barrières of kamerdelers binnen de simulatie.

| Modelnaam | Positie `(x y z r p y)` | Vorm / Geometrie | Afmetingen `(l b h)` of `(r, l)` | Kleur (RGB) | Beschrijving / Oriëntatie |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `wall_1` | `6, 0, 1, 0, 0, 0` | Box | `0.3 × 8.0 × 2.0` | Grijs (`0.4, 0.4, 0.4`) | Een dunne, hoge muur aan de oostkant parallel aan de Y-as. |
| `wall_2` | `0, 6, 1, 0, 0, 1.5708` | Box | `0.3 × 8.0 × 2.0` | Grijs (`0.4, 0.4, 0.4`) | Zelfde afmetingen als `wall_1`, maar $90^\circ$ gedraaid aan de noordkant. |
| `wall_3` | `-4, -8, 1, 0, 0, 1.5708` | Box | `0.6 × 11.0 × 3.0` | Donkerrood (`0.76, 0.22, 0.22`) | Een zeer dikke, lange en hoge barrière aan de zuidkant, $90^\circ$ gedraaid. |
| `wall_left` | `4.5, 1, 0.5, 0, 0, 1.5708` | Box | `0.5 × 3.0 × 1.0` | Geel (`1, 1, 0`) | Lagere wandsectie, $90^\circ$ gedraaid. |
| `wall_right` | `4.5, 3, 0.5, 0, 0, 1.5708` | Box | `0.5 × 3.0 × 1.0` | Cyaan (`0, 1, 1`) | Ligt in het verlengde van `wall_left` (Y-as verschuiving), $90^\circ$ gedraaid. |

### 3.2 Vrijstaande Blokken & Obstakels
Deze objecten zijn van verschillende schalen, ideaal voor het testen van path planning en LiDAR-reflecties.

| Modelnaam | Positie `(x y z r p y)` | Vorm | Afmetingen `(l b h)` | Kleur (RGB) | Kenmerken |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `low_obstacle` | `-3.5, 0, 0.2, 0, 0, 0` | Box | `1.0 × 1.0 × 0.4` | Groen (`0, 1, 0`) | Zeer laag platform ($0.4\text{m}$). Rust op de grond (`Z = 0.2`). |
| `medium_box` | `-5, 3, 0.5, 0, 0, 0` | Box | `1.5 × 1.5 × 1.0` | Rood (`1, 0, 0`) | Middelgroot obstakel met een hoogte van exact $1.0\text{m}$. |
| `big_box` | `-7, -3, 1, 0, 0, 0` | Box | `2.0 × 2.0 × 2.0` | Rood (`1, 0, 0`) | Een grote kubus van $2\text{m}$ hoog. Vormt een flinke blinde vlek voor sensoren. |

### 3.3 Cilindrische Elementen
Het model bevat één specifiek niet-hoekig objec.

* **Modelnaam:** `obstacle_2`
* **Positie `(x y z r p y)`:** `4.5, -5.5, 0.5, 0, 0, 0`
* **Geometrie:** `<cylinder>`
    * **Radius ($r$):** $0.5\text{m}$ (Totale diameter = $1.0\text{m}$)
    * **Lengte/Hoogte ($l$):** $1.0\text{m}$
* **Kleur:** Groen (`RGB: 0, 1, 0`)
* **Plaatsing:** Bevindt zich in het zuidoostelijke kwadrant van de wereld.