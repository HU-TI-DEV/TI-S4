# Technische Documentatie: AStar Pathfinding algoritme
## Architectuur (& keuzeonderbouwing)
Voor de navigatie van Flip is gekozen voor het A (A-Star) algoritme*. Het doel van pathfinding is om van punt A naar punt B te navigeren met de laagste 'kosten'.  

Het systeem is opgebouwd uit drie componenten:
- De Prioriteitswachtrij (pQueue): Een op maat gemaakte datastructuur die zorgt dat we altijd de meest kansrijke volgende stap als eerste berekenen. Dit bespaart rekentijd.
- De Grid-omzetter: Functies die wereld-coördinaten (meters) vertalen naar raster-coördinaten (pixels/cellen) en vice versa, zodat de robot begrijpt waar hij staat.
- De Omgevingsanalyse: De logica die controleert welke cellen begaanbaar zijn en welke aangrenzende cellen (buren) de robot kan bezoeken.

### Keuzeonderbouwing
In de beginfase van het project hebben we naar het Dijkstra algoritme gekeken. het Dijkstra algoritme is een ook een pathfinding algoritme, maar het is 'blind': het zoekt in alle richtingen tegelijk naar het doel, wat erg rekenintensief is.

Het AStar algoritme is de logische verbetering op het Dijkstra algoritme. Het voegt een heuristiek toe (een slimme schatting). Het AStar algoritme kijkt niet alleen naar de kosten die al gemaakt zijn om op een plek te komen (gScore), maar schat ook in wat de afstand tot het einddoel nog is (hScore of heuristic).

Dijkstra: f(n) = g(n) (afgelegde weg)  
AStar:    f(n) = g(n) + h(n) (afgelegde weg en geschatte afstand tot doel) 

Door deze extra informatie 'ziet' het algoritme waar het doel ligt, waardoor het veel minder cellen hoeft te verkennen en aanzienlijk sneller een pad vindt. Al helemaal voor een blusrobot is het *sneller* vinden van een pad ontzettend belangrijk, vandaar was het ook geen moeilijke keuze toen we hoorde over het AStar algortime en zijn we direct overgestapt.

## Mappenstructuur
De code van het algoritme is als volgt te vinden:    
/src  
  /Futurised  
    explorer.py #Bevat Klasse pQueue en AStarPathfinder.

## Code documentatie
### Klasse pQueue
Deze klasse beheert de 'Open Set'. Het maakt gebruik van een min-heap implementatie om efficiënt de node met de laagste fScore (kosten) op te halen. Hierdoor hoeven we niet de hele lijst te sorteren, wat de prestaties enorm verbetert.

**Leermoment:** We hebben deze pQueue volledig zelf geschreven voor extra controle over de data. In een professionele productieomgeving zouden we heapq (Python's standaard library) gebruiken voor hogere performance, maar door het zelf te schrijven hebben we diep inzicht gekregen in hoe padvinden op datastructuur-niveau werkt. 

### Klasse AStarPathfinder
**world_to_grid & grid_to_world:** Deze functies werken als vertalers tussen de fysieke wereld en het interne raster van de robot. De wereld werkt in meters (float), maar ons grid werkt in gehele getallen (indexen). Deze functies schalen de coördinaten aan de hand van de resolution. Voorbeeld: Als de resolutie 0.05m is, wordt een positie van 1.0 meter in de wereld vertaald naar index 20 in het grid.

**is_valid:** De veiligheidscheck. Hier wordt bepaald of een cel begaanbaar is (waarde < 50) of dat er een obstakel aanwezig is.

**get_neighbors:** Berekend de mogelijke stappen. De robot kan horizontaal, verticaal en diagonaal bewegen, waarbij diagonale stappen een hogere kostenfactor (1.414) hebben.