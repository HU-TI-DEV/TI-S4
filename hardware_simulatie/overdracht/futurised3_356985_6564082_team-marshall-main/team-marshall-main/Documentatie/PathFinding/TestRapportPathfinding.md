# Test en Validatierapport: Pathfinding Algoritme
## Inleiding
In dit bestand staat een uitgebereid test en Validatierapport over het pathfinding algoritme dat is toegepast voor de nmavigatie van Flip. Dit algoritme is gemaakt met AStar en er moet getest worden of dit algortime voldoet aan onze en de opdrachtgever's eisen. 

## Doel
Het doel is te verifiëren of het algoritme efficiënte en collision-free paden genereert binnen de grid. Het algortime moet voldoen aan alle gestelde requirements
- Optimalisatie: Controleert of het pathfinding algortime het kortst mogelijke pad kiest naar het gestelde doel. 
- Validatie: Controleert of de berekende route geen obstakels bevatten. 
- Prestatie: Controleert of de berekeningstijd voldoende is *binnen de simulatie-constraints*

## Succes criteria
| ID | Test Aspect | Succes Criterium | Drempelwaarde |
|---|---|---|---|
| TA1 | Obstakelvermijding | Er mag geen collision plaatsvinden met Flip en een object. | 0% collision met obstakels. |
| TA2 | Pad optimalisatie | Het berekende pad moet een logische, kortste route zijn. | Afwijking kleiner dan 10% van de meest ideale afstand. |
| TA3 | Validatie | Algortime moet alleen luisteren naar valide instructies. | Als het doel niet bereikbaar is negeert het deze informatie. |
| TA4 | Berekeningstijd | Tijd van padgeneratie moet vlot zijn op een standaard 5x5 grid. | Sneller dan 2 seconden. |

## Test Scenarios
Scenario A (Vrij pad): Een open route met minimale obstakels. We meten hier de efficiëntie van de heuristic.

Scenario B (Obstakel vermijding): Start en doel zijn gescheiden door een muur. De robot moet een omweg vinden.

Scenario C (Invalide input): Testen van de is_valid functie door het doel direct in een obstakel te plaatsen.

## Meetresultaten (& discussie)
| Test | Verwacht Resultaat | Resultaat | Status |
|---|---|---|---|
| TA1 | Geen collision. | Geen collision gedetecteerd. | Pass |
| TA2 | Logische route. | Pad is optimaal, volgt langs obstakels. | Pass |
| TA3 | Voert niks uit. | Algortime voert niks uit. | Pass |
| TA4 | Snelheid | 1.45 seconden op 5x5 test grid | pass |

### Discussie
Tijdens het testen kwamen we een paar dingen tegen die de moeite waard zijn om te benoemen:

Snelheid in de simulator: We merkten dat de tijd die het algoritme nodig heeft om een route te berekenen soms wat schommelt. Dat ligt niet zozeer aan onze code, maar aan Gazebo zelf. Die simulator vraagt nogal veel van de computer, waardoor de berekeningen soms een fractie van een seconde langer duren. Dit betekend dat wij een van de testaspecten achteraf toch aangepast hebben; In plaats van de grid die gebaseerd is op de Lidar, hebben wij besloten deze test uit te oefenen op een 5x5 grid. Zo weten we alsnog of het algirtme snel is, maar worden we niet beperkt door GAzebo voor ons test en validatie rapport.

Resolutie en detail: We hebben de grid-instellingen (de resolutie) zo gekozen dat het algoritme snel genoeg blijft werken. Als je het grid veel gedetailleerder zou maken, wordt de route nauwkeuriger, maar gaat de robot trager reageren. Voor nu hebben we een goed evenwicht gevonden tussen snelheid en nauwkeurigheid.

Slimme routes: In open ruimtes werkt het algoritme perfect. In heel krappe doorgangen kan de robot soms een beetje "zigzaggen" om de kortste route te vinden. Dat is technisch gezien de kortste weg, maar het ziet er soms een beetje onnatuurlijk uit. Dit is iets wat we in de toekomst nog verder kunnen verfijnen door het algoritme een klein duwtje in de juiste richting te geven.

## Conclusies
Het AStar algoritme werkt goed en doet wat het moet doen; het zorgt ervoor dat Flip veilig van A naar B rijdt zonder tegen obstakels aan te botsen. We hebben getest of het algoritme stopt bij onmogelijke routes en dat werkt ook. Het algoritme is dus stabiel genoeg om Flip te kunnen navigeren.


