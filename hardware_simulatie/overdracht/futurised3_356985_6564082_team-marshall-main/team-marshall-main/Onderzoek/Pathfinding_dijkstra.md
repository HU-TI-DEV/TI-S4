Pathfinding met het dijkstra algoritme
--

Met pathfinding (vooral in games) werkt je niet met losse steden, maar met een grid (raster van tegels).

- Elke tegel is een node
- De verbindingen naar de buren (omhoog, omlaag, links, rechts) zijn de *edges*.
- Normale tegel gewicht van 1
- Tegel met modder of water gewicht van 5 of meer.
- Muur gewicht van oneindig (∞).

A* (A-star) is de verbeterde versie van dijkstra
- Dijkstra zoekt in alle richtingen tegelijk. Heel nauwkeurig, maar kost veel meer rekenwerk.
- A* doet hetzelfde, maar heeft een 'vermoeden' waar het doel is. Hierdoor zoekt hij gerichter in de juiste richting.

Robot operating system Ros2.
2 opties:
1. snel met nav2
2. leerzaam (zelf programmeren in python)

#### Optie 1 nav2
Dijkstra zit ingebouwd als "global planner". Je voert een kaart (occupancy grid) in, en nav2 rekent met Dijkstra uit hoe de robot van A naar B komt met muren ontwijken.

#### Optie 2 zelf
De robot gebruikt dan een lidar om de wereld te zien en zet deze om en zet deze om naar een grid met mapping. Dijkstra berekent dan de kortste route, en de robot moet dan commands krijgen zodat die gaat rijden.

We moeten een grid maken waarbij:
0 = vrije ruimte (gewicht 1)
1 = obstakel / muur (gewicht ∞)