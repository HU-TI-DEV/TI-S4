<img src = ../../images/teamlogo.png align="right" width="135">

# Contributions
This section was both written and programmed fully by Yannick Hogetoorn.

# Pathfinding
Pathfinding or pathing is the search, by a computer application, for the shortest route between two points (Wikipedia, n.d.). How a computer goes about finding this route is completely up to the developer. Each algorithms has its use cases. Finding out which algorithm works for each project can be made a little simpler though. 

The most basic pathfinding algorithms are Breadth First Search (BFS) and Depth First search (DFS). These algorithms are easy to code and will always find a path but can be very slow and memory intensive (Mitic, 2025). A step above this is Dijkstra's algorithm. This is an improvement over the first two algorithms mostly in its speed. This algorithm will always find the shortest path to a goal node even when positive weights are assigned to the paths (Brilliant.org, n.d.). Even though it is an improvement over depth and breadth first search it is still not fast enough and can still be very space inefficient. 
When the goal node of a path is known we can improve the speed of the algorithm drastically. The pathfinding algorithms can then make use of heuristics to find the shortest path to a goal. This shortest path is found based on the direction the goal is in. A* is an excellent example of these algorithms (Ung et al., 2021).

"Why is it of importance to know the difference between these algorithms?" you may ask. When implementing a certain pathfinding algorithm it is important to know what the limitations are and why a certain algorithm is best used. 

## Choices & Clarification
### A*
As explained above the fastest algorithm is one which is capable of using a heuristic function. Since the distance between bunds is a preset distance, it is possible to accurately calculate where the next goal will be. This means the Autonomous Mobile Platform is capable of using a pathfinding algorithm such as A*. The Autonomous Mobile Platform also needs to be able to quickly calculate its next path in order to redirect it from obstacles or to distance itself from dangerous situations. Combine all these factors and the choice to use A* becomes very easy. 

There are also other heuristic pathfinding algorithms out there which could be of use. Some algorithms worth mentioning are Theta* or D*. Theta* for example is an algorithm which is still worth checking out. The algorithm tries to "cut" corners and let the robot drive easier paths (Nash & Koenig, 2015). It is however heavily reliant on a good camera and object recognition algorithm. Since this was not yet established when programming the algorithm it had not been chosen. For D*, the case is pretty similar. The algorithm is truly very promising (wikipedia2, n.d) but was too complex to dive in with no safety net to rely on. D* would be a good choice when continuing to develop this project. 

### DataStructures
In order to use a relatively simple and powerful pathfinding algorithm, the use of a priority queue is quite important. Seeing as importing an entire library for one function is not as space efficient as some would like, a minHeap algorithm was developed by Yannick. This minHeap allows us to access the most promising node at any point and expand upon it. This datastructure is the backbone of A* and is also why the algorithm is so fast. 

### Return types
We have chosen to give a lot of functions return types. This choice was to easily communicate if a function worked or not. Functions similar to findGoal() return false if their goal was not reached. They however, do still program the code into variables. This means that the return types for these functions are meant as messages to future engineers.

## Problems
No real complications were faced throughout this process. We did choose to keep the program as generic as possible so any alteration can be done in a different file. 

## Advice
The algorithm only takes a 2 dimensional area as a movement space. This is a fully intentional choice as the grid GreenDigger has chosen only requires 2 dimensions. It does however, leave edge cases uncatched. Think of the distance between two bunds on a hill. This distance may start to vary depending on the incline of the hill. If any party wants to fully cover this edge case, it is recommended to add a third dimension. 

Any next developers would be advised to implement tricks on top of this algorithm to make the algorithm even more capable. This could be to implement changes such as D* or Theta* does to the algorithm to make it even faster or even better.

If any next developer has any doubts about the MinHeap it is highly encouraged to use an include to do it for you. There is not much difference in performance, but it does make the code a lot more openly accepted.

# Code
The code speaks for itself. We highly recommend continuing the code which is already present and not including too many unnecessary packages. This is the only code file not using any gazebo includes.

[CPP file](./aStar.cc)

# Sources
Wikipedia. (n.d.). Pathfinding. https://en.wikipedia.org/wiki/Pathfinding
Mitic, N. (2025, July 31). Comparing BFS, DFS, Dijkstra, and A* algorithms on a practical maze solver example. https://nemanjamitic.com/blog/2025-07-31-maze-solver/ 
Brilliant.org. (n.d.). Dijkstra's shortest path algorithm. https://brilliant.org/wiki/dijkstras-short-path-finder/ 
Ung, L. W., Hendrawan, H., & Ali, N. A. (2021). A systematic literature review of A* pathfinding. Procedia Computer Science, 179, 507–514. https://www.sciencedirect.com/science/article/pii/S1877050921000399 
Nash, A., & Koenig, S. (2015). Theta*: Any-angle path planning on grids (arXiv:1401.3843). arXiv. https://arxiv.org/pdf/1401.3843 
Wikipedia. (n.d.). D*. https://en.wikipedia.org/wiki/D*