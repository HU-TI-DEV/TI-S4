### Stappen plan
grid -> start, goal  
Heuristic  
Path  

Grid vol nullen  
zet start   
zet goal  
zet obstakels 

find path -> f(n) = g(n) + h(n)  
 g(n) == cost: start tot node  
 h(n) == cost: node tot goal  


### Grid
Eerst op en 5x5 grid:

[[0, 0, 0, 0, 0]  
 [0, 0, 0, 0, 0]  
 [0, 0, 0, 0, 0]  
 [0, 0, 0, 0, 0]  
 [0, 0, 0, 0, 0]]  
> Hierna kunnen we het toepassen op de map


### Python Priority queue
``` python
class pQueue:
    def __init__(self):
        # Layout: [[(x, y), fScore], ...]
        self.heap = []

    def heapUp(self, index):
        parent = (index - 1) // 2 # Gehele deling afgerond naar boven om op de juiste parent uit te komen.
        if index > 0 and self.heap[index][1] < self.heap[parent][1]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index] # Wissel.
            self.heapUp(parent) # Recursie.


    def heapDown(self, index):
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2
        size = len(self.heap)

        if left < size and self.heap[left][1] < self.heap[smallest][1]:
            smallest = left
        if right < size and self.heap[right][1] < self.heap[smallest][1]:
            smallest = right
        
        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index] # Wissel.
            self.heapDown(smallest)


    def queue(self, v , p):
        # Lijst [waarde, prioriteit] toevoegen.
        self.heap.append([v, p])
        self.heapUp(len(self.heap) - 1)

    
    def dequeue(self): 
        # Root uit de queue halen.
        if not self.heap:
            return None

        root = self.heap[0][0]

        lastElement = self.heap.pop()
        if self.heap:
            self.heap[0] = lastElement
            self.heapDown(0)
        
        return root

    def contains(self, v): # (O(n)).
        # De waarde v checken.
        for item in self.heap:
            if item[0] == v:
                return True
        return False
    

    def remove(self, v): # (O(n)).
        # De waarde v uit de queue halen.
        correctValues = []

        for item in self.heap:
            if item[0] != v:
                correctValues.append(item)

        self.heap = correctValues

        # Heap herstellen.
        for i in range(len(self.heap)// 2 - 1, -1, -1):
            self.heapDown(i)


class AStar:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        ''' Grid: 
        0  = leeg, 
        -1 = muur, 
        1  = doel, 
        2  = start. '''
        self.grid
        self.path
        

    def setStart(self, x, y):
        self.startX, self.startY = x, y
        self.grid[y][x] = 2
S

    def setGoal(self, x, y):
        self.goalX, self.goalY = x, y
        self.grid[y][x] = 1


    def setObstacle(self, x, y):
        self.grid[y][x] = -1


    def calculateHeuristic(self, x, y):
        h = math.sqrt((self.goalX - x)**2 + (self.goalY - y)**2)
        return h
    
    def findpath(self)
        openList = pQueue()
        openlist.queue((self.startX, self.startY), 0)
        closedSet = set()
        gScores = {(self.startX, self.startY): 0}
        parent = {}

        while not openList.isEmpty():
            current = openList.dequeue()
            cx, cy = current

            if (cx,cy) ==  (self.goalX, self.goalY):
                self.path = self.reconstructPath(parent, current)
                return self.path
            
            closedSet.add((cx, cy))

            for neighbour in self.getNeighbours(cx, cy):
                nx, ny = neighbour

                    if neighbour in closedSet:
                        continue
                
                    dx, dy = abs(nx - nc), abs(ny - cy)
                    stepCost = math.sqrt(2) if dx == 1 and dy == 1 else 1

                    newG = gScores[(cx, cy)] + stepcost

                    if neighbour not in gScores or newG < gScores[neighbour]:
                        gScores[neighbour = newG]
                        h = self.calculateHeuristic(nx, ny)
                        f = newG + h
                        parent[neighbour] = current

                        if openList.contains(neighbour)
                            openList.remove(neighbour)
                        openList.queue(neighbour, f)

        return []
                
```





### Notes C++
``` C++
#include <vector> // Sowieso nodig voor grid.

struct Node{
    g        start node
    h        euclidean 
    f        g+h
    parent   previous node -> parent.position
    position [x, y]
}


class AStar{
private:
    vector<vector<int>> grid
    int startX,   startY; // Start coordinates.
    int goalX,    goalY;  // Goal coordinates.
    int width,    height; // Grid size.
    int currentX, currentY
    bool start = false;   // check is there is a start.
    
public:
    AStar(width, height); width(widthX), width(widthY), height(heightX), height(heightY), grid(height, (width, 0))
    setStart(int x, int y)    -> grid[x][y] = 1; start = true; startX/Y
    setGoal(int x, int y)     -> if start AND goal != start; grid[x][y] = 2; goalX/Y
    setObstakel(int x, int y) -> if start AND start != obstakel; grid[x][y] = -1;

    findPath()
    calculateHeuristic(x, y, goalX, goalY) // Separate function for heuristic calculation.
    neighbours(x, y) -> return neighbours  // Nodes next to current position. Including parent
};


findPath(){
    if current is None: current = start
    pair neighbours[8] = neighbours(current)
    fir (neighbour in neighbours){
        if (neighbour not in visited){
            priorityqueue.push(neighbour)
        }
    }
}
```



