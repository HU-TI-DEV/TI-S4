# Software Architectuur
## Keydrivers
**Betrouwbaarheid**  
De techniek dat Futurised gebruikt moet betrouwbaar zijn. Machines moeten voorspelbaar reageren, zodat zij hier altijd op kunnen vertrouwen.   

**Veiligheid**   
De technologie moet een bijdrage leveren aan het redden en helpen van mensen tijdens een brand. Apparatuur moet gevaren minimaliseren en mag nooit zelf een extra obstakel vormen.

**Autonomie**  
Tijdens een brand is er zoveel mogenlijk mankracht nodig en moet apparatuur zelfstandig kunnen rijden, obstakels ontwijken en de snelste route kunnen uitrekenen.

## Application Keydrivers
- Reactietijd
- Consistentie
- Testbaarheid
- Robuustheid
- Voorspelbaarheid 
- Route optimalisering
- Zelfherstellend 

## Functionele Requirements  
**F01 Rondrijden**  
Omschrijving: De robot moet zich in de simulatie kunnen bewegen (Vooruit, achteruit em draaien.)  
*Business Priority: Must have*

**F02 Omgeving scannen**  
De robot moet in de simulatie de omgeving kunnen scannen met behulp van een sensor.  
*Business Priority: Must have*

**F03 Obstakels herkennen**  
De robot moet objecten en muren in de simulatie herkennen om botsingen te voorkomen.  
*Business Priority: Must have*

**F04 Zelfstandig Navigeren**  
De robot moet zelfstandig van de ene naar de andere plek rijden in de simulatie.  
*Business Priority: Must have*

**F05 Doorgangen vinden**  
De robot moet bepalen of een opening (zoals een deur) breed genoeg is om doorheen te rijden.  
*Business Priority: Should have*

**F06 Gebruikers interactie**  
De gebruiker geeft commandos en de robot moet deze zelfstandig uitvoeren.  
*Business Priority: Should have*

**F07 Virtuele omgeving**   
Er is een virtuele omgeving waar de robot kan rondrijden.  
*Business Priority: Must have*

**F08 Veilig werken**  
De Robot moet stoppen wanneer een obstakel te dicht in de buurt komt van de robot. De robot moet bij voorkeur iets terug.
*Business Priority: must have*

**F09 Andere route Bepalen**  
De robot moet wanneer het ingesloten wordt door obstakels een andere route kiezen zonder verder in de buurt te komen van de obstakels.
*Business Priority: Should have*

## Niet-functionele Requirements
**NF01 Simulatie omgeving**  
De simulatie draait binnen Gazebo.  

**NF02 Rondrijden**  
De robot kan rijden met wielen met een snelheid van 0,5 m/s.

**NF03 Navigatie sensor**  
Voor het navigeren en scannen van de omgeving wordt er gebruik gemaakt van een Lidar-sensor met een bereik van 360 graden.  

**NF04 Obstakels ontwijken**  
De robot navigeert via een Pathfinding algortime.

**NF05 Voorspelbaar reageren**  
In drie identieke testsituaties heeft de route een maximale afwijking van 10% in tijd en afstand. 

**NF06 reactie tijd**  
De robot reageert op een obstakel binnen twee seconden na het detecteren ervan.

**NF07 Sensorwaarden vastleggen**  
De sensorwaarden van de LiDAR sensor worden vastgelegd met een frequentie van 10hz , zodat dit meegenomen kan worden voor verder onderzoek.

**NF08 Route herberekenen**  
Zorda een obstakel gedetecteerd wordt op de route, vindt de robot binnen vijf senconden een alternatieve route.

**NF09 Nauwkeurige Sensoren**  
De sensoren in de simulatie hebben ten minste 85% van de test gevallen de obstakels correct gedetecteerd.

**NF10 Afstand tot obstakel**  
De Robot houdt minstens 30cm afstand van een obstakel.

**NF11 Doorgangen**  
Een opening wordt pas gezien als doorgang zodra dit minimaal 20 centimeter breder is dan de breedte van de robot zelf.

**NF12 Beperkt zicht**  
De LiDAR kijkt door rook met een nauwkeurigheid van 85%

## Constraints
**C01 Wetgeving**  
De robot moet voldoen aan de Europese richtlijnen voor machines en specifieke veiligheidseisen voor brandweer uitrusting. 

**C02 Omgeving**  
De robot gaat te werk in een omgeving waar de temperatuur kan oplopen tot 500 graden en waar veel rook kan plaatsvinden.
