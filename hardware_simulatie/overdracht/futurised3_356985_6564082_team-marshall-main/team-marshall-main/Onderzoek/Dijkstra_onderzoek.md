Dijkstra's algoritme
--

### Wat is Dijkstra's algoritme?
Dijkstra' s algoritme ofwel dijkstra's kortste pad algoritme wordt gebruikt om de minimale afstand van een startende node naar elke andere node in een gewogen graph met non negative edge weights (hier stukje verder nog uitleg over) te vinden. Je kunt een node zien als een specifieke plek op een kaart, zoals een stad, een kruispunt of je eigen huis. Als de lijnen de wegen zijn, dan zijn de nodes de plekken waar die wegen langs samenkomen of eindigen. Dit wordt ook gebruikt bij gps, hierbij wordt dan de kortste route berekent door mogelijke wegen te evalueren en het pad kiezen met het minst aantal kilometer of tijd. 

### Non negative edge weights betekenis
Dit betekent dat elk pad of connectie tussen 2 punten een "kost" dat of 0 of een positieve waarde heeft. Er zijn geen negatieve kosten. Het is de grens tussen algoritmes  dat super snel zijn en die complex en sloom zijn.

Je kan het zien als fysieke metingen, in het echt kunnen de meeste dingen niet negatief zijn:
- Afstand: Je kan niet -5 kilometer reizen
- Tijd: Iets kan niet -10 minuten duren
Bij het dijkstra algoritme is dit hetzelfde.

#### Probleem met negatieve gewichten
Als er negatieve gewichten zijn kun je in een negatieve cyclus terecht komen. Hierbij is de totale som van gewichten kleiner dan 0. Als een algoritme het kortste pad zoekt, gaat die oneindig door de loop heen en blijft die maar doorgaan. Daarmee maakt die het pad "korter" (-∞) met elk rondje. Niet negatieve gewichten zorgen ervoor dat met elke stap je pad langer wordt of hetzelfde blijft.

| Feature | Dijkstra’s Algorithm | Bellman-Ford Algorithm |
| :--- | :--- | :--- |
| **Edge Weight Requirement** | Must be non-negative (>= 0) | Can handle negative weights |
| **Speed** | Very Fast (O(E log V)) | Slower (O(VE)) |
| **Core Logic** | **Greedy**: Once a node is visited, its shortest path is locked in. | **Relaxation**: Re-checks paths multiple times just in case. |

Omdat Dijkstra een 'greedy' (hebzuchtig) algoritme is, gaat het ervan uit dat de kortste weg naar een punt definitief is zodra die node bezocht is. Negatieve gewichten zouden deze logica breken, omdat een weg die in eerste instantie langer lijkt, later ineens 'goedkoper' zou kunnen worden door een negatief getal.

### Verder met Dijkstra's algoritme
Dit algoritme onderzoekt vanaf de source node en update steeds de waarde met het kortste pad naar elke node totdat de optimale route is gevonden. Hierdoor wordt altijd de kortste route gevonden. De source node is de node waar het algoritme start.

Dit algoritme kiest steeds de node met de kleinste 'known distance' en breidt vanaf daar uit

#### Stap voor stap
Ik ga het nu stap voor stap visueel laten zien. Dit is waarmee we starten. 

![begin](./Files/begin.png)

#### Source node
We hebben A als de source node en starten we dus vanaf daar.

![source_node](./Files/source_node.png)

#### Afstanden
De afstand van de source naar zichzelf is gezet op 0, terwijl de afstanden naar de andere overgebleven nodes (A, B, C, D, E, F) op oneindig (∞) gezet zijn. Dit geeft aan dat ze nog niet bereikbaar zijn. We zetten ze op oneindig omdat we aan het begin van het algoritme nog niet weten of er überhaupt een weg naartoe bestaat. Zodra we een node 'ontdekken', vervangen we die oneindigheid door de echte afstand.

Dit algoritme bekijkt als eerst de nodes naast diegene. De buren zijn C en B en hebben beide een gewicht van 4:
- Afstand tot B = 0 + 4 = 4
- Afstand tot C = 0 + 4 = 4

Nu zijn de waardes van B en C geupdate van ∞ naar 4. Je kunt zien dat van beide de afstanden 4 zijn. Dit algoritme kiest altijd voor degene met de laagste bekende waarde, maar B en C zijn gelijk dus voor nu kiezen we B.

![2e](./Files/2enode.png)

Zoals je kunt zien staan we nu op B. Vanaf B bekijkt die zijn buren en voor nu is de enige nog niet bezochte node C.De afstand van B naar C is 4 + 2 = 6. 

Omdat 6 groter is dan de huidige waarde van C (4) wordt C ook niet aangepast. Het algoritme gaat dan door naar de volgende dus C.

Vanaf node C bekijkt die alle nog niet bezochte buren: D, E en F.

de afstanden zijn: <br>
D = 4 + 3 = 7 <br>
E = 4 + 1 = 5 <br>
F = 4 + 6 = 10

De waardes van D, E en F worden dan ook van ∞ naar hun bekende waardes veranderd want ze zijn lager dan de huidige waarde.

![C](./Files/C.png)

De volgende niet bezochte node met de kleinste waarde is E (afstand 5). Vanaf hier gaan we de onbezochte buren D en F bekijken.

Afstand naar D via E = 5 + 3 = 8 -> Niet kleiner dan huidige waarde van D (7) dus wordt dan ook niet aangepast

Afstand naar F via E = 5 + 3 = 8 -> Dit is kleiner dan de huidige waarde van F (10) dus dit wordt aangepast naar 8

![finale](./Files/finale.png)

De volgende node met de kleinste afstand is D (afstand van 7, namelijk vanaf C: 4 + 3 = 7). De enige buur die nog niet bezocht is vanaf D is F

Afstand van D naar F = 7 + 2 = 9 -> Dit is kleiner dan de huidige waarde van F (8) dus deze wordt niet aangepast.

Nu is alles bezocht en stopt het algoritme.

Kortste route tot alle nodes:

A = 0 <br>
B = 4 <br>
C = 4 <br>
D = 7 <br>
E = 5 <br>
F = 8 <br>

Dit is een beetje kort en simpel samengevat hoe het dijkstra algoritme werkt.