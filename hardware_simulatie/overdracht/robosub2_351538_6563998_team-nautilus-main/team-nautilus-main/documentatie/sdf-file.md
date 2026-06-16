# Documentatie van de SDF file

## Overzicht

Deze SDF-file beschrijft een **onderwater simulatieomgeving** in Gazebo waarin een RoboSub met een robotarm wordt gesimuleerd.

De simulatie bestaat uit:

* Een **onderwaterwereld** met zwaartekracht en licht
* **Fysische plugins** voor watergedrag (buoyancy en hydrodynamica)
* Een **zeebodem (seafloor)**
* Een **RoboSub model** met een meervoudige robotarm (links + joints)

---

## Environment (Wereldconfiguratie)

### Waterdruk & Buoyancy

De RoboSub moet onderwater functioneren. Daarom wordt de volgende plugin gebruikt:

```xml
<plugin filename="gz-sim-buoyancy-system"
        name="gz::sim::systems::Buoyancy">
  <uniform_fluid_density>1025</uniform_fluid_density>
</plugin>
```

* Simuleert **opwaartse kracht (Archimedes)**
* Gebaseerd op:

  * Volume van het object
  * Dichtheid van water (**1025 kg/m³ = zeewater**)
* Bepaalt of de RoboSub:

  * Zinkt
  * Drijft
  * Neutraal zweeft

---

### Hydrodynamica & Drag

Voor realistisch onderwatergedrag wordt gebruik gemaakt van de hydrodynamics plugin:

```xml
<plugin filename="gz-sim-hydrodynamics-system"
        name="gz::sim::systems::Hydrodynamics">
```

Deze simuleert:

* **Lineaire weerstand** (lage snelheid)
* **Kwadratische weerstand** (hogere snelheid)
* **Demping van beweging**

Bijvoorbeeld:

```xml
<linear_damping>-1 -1 -1 -0.1 -0.1 -0.1</linear_damping>
<quadratic_damping>-0.5 -0.5 -0.5 -0.05 -0.05 -0.05</quadratic_damping>
```

Betekenis:

* Eerste 3 waarden → translatie (x, y, z)
* Laatste 3 → rotatie (roll, pitch, yaw)

Elke link heeft **andere damping**, afhankelijk van grootte en functie (gripper minder weerstand dan arm).

---

### Lighting (Belichting)

```xml
<light name="sun" type="directional">
```

* Simuleert zonlicht onder water
* Belangrijke parameters:

  * `diffuse`: algemene lichtintensiteit
  * `specular`: reflectie (glans)
  * `direction`: richting van het licht

➡️ Invloed:

* Bepaalt hoe zichtbaar de RoboSub is
* Heeft grote impact op **materiaal kleuren** (zoals je merkte)

---

## 3. Seafloor (Zeebodem)

```xml
<model name="seafloor">
```

* Geplaatst op **z = -10**
* Bestaat uit een vlak (plane)
* Is **static** → beweegt niet

### Functie:

* Botsingsoppervlak voor de RoboSub
* Referentiepunt voor diepte

### Materiaal:

```xml
<diffuse>0.75 0.70 0.45 1</diffuse>
```

* Donker geel/bruin → zandkleur
* Zorgt voor visueel contrast met de RoboSub

---

## 4. RoboSub Model

```xml
<model name='RoboSub'>
```

* Startpositie:

  ```xml
  <pose>0 0 -5 0 0 0</pose>
  ```

  → Halverwege tussen wateroppervlak en bodem

---

### Fixatie aan de wereld

```xml
<joint name='world_to_robosub' type='fixed'>
```

* Verbindt RoboSub aan de wereld
* Voorkomt beweging van het hoofdlichaam

Belangrijk:

* Handig voor testen van de arm
* Niet realistisch voor een bewegende sub (kan later verwijderd worden)

---

## 5. Opbouw van de Robotarm

De robotarm bestaat uit meerdere **links en joints**:

### Structuur:

```
RoboSub (body)
 └── Base
      └── bovenarm
           └── onderarm
                └── pols
                     └── handBase
                          ├── gripper1
                          └── gripper2
```
