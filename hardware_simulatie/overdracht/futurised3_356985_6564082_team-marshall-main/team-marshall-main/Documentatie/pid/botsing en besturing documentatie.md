# Documentatie: `pid_controller.hh` en `botsing_detectie.cc`

**Bestanden**

- `pid_controller.hh` — Een eenvoudige en herbruikbare PID-regelaar (klasse).
- `botsing_detectie.cc` — Een programma dat een LIDAR gebruikt om afstand te regelen en met behulp van de PID-regelaar snelheidscommando's naar de robot publiceert.

---

**Algemene terminologie (kort)**

- `error`: het verschil tussen de gewenste waarde en de gemeten waarde.
- `P` (Proportioneel): reageert op de huidige fout.
- `I` (Integraal): corrigeert voor cumulatieve fout over tijd (vermindert blijvende afwijking).
- `D` (Afgeleide): reageert op de snelheid waarmee de fout verandert (dempt oscillaties).
- `anti-windup`: techniek om te voorkomen dat de integrator te groot wordt (beperking).
- `dt`: tijdsverschil tussen twee metingen (in seconden).

---

## `pid_controller.hh`

Beschrijving: `PIDController` is een C++ klasse die een PID-regelaar implementeert. Je kunt hiermee een foutwaarde (`error`) invoeren en de klasse geeft een correctiewaarde terug (bijvoorbeeld een motorsnelheid).

Belangrijkste onderdelen:

- Constructor: `PIDController(double kp, double ki, double kd, double integralLimit)`
  - `kp`: proportionele factor (hoe sterk reageert op huidige fout).
  - `ki`: integrale factor (hoe sterk reageert op opgestapelde fout).
  - `kd`: afgeleide factor (hoe sterk reageert op verandering van fout).
  - `integralLimit`: absolute grens voor de opgestapelde fout (anti-windup).

- `void reset()`
  - Reset de interne staat: zet de integrator (`integral_`) en `previousError_` naar 0 en markeert de controller als niet-geïnitialiseerd.
  - Gebruik dit als je de controller wilt herstarten, bijvoorbeeld na een pauze of bij een belangrijke wijziging.

- `double update(double error)`
  - De belangrijkste methode. Geef de actuele `error` (verschil tussen gemeten en gewenste waarde).
  - Intern wordt het huidige tijdstip vastgelegd en `dt` berekend.
  - Als dit de eerste keer is dat `update` wordt aangeroepen, geeft de functie alleen de P-term terug (er is geen `dt` om D-term te berekenen).
  - De integrator wordt geüpdatet met `error * dt` en beperkt met `std::clamp(..., -integralLimit_, integralLimit_)` om anti-windup te doen.
  - De afgeleide (`derivative`) wordt als `(error - previousError_) / dt` berekend.
  - De uitkomst is: `(kp_ * error) + (ki_ * integral_) + (kd_ * derivative)`.

Private velden (kort uitgelegd):

- `kp_, ki_, kd_`: PID-gewichten.
- `integralLimit_`: limiet voor `integral_`.
- `integral_`: opgeslagen integrale term.
- `previousError_`: fout van vorige update (nodig voor D-term).
- `initialized_`: bool die bijhoudt of we al een vorige update hadden.
- `lastUpdate_`: tijdstip van vorige update (voor dt).

---

## `botsing_detectie.cc`

Beschrijving: Dit bestand maakt verbinding met een Gazebo/ignition-achtige transportlaag (`gz::transport`) en doet twee dingen:
- Abonneert zich op een LIDAR-topic (`/lidar`) om afstanden te lezen.
- Publiceert snelheidscommando's (`/cmd_vel`) als `gz::msgs::Twist` op basis van de PID-regelaar.

Belangrijkste onderdelen en functies:

- Globale variabelen:
  - `gz::transport::Node::Publisher pub;` — de publisher voor `/cmd_vel`.
  - `PIDController speedPID(1.0, 0.05, 0.1, 0.5);` — instantiering van de PID-regelaar met voorbeeldwaarden.
  - `const double GEWENSTE_AFSTAND = 1.5;` — gewenste afstand tot het object (in meters).
  - `double kortste_afstand_voor = 999.0;` — laatst gemeten kortste afstand vooraan (start met hoge fictieve waarde).

- `void lidarCallback(const gz::msgs::LaserScan &_msg)`
  - Deze functie wordt aangeroepen telkens als er een nieuw LIDAR-bericht binnenkomt.
  - `int num_samples = _msg.ranges_size();` haalt het aantal meetpunten op.
  - De code zoekt in het midden van de scan (40%–60% van de samples) voor het dichtstbijzijnde object. Dit vermindert invloed van zijwaartse obstakels.
  - De kleinste geldige afstand (> 0.05m) wordt opgeslagen in `kortste_afstand_voor`.

- `int main()`
  - Maakt een `gz::transport::Node` aan en initialiseert `pub` met `node.Advertise<gz::msgs::Twist>("/cmd_vel")`.
  - Abonneert zich op `/lidar` met `node.Subscribe("/lidar", lidarCallback)`.
  - In een oneindige while-loop wordt voortdurend het volgende gedaan:
    1. Bereken `error = kortste_afstand_voor - GEWENSTE_AFSTAND;` (positief als we verder van de muur zijn dan gewenst).
    2. `double berekende_snelheid = speedPID.update(error);` — vraag de PID om de juiste snelheid.
    3. Snelheid wordt begrensd tussen -1.5 en +1.5 m/s.
    4. Er wordt een `gz::msgs::Twist` bericht gemaakt en de `linear.x` gezet op `berekende_snelheid`.
    5. Het bericht wordt gepubliceerd op `/cmd_vel`.
    6. Status wordt naar de console geprint (afstand, fout, PID snelheid).
    7. `usleep(50000);` — wacht 50 ms (20 Hz update frequentie).

Belangrijke opmerkingen en mogelijke verbeteringen (veiligheid & robuustheid):

- `kortste_afstand_voor` start op een hoge waarde (999.0). Als er tot de eerste callback lang geen LIDAR-bericht komt, kan de controller rare commando's uitgeven. Overweeg:
  - Een timeout-mechanisme: stop de robot als er geen recente LIDAR-updates zijn.
  - Een veilige start: verlaag snelheid tot 0 totdat de eerste geldige meting is binnengekomen.

- Controleer op ongeldige waarden (NaN, INFINITY) in LIDAR-gegevens voordat je ze gebruikt.

- Thread-synchronisatie: `lidarCallback` en `main` delen `kortste_afstand_voor`. De gebruikte types en het platform maken dit meestal veilig genoeg voor eenvoudige toepassingen, maar bij strakkere timing of meerdere threads kun je mutexen gebruiken.

- De `error`-berekening is `kortste_afstand_voor - GEWENSTE_AFSTAND`. Afhankelijk van hoe je PID logisch wilt opbouwen kun je ook `GEWENSTE_AFSTAND - kortste_afstand_voor` gebruiken; let op tekenconventies: in de huidige code betekent positieve `error` dat de robot verder van de muur is dan gewenst, waardoor de PID vermoedelijk positieve snelheid geeft (naar voren) — controleer dat dit overeenkomt met je robotoriëntatie.

---


## Designkeuzes

Deze sectie legt uit waarom bepaalde implementatie- en architectuurbeslissingen zijn genomen, en wat de voor- en nadelen zijn.

- `PIDController` als aparte klasse:
  - Keuze: de PID-regelaar is losgekoppeld van de sensor- en actuatorcode.
  - Reden: verhoogt herbruikbaarheid en testbaarheid. Je kunt de PID apart unit-testen zonder de hele robot/simulator.

- Anti-windup met `integralLimit_` en `std::clamp`:
  - Keuze: de integratorterm wordt begrensd.
  - Reden: voorkomt dat de integrator te ver oploopt wanneer de actuator begrensd is, wat tot langdurige overshoot leidt.

- Tijdgebaseerde afgeleide (`dt` via `chrono`):
  - Keuze: de D-term gebruikt echte tijd tussen aanroepen.
  - Reden: maakt de controller robuuster bij wisselende loopfrequenties. Nadeel: ruis in `dt` kan de D-term instabiel maken.

- Eerste-aanroep-initialisatie (`initialized_`):
  - Keuze: op de eerste `update` wordt alleen de P-term gebruikt.
  - Reden: er is geen vorige fout of dt beschikbaar, dus D-term zou onnauwkeurig zijn.

- Midden-20% van LIDAR-scan voor `kortste_afstand_voor`:
  - Keuze: zoek alleen in het midden van de scan (40%–60%).
  - Reden: vermindert invloed van zijwaartse objecten en richt zich op wat recht voor de robot zit. Nadeel: kan voorwerpen missen die net buiten dat bereik vallen.

- Negeren van waarden < 0.05 m in LIDAR:
  - Keuze: kleine afstanden als ruis/ongeldig markeren.
  - Reden: sommige sensoren geven zeer kleine of nulwaarden bij fouten; die zouden de controller kunnen verstoren.

- Gebruik van globale variabele `kortste_afstand_voor`:
  - Keuze: eenvoudige communicatie tussen callback en hoofdloop.
  - Reden: eenvoudig en voldoende voor simpele single-thread toepassingen. Nadeel: bij complexere multi-threaded apps is expliciete synchronisatie (mutex) veiliger.

- Direct publish-loop met `usleep(50000)` (20Hz):
  - Keuze: eenvoudige blokkerende loop die periodiek publiceert.
  - Reden: makkelijk te begrijpen en voldoende voor veel toepassingen. Nadeel: minder flexibel dan event-driven of timer-gebaseerde frameworks.

- Begrenzing van motorsnelheid (`-1.5` tot `+1.5` m/s):
  - Keuze: harde limiet op output.
  - Reden: veiligheidsmaatregel om te voorkomen dat de robot te snel gaat.

- Gebruik van `gz::transport` en `gz::msgs::Twist`:
  - Keuze: standaard Ignition/Gazebo messaging APIs gebruiken.
  - Reden: integratie met simulatie en bestaande ecosystemen. Als je ROS gebruikt, kun je vergelijkbare topics/berichten gebruiken.

Verbeteringen en alternatieven (kort):

- Voeg een timestamp en timeout toe aan `kortste_afstand_voor` om te stoppen bij ontbrekende data.
- Filter de LIDAR-data (bijv. median filter) om ruis te verminderen voordat je de PID voedt.
- Pas een low-pass filter toe op de D-term om afgeleide ruis te dempen.
- Abstracteer de transportlaag (interface) zodat dezelfde regelcode zowel in simulatie als op echte hardware kan werken zonder aanpassingen.
- Gebruik feedforward wanneer je model van de robot kent, zodat de PID minder hard hoeft te corrigeren.

---

## Implementatiebeslissingen en motivatie

**PID vs. aan/uit controle:** Initieel werd aan/uit-controle (stop als < 0,5m) getest, maar dit gaf instabiel gedrag (oscillatie, hoog energieverbruik). PID-regelaars bieden voortdurende aanpassingen en beter gedrag.

**Scheiding van de PIDController-klasse:** De regelaar werd losgemaakt van sensor- en actuatorlogica voor herbruikbaarheid en testbaarheid.

**LIDAR-scan: midden 20%:** Eerste versie gebruikte de dichtstbijzijnde waarde van hele scan, maar dit veroorzaakte reacties op zijmuren. Focus op midden 20% (hoeken 40-60%) beperkt afleiding door zijwaartse objecten.

**Anti-windup met integralLimit:** Zonder limiet groeit de integrale term oneindig als fout constant blijft, wat tot instabiliteit leidt. `integralLimit` maximaliseert deze term.

**Tuningwaarden (kp=1.0, ki=0.05, kd=0.1):** Bepaald via trial-and-error. Andere robottypen vereisen hertuning.

**Update-frequentie 20 Hz (50ms):** Compromis tussen responsiviteit (snelle updates) en stabiliteit (ruis-immune).

---

## Veelvoorkomende problemen & oplossingen

- Oscillatie (snel heen en weer): verlaag `kp` of verhoog `kd`.
- Te traag corrigeren / blijvende fout: verhoog `ki`, maar pas `integralLimit` aan om wind-up te voorkomen.
- Onstabiele D-term: als `dt` heel klein of variabel is, kan de afgeleide ruis versterken — maak `kd` kleiner of filter de fout voordat je de D-term berekent.
- Geen beweging: controleer dat `/cmd_vel` de juiste topic is en dat het berichttype (`gz::msgs::Twist`) wordt verwacht door de motorcontroller.

---