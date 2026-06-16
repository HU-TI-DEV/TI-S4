# Technische Documentatie: RViz Configuratie

## 1. Systeemoverzicht

Dit bestand beschrijft de RViz 2-configuratie voor de visualisatie van robot Flip. De configuratie stelt RViz in om de occupancy grid (kaart), LiDAR-puntenwolk, TF-transformatieboom en deurmarkers tegelijkertijd weer te geven in een bovenaanzicht. Het bestand wordt geladen bij het opstarten van RViz en bepaalt welke topics worden gevisualiseerd en hoe.

---

## 2. Globale instellingen

| Parameter | Waarde | Beschrijving |
|---|---|---|
| `Fixed Frame` | `map` | Alle displays worden uitgedrukt ten opzichte van het kaartframe |
| `Background Color` | `48, 48, 48` | Donkergrijze achtergrond voor contrast |
| `Frame Rate` | 30 Hz | Maximale verversingssnelheid van het venster |

Het gebruik van `map` als fixed frame vereist dat de TF-keten `map` → `odom` → `base_link` aanwezig is. Deze wordt aangeleverd door SLAM Toolbox (voor `map` → `odom`) en de `TFBroadcasterNode` (voor `odom` → `base_link`).

---

## 3. Displays

### Map

Toont de occupancy grid die door SLAM Toolbox wordt gepubliceerd.

| Parameter | Waarde |
|---|---|
| Topic | `/map` |
| Color Scheme | `map` (grijs: onbekend, wit: vrij, zwart: bezet) |
| Alpha | 0.7 (licht transparant) |
| Durability | Transient Local (ontvangt ook eerder gepubliceerde kaarten) |
| Reliability | Reliable |

De `Transient Local` durability is essentieel: SLAM Toolbox publiceert de kaart niet continu maar alleen bij updates. Zonder deze instelling zou RViz de kaart missen als het later wordt opgestart dan de kaartnode.

---

### LaserScan

Toont de ruwe LiDAR-meetpunten als rode punten in het kaartframe.

| Parameter | Waarde |
|---|---|
| Topic | `/scan` |
| Color | Rood (255, 0, 0) |
| Color Transformer | `FlatColor` (vaste kleur, geen intensiteitscodering) |
| Style | `Points` |
| Size | 3 pixels |
| Reliability | Best Effort |

`Best Effort` wordt gebruikt voor de laserscan omdat LiDAR-data met hoge frequentie binnenkomt en een verloren pakket geen probleem is; het volgende pakket bevat al nieuwe data.

---

### RoomMarkers

Toont de door `RoomDetectorNode` gepubliceerde visualisatiemarkers: rode cilinders voor gedetecteerde openingen en een blauwe bol voor het actieve navigatiedoel.

| Parameter | Waarde |
|---|---|
| Topic | `/room_markers` |
| Reliability | Reliable |

---

### TF

Toont de volledige TF-transformatieboom als assen en pijlen in de 3D-weergave.

| Parameter | Waarde |
|---|---|
| Frame Timeout | 15 seconden |
| Marker Scale | 0.5 |
| Show Arrows | Aan |
| Show Axes | Aan |
| Show Names | Aan |

De `Frame Timeout` van 15 seconden zorgt ervoor dat frames pas verdwijnen als ze langer dan 15 seconden niet zijn bijgewerkt, wat nuttig is bij tijdelijke onderbrekingen.

---

## 4. Cameraweergave

De configuratie gebruikt een bovenaanzicht (`TopDownOrtho`) als standaardweergave:

| Parameter | Waarde | Beschrijving |
|---|---|---|
| Class | `TopDownOrtho` | Orthografisch bovenaanzicht (geen perspectief) |
| Scale | 50 | Zoomfactor van de weergave |
| Target Frame | `map` | Camera volgt het kaartframe |
| Angle | 0 | Geen rotatie (was eerder 0.49 rad, wat een scheef beeld gaf) |
| X / Y | 0 / 0 | Camera gecentreerd op de oorsprong van de kaart |

Het orthografische bovenaanzicht is de meest praktische weergave voor een 2D-navigatiestack: de kaart, de robotpositie en de rijpaden zijn direct leesbaar zonder perspectiefdistorsie.

---

## 5. Beschikbare tools

| Tool | Functie |
|---|---|
| `Interact` | Interactie met markers in de scène |
| `MoveCamera` | Verplaatsen en zoomen van de cameraweergave |
| `Select` | Selecteren van objecten in de weergave |

---

## 6. Conclusie & Ontwerpverantwoording

De RViz-configuratie is afgestemd op de navigatiestack van Flip en biedt in één oogopslag inzicht in de drie kernprocessen: kaartvorming (Map), omgevingswaarneming (LaserScan) en doelplanning (RoomMarkers).

Twee configuratiekeuzes zijn bewust gemaakt:

- **Transient Local voor de Map-display:** omdat SLAM Toolbox de kaart alleen bij updates publiceert, is Transient Local noodzakelijk om de kaart te ontvangen ook als RViz later wordt gestart dan de kaartnode. Zonder deze instelling blijft de kaartweergave leeg.

- **Best Effort voor LaserScan:** LiDAR-data heeft een hoge publicatiefrequentie en is tijdsgevoelig. Het gebruik van Best Effort voorkomt dat RViz wacht op verloren pakketten en zorgt voor een vloeiende, real-time weergave van de sensordata.