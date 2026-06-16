# Requirements
## Requirements

In dit hoofdstuk worden de requirements opgesteld door de samenhang te beschrijven tussen de verschillende onderdelen van het ontwerp. De functionele requirements definiëren wat het systeem moet kunnen doen. Terwijl de constraints vastleggen onder welke voorwaarden of beperkingen dit moet gebeuren.

### Functionele Requirements

Hier worden de functionele requirements beschreven die aangeven wat het systeem moet kunnen en welke functies essentieel zijn voor de werking ervan. Deze requirements komen ook vanuit Robosub zelf en zijn besproken met de opdrachtgevers.

| F01.1            | Robotarm - Uitstrekken van robotarm                       |
| ---------------- | --------------------------------------------------------- |
| **Beschrijving** | De robotarm moet een uitstrekkende beweging kunnen maken. |
| **Rationele**    | De robotarm moet een valve kunnen bereiken.               |
| **Prioriteit**   | Must have                                                 |


| F02.1            | Kop - Vastpakken van een valve                             |
| ---------------- | ---------------------------------------------------------- |
| **Beschrijving** | De robotarm moet een valve kunnen vastpakken               |
| **Rationele**    | De valve kan alleen worden gedraaid als de robotarm werkt. |
| **Prioriteit**   | Must have                                                  |


| F02.2            | Kop - Draaien van robotarm                                    |
| ---------------- | ------------------------------------------------------------- |
| **Beschrijving** | De robotarm moet een kwartslag kunnen draaien                 |
| **Rationele**    | Om een valve vast te kunnen pakken, moet de arm gaan draaien. |
| **Prioriteit**   | Must have                                                     |



| F03.1            | Documentatie - Productdocumentatie                                                                             |
| ---------------- | -------------------------------------------------------------------------------------------------------------- |
| **Beschrijving** | Het eindproduct bevat zelfbeschrijvende documentatie bestaand uit haar voorafgaande onderzoek en specificatie. |
| **Rationele**    | Het eindproduct moet begrijpelijk en toegankelijk zijn voor de eindgebruiker.                                  |
| **Prioriteit**   | Must have                                                                                                      |


| **F04.1**        | Vision - Camera voor Vision                                                                                             |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Beschrijving** | De simulatie moet een continue videostroom beschikbaar stellen die geschikt is als input voor objectdetectie.                |
| **Rationele**    | Een stabiele aanvoer van beelddata is noodzakelijk voor het functioneren van de gehele vision pipeline. |
| **Prioriteit**   | Must have                                                                                                             |

| **F04.2**        | Vision - Automatische Detectie                                                               |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Beschrijving** | De vision pipeline moet in staat zijn om de valve automatisch te detecteren en te lokaliseren zonder dat er tijdens runtime handmatige invoer of selectie nodig is.           |
| **Rationele**    |Het elimineren van menselijke tussenkomst tijdens de missie is cruciaal voor de autonomie van de RoboSub. |
| **Prioriteit**   | Must have                                                                                                             |

| **F04.3**        | Vision - Output met Confidence Score                              |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Beschrijving** | Het detectiemodel moet bij elke detectie een confidence-score genereren.         |
| **Rationele**    |Door middel van deze score kan de controller onzekere detecties filteren, waardoor acties alleen worden ondernomen bij een voldoende betrouwbaar resultaat.|
| **Prioriteit**   | Should have |

| **F04.4**        | Vision - Integratie                              |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Beschrijving** | De output van de vision pipeline moet in een gestandaardiseerd formaat (bijv. coördinaten of ROS-topics) worden aangeleverd aan de robotarm controller.           |
| **Rationele**    |Het systeem moet modulair zijn zodat de vision data direct kan worden gebruikt voor de aansturing van de arm (inverse kinematica).|
| **Prioriteit**   | Should have                                                                                                            |



| **F05.1**        | Dynamica - Zwaartekracht                                                           |
| ---------------- | ---------------------------------------------------------------------------------- |
| **Beschrijving** | Op de robotarm moet een zwaartekracht component zitten.                            |
| **Rationele**    | De zwaartekracht is nodig om de virtuele omgeving zo realistisch mogelijk te maken |
| **Prioriteit**   | Should have                                                                        |

| **F05.2**        | Dynamica - Hydrauliek                                                              |
| ---------------- | ---------------------------------------------------------------------------------- |
| **Beschrijving** | De robotarm moet door middel van hydrauliek kunnen bewegen.                        |
| **Rationele**    | De hydrauliek is nodig, omdat het voor een soepele beweging van de arm kan zorgen. |
| **Prioriteit**   | Should have                                                                        |

| **F06.1**        | PID - Controller input                                                             |
| ---------------- | ---------------------------------------------------------------------------------- |
| **Beschrijving** | De robotarm moet aangestuurd kunnen worden via een fysieke controller met gebruik van een PID.                 |
| **Rationele**    | De robotarm kan handmatig door de gebruiker naar de valve gestuurd worden.  |
| **Prioriteit**   | Could have                                                                        |

### Niet-Functionele Requirements

Er zijn natuurlijk ook niet-functionele requirements opgezet, deze zijn nagelopen  met Robosub te controleren of ze voldoen aan hun belangen. 

| NF01.1           | Robotarm - Structuur robotarm                                                                 |
| ---------------- | --------------------------------------------------------------------------------------------- |
| **Beschrijving** | De simulatie van de robotarm moet bestaan uit een basis, drie segmenten en een roterende kop. |
| **Rationele**    | Deze structuur is in werkelijkheid gerealiseerd, dus de simulatie moet aansluitend zijn.      |
| **Prioriteit**   | Must have                                                                                     |

| NF01.2           | Kop - Rotatie van de kop                                                      |
| ---------------- | ----------------------------------------------------------------------------- |
| **Beschrijving** | De kop van de robotarm moet minimaal 90 graden kunnen roteren.                |
| **Rationele**    | Om een valve te openen moet het handvat een kwartslag gedraaid kunnen worden. |
| **Prioriteit**   | Must have                                                                     |


| NF03.1           | Documentatie - Overdraagbare documentatie                                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Beschrijving** | Het eindproduct bevat een overdraagbare documentatie zodat toekomstige projectgroepen eenvoudig op het al bestaande werk kunnen doorbouwen. |
| **Rationele**    | Toekomstige projectgroepen besteden minder tijd aan het begrijpen en reproduceren van het al gemaakte werk.                                 |
| **Prioriteit**   | Must have                                                                                                                                   |


| NF04.1           | Vision - Camera Positie                                                                                                                                                |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Beschrijving** | Positie van camera moet zo dicht mogelijk bij de werkelijkheid zitten. +- *input foutmarge*                                                                            |
| **Rationele**    | Als de positie van de camera hetzelfde is als waar die in het echt zit, kan je uit de simulatie nauwkeurig testen hoe de robotarm er in ed werkelijkheid uit gaat zien |
| **Prioriteit**   | Should have  |


| NF04.2           | Vision - Detectienauwkeurigheid                                                                 |
| ---------------- | ------------------------------------------------------------------------------------------ |
| **Beschrijving** | Het model moet de valve met een nauwkeurigheid van minimaal 75% correct herkennen.detecteren                              |
| **Rationele**    | Een hoge accuraatheid is essentieel om de valve veilig te kunnen benaderen en vast te pakken zonder faalkans. |
| **Prioriteit**   | Should have                                                                              |

| NF04.3           | Vision - Robuustheid                                                                |
| ---------------- | ------------------------------------------------------------------------------------------ |
| **Beschrijving** | De detectie moet betrouwbaar blijven bij variaties in de opnamehoek, afstand en belichting binnen de gesimuleerde omgeving.                        |
| **Rationele**    | De omgeving onder water en de positie van de robot zijn variabel; het systeem mag niet falen door kleine afwijkingen in omgevingsfactoren. |
| **Prioriteit**   | Should have                                                                              |

| NF04.4           | Vision - Inference Snelheid                                                             |
| ---------------- | ------------------------------------------------------------------------------------------ |
| **Beschrijving** | De verwerkingstijd (inference) van het model moet laag genoeg zijn om real-time bewegingen in de simulatie mogelijk te maken.                       |
| **Rationele**    | Vertraging in de beeldverwerking resulteert in een trage respons van de robotarm, wat het uitvoeren van snelle handelingen belemmert. |
| **Prioriteit**   | Should have                                                                              |

| NF04.5           | Vision - Maintainability                                   |
| ---------------- | ------------------------------------------------------------------------------------------ |
| **Beschrijving** | De gebruikte dataset, de gelabelde beelden en de configuratiebestanden moeten volledig gedocumenteerd zijn.               |
| **Rationele**    | Dit stelt toekomstige ontwikkelaars in staat om het model efficiënt te hertrainen of te verbeteren met nieuwe data.|
| **Prioriteit**   | Should have                                                                              |




| NF05.1           | Dynamica - Dynamica-berekeningen                                             |
| ---------------- | ---------------------------------------------------------------------------- |
| **Beschrijving** | De berekeningen moeten **snel genoeg** zijn.                                 |
| **Rationele**    | De **snelle berekeningen** zorgen ervoor dat de robot real-time kan bewegen. |
| **Prioriteit**   | Should have                                                                  |


| NF05.2           | Dynamica - Dynamica bij draaien van de kop                                   |
| ---------------- | ---------------------------------------------------------------------------- |
| **Beschrijving** | Het draaien van de kop van de robotarm moet op **matige snelheid** gebeuren. |
| **Rationele**    | Met een **matige snelheid** kan de robotarm nauwkeurig draaien.              |
| **Prioriteit**   | Should have                                                   |

| NF06.1          | PID  - Overshoot                                    |
| ---------------- | ---------------------------------------------------------------------------- |
| **Beschrijving** | De overshoot moet beperkt blijven tot maximaal 5% van de totale verplaatsing. |
| **Rationele**    | en te grote overshoot zorgt ervoor dat de robotarm voorbij zijn doel schiet. Dit kan resulteren in botsingen met de omgeving of het missen van de valve, wat de taak faalt.|
| **Prioriteit**   | Must have                                             |

| NF06.2         | PID  - Settling time                                   |
| ---------------- | ---------------------------------------------------------------------------- |
| **Beschrijving** | De arm moet een ingestelde positie bereiken en stabiel blijven (binnen een foutmarge van 2% van het setpoint) binnen maximaal 10 seconden na het commando. |
| **Rationele**    | Een snelle settling time is vereist voor efficiënte operaties. de arm mag niet onnodig lang blijven trillen of zoeken naar zijn eindpositie voordat de grijper wordt geactiveerd.|
| **Prioriteit**   |Should have                                         |

| NF06.3         | PID  - Steady-State Error                                   |
| ---------------- | ---------------------------------------------------------------------------- |
| **Beschrijving** | Na het bereiken van de doelpositie mag de permanente afwijking niet groter zijn dan 0.05 radialen. |
| **Rationele**    | Hoge precisie is essentieel bij het grijpen van objecten. een te grote afwijking zorgt ervoor dat de grijper het handvat niet correct kan omsluiten.|
| **Prioriteit**   |Must have   

### Constraints

Natuurlijk zijn er ook onderdelen waarbij rekening gehouden moeten worden of deze juist niet erin moeten komen of dat ze ter veiligheid wel gesteld zijn. Ze bepalen binnen welke kaders het systeem moet worden ontwikkeld.

| C01.1            | Main body sub                                                                                      |
| ---------------- | -------------------------------------------------------------------------------------------------- |
| **Beschrijving** | De robot arm kan maximaal *zoveel graden* naar boven bewegen                                       |
| **Rationele**    | Het hoofd onderdeel van de sub bevindt zich boven de arm waardoor die niet die kant op kan bewegen |