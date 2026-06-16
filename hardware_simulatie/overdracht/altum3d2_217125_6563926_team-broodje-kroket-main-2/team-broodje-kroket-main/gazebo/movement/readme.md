# Beweging

Deze map bevat de code voor de beweging van de robot.

De map bevat een eenvoudige PID-controller die wordt gebruikt om de beweging van de robot aan te sturen. De PID-controller regelt de snelheid van de robot en zorgt ervoor dat deze op koers blijft. De code is geschreven in C++ en maakt gebruik van de Gazebo Transport-bibliotheek om te communiceren met de Gazebo-simulator.

# PID-controller

De PID-controller is een eenvoudige implementatie van een proportioneel-integraal-differentieelregelaar. De controller ontvangt een gewenste setpointwaarde, de huidige waarde en de tijdstap. Vervolgens berekent hij een stuuruitgang op basis van de fout tussen de gewenste en de huidige waarde.

De controller heeft drie parameters:

* Kp: de proportionele versterking
* Ki: de integrale versterking
* Kd: de differentiële versterking

De stuuruitgang wordt als volgt berekend:

output = Kp * error + Ki * integral + Kd * derivative

Waarbij:

* error het verschil is tussen de gewenste en de huidige waarde
* integral de opgetelde fout over de tijd is
* derivative de verandering van de fout per tijdseenheid is

De PID-controller wordt gebruikt om de snelheid van de robot te regelen en ervoor te zorgen dat deze op de juiste koers blijft. De berekende stuuruitgang wordt naar de Gazebo-simulator gestuurd om de beweging van de robot aan te sturen.

# PID-afstelling

* Kp: De proportionele versterking bepaalt hoe sterk de stuuruitgang reageert op de huidige fout. Een hogere Kp zorgt voor een krachtigere reactie, maar kan ook leiden tot overshoot en instabiliteit wanneer deze te hoog wordt ingesteld.
* Ki: De integrale versterking bepaalt hoe sterk de stuuruitgang reageert op de opgetelde fout over de tijd. Een hogere Ki helpt om blijvende fouten te elimineren, maar kan ook instabiliteit veroorzaken wanneer deze te hoog wordt ingesteld.
* Kd: De differentiële versterking bepaalt hoe sterk de stuuruitgang reageert op de snelheid waarmee de fout verandert. Een hogere Kd helpt om de reactie te dempen en overshoot te verminderen, maar kan eveneens instabiliteit veroorzaken wanneer deze te hoog wordt ingesteld.

Het afstellen van een PID-controller bestaat uit het vinden van de juiste balans tussen deze drie parameters om de gewenste prestaties te behalen. Dit gebeurt vaak door middel van testen en bijstellen.

# Inverse Kinematics

Naast de PID-controller bevat dit project een inverse kinematics (IK) solver voor de robotarm. De solver berekent de benodigde gewrichtshoeken om de eindpositie van de robotarm op een gewenste locatie in de wereld te plaatsen.

## Robotconfiguratie

De robotarm bestaat uit drie gewrichten:

- `joint`: rotatie van de basis (yaw)
- `joint1`: schoudergewricht
- `joint2`: ellebooggewricht

De arm heeft twee segmenten:

```cpp
L1 = 0.77 m
L2 = 0.77 m
```

De basis van de arm bevindt zich op:

```cpp
BASE_X =  0.000000
BASE_Y = -1.337465
BASE_Z =  0.240018
```

Alle doelcoördinaten worden eerst omgerekend naar het lokale coördinatensysteem van de robotbasis.

## Berekening van de gewrichtshoeken

Voor een doelpositie `(x, y, z)` worden de volgende stappen uitgevoerd.

### Basisrotatie

De eerste hoek bepaalt in welke richting de arm moet draaien.

```cpp
joint1_angle = atan2(y, x);
```

### Horizontale afstand

De afstand van de basis tot het doel in het horizontale vlak wordt berekend met:

```cpp
r = sqrt(x * x + y * y);
```

### Ellebooghoek

Met behulp van de cosinusregel wordt de hoek van het tweede armsegment berekend.

```cpp
cos_angle =
    (L1 * L1 + L2 * L2 - r * r - z * z)
    / (2.0 * L1 * L2);
```

De waarde wordt begrensd tussen `-1` en `1` om numerieke fouten te voorkomen.

```cpp
cos_angle = std::clamp(cos_angle, -1.0, 1.0);
```

Daarna wordt de hoek berekend:

```cpp
joint2_angle = -acos(cos_angle);
```

### Schouderhoek

De schouderhoek wordt berekend op basis van de hoogte van het doel en de positie van het tweede armsegment.

```cpp
joint3_angle =
    atan2(z, r)
    - atan2(
        L2 * sin(joint2_angle),
        L1 + L2 * cos(joint2_angle)
      );
```

De functie retourneert vervolgens:

```cpp
return {joint1_angle, joint2_angle, joint3_angle};
```

## Bewegingslogica

De robot gebruikt een eenvoudige toestandsmachine om veilig tussen doelposities te bewegen.

### YAW

De basis draait eerst richting het doel terwijl de arm volledig is ingetrokken.

### EXTEND

Zodra de yaw-hoek is bereikt, worden de schouder en elleboog naar de berekende IK-hoeken gestuurd.

### WAIT

Wanneer alle gewrichten binnen de ingestelde foutmarge van hun doel zitten, wacht de robot kort op de locatie.

### RETRACT

Na het wachten wordt de arm teruggebracht naar de thuispositie.

### NEXT TARGET

Na het intrekken wordt het volgende doel geselecteerd en begint de cyclus opnieuw.

## Voorbeeld doelposities

De robot beweegt cyclisch tussen meerdere vooraf gedefinieerde locaties:

- Printer
- Curing station
- Table
- Bin

Voor iedere locatie wordt inverse kinematics gebruikt om de benodigde gewrichtshoeken te berekenen.

## Aanbevelingen
Een mogelijke verbetering voor toekomstige versies van het systeem is het volledig benutten van de verticale bewegingsmogelijkheden van de robotarm. Hoewel de arm momenteel in hoogte kan bewegen, wordt deze functionaliteit slechts beperkt gebruikt. Tijdens de uitvoering beweegt de arm naar een vooraf bepaalde hoogte en keert daarna terug naar de basispositie, ongeacht de hoogte van het doelobject. Door de hoogtebeweging rechtstreeks op te nemen in de trajectplanning en inverse kinematics kan de arm nauwkeuriger naar specifieke doelposities bewegen. Dit zou leiden tot efficiëntere bewegingen, een groter bruikbaar werkbereik en een betere positioneringsnauwkeurigheid.

Een verdere aanbevolen verbetering is het optimaliseren van de collision-configuratie van de robotarm en de objecten in de simulatie. Momenteel kan de arm in sommige situaties door objecten heen bewegen. Door correcte botsingsdetectie en collision-afhandeling toe te passen, wordt het gedrag van de robot realistischer en sluit de simulatie beter aan op een fysieke implementatie.

Een verdere aanbeveling is het uitbreiden van de robotarm met een extra actief gewricht. In de huidige implementatie worden slechts twee vrijheidsgraden gebruikt voor de positionering van de arm, waardoor de bewegingsmogelijkheden beperkt zijn en sommige posities moeilijk of niet optimaal bereikt kunnen worden. Door een derde joint te implementeren en op te nemen in de inverse kinematics-berekeningen, krijgt de robotarm een grotere bewegingsvrijheid. Dit vergroot het bereik, verbetert de flexibiliteit bij het benaderen van objecten en maakt complexere bewegingen en taken mogelijk.

# Bronnen
Voor de Inverse Kinematics is er maar een bron gebruikt:

MathWorks. (n.d.). Derive and apply inverse kinematics to robot arm. MATLAB & Simulink Documentation. https://www.mathworks.com/help/symbolic/derive-and-apply-inverse-kinematics-to-robot-arm.html
# Bouwen en uitvoeren

Volg deze stappen om de code te bouwen en uit te voeren:

Ga naar de map movement.

mkdir build
cd build
cmake ..
make

Voer vervolgens het programma uit met:

./movement
