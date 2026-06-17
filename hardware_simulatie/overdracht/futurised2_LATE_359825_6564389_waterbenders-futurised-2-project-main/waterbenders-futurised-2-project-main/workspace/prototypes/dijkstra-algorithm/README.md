# Dijkstra Algorithm
*13/06/2026* <br>
*Sarah Gbagi*

# Table of contents
- [What's in this folder](#whats-in-this-folder)
- [Reasoning](#reasoning)
    - [1. What is Dijkstra's Algorithm](#what-is-dijkstras-algorithm)
    - [2. Why the upgrade from Breadth-First Search](#why-the-upgrade-from-breadth-first-search)
- [Implementation](#implementation)
    - [1. Dijkstra code explained in more detail](#dijkstra-algorithm)
    - [2. Mainloop](#mainloop)
    - [3. Reading route](#reading-route)
- [Setup](#setup)
- [Advice](#advice)
- [Source](#source)

# What's in this folder
Inside this folder you will find a test version of the Dijkstra code that can be run directly via the terminal. This test script was made to experiment with the pathfinding logic before fully embedding the finalized code into the main robot system.

This code was later implemented into the main robot system which you can find [here](../../models/ros/packages/path_planning/path_planning/main.py)

# Reasoning
At the start of the project, the Breath First Search Algorithm was implemented. Eventually, this was upgraded to the Dijkstra Algorithm so the robot could drive more smoothly and efficiently.

## What is Dijkstra's Algorithm
Dijkstra's algorithm is a smart way to find the absolute shortest path between two points on a grid map.

Here is how it works step by step:
1. **Starting Point:** It gives the robot's current position a distance score of 0. It gives every other square on the map a starting score of "infinity" (meaning it doesn't know the distance yet).
2. **Checking Neighbors:** The robot looks at the squares right next to it and calculates the distance to them.
3. **Choosing the Shortest Step:** It picks the unvisited square that is closest to the start. From that new square, it looks at the next set of neighbors.
4. **Updating the Scores:** If it finds a new path to a square that is shorter than the old path, it replaces the old score with the new, shorter one.
5. **Finishing:** It repeats this loop until it has checked the squares and found the best, shortest route possible.

## Why the upgrade from Breadth-First Search
While BFS (Breadth-First Search) worked fine at the beginning, it had a few problems that made the robot struggle in the environment:

- **BFS is Blind to Costs:** BFS thinks that moving straight and moving diagonally take the exact same amount of effort. Dijkstra knows diagonals are longer and calculates them correctly.
- **BFS drives too close to obstacles:** BFS only cares about using the fewest number of grid squares. Because of this, it will often plan a path that scrapes right against a wall if it is shorter. Dijkstra checks our "costmap" (obstacle buffer) and stays a safe distance away from walls.

# Implementation
The **Dijkstra** function is written in Python using a **Priority Queue** to make sure it always processes the safest and lowest cost movements first. 

Instead of checking every single square on the map randomly the code uses a priority queue to sort positions by their total *cost score.* 
- It starts by putting the robot's current position into the queue with a score of *0.0*.
- It uses two dictionary lists (*came_from* and *cost_so_far*) to keep track of the history of where the robot has been and how much effort it took to get there.

The algorithm runs a while loop that keeps going as long as there are squares left to check in the queue. For every square it looks at, it uses the *find_neighbouring_cells* function to check all 8 surrounding directions (up, down, left, right, and all four diagonals).

Before doing any math on a neighboring square, the code looks at *self.costmap*. If a square has any value other than 0 (meaning it is a wall, a corner, or an obstacle), the code hits a continue statement. This instantly skips the "dangerous" square, ensuring the robot never plans a path that cuts corners too close to walls.

For squares that are safe, the code calculates *new_cost* using a math formula:
```python
new_cost = cost_so_far[current] + (0.8 * distance_to_robot + 0.2 * rotation_to_robot) + step_cost
```

The loop instantly breaks the moment it steps onto an unmapped square (-1) that meets your distance rule:
```python
if occupancy_grid[ni] == -1 and distance_to_robot >= self.DISTANCE_TO_FRONTIER:
```
Once this target is found, a while loop runs backward through the *came_from records*. It collects all the grid coordinates, flips them into the correct order using path.reverse(), and hands the clean list of coordinates over to the movement controller.

## Dijkstra code explained in more detail
For the initialization of "infinite distances" **Dicts** are used. Everything that is not yet know has an infinite distance. 

With **frontier = Queue()** a queue is created. This is where to put all the points that still need to be visited. The queue automatically ensures that the point with the shortest distance is always at the front.

Using **frontier.put((0.0, start))** the starting node is added to the queue and assigned a distance of (0,0), in other words: (distance, point).

Two empty dicts are created: **came_from = dict()** and **cost_so_far = dict()**. **came_from** remembers which point came before a specific point. **cost_so_far** keeps track of the shortest known distance from the starting point.

**came_from[start] = None** and **cost_so_far[start] = 0.0** register the starting values in the dicts. The starting point has no predecessor **(None)** and the distance to itself is 0.0. All other points in the matrix that are not inside **cost_so_far** theoretically have a distance of infinity at this moment.

**current = start** sets the starting point for the initial node of exploration.

## Mainloop

**while not frontier.empty()** ensures the loop continues as long as there are nodes in the frontier to explore.

With **if not edge_cells: break** if all unknown frontiers on the map have already been processed, the algorithm does not need to calculate the entire rest of the world and stops earlier instead.

With **current_cost, current = frontier.get()** the algorithm picks the unvisited point that lies closest to the starting point. The queue immediately gives the point with the absolute lowest current_cost known at that moment using .get(). This point now becomes the current position (current).

**if current in edge_cells: edge_cells.remove(current)** if the chosen closest point is one of the edge cells, remove it from the list of edge cells.

With **neighbours = find_neighbouring_cells(grid, current[0], current[1], diagonals=True)** you get back a list of all 8 cells that lie directly around the current point.

With **for ni, step_cost in neighbours:** the code loops through all the neighbors. **ni** is the coordinate of the neighbor and **step_cost** is the distance to get there (1.0) for straight and (1.414) for diagonal. This is why the logic of the function **find_neighbouring_cells** was adjusted to also make diagonal movements.

With **if grid[ni] == 100: continue** the code ignores the neighbor if it is an obstacle (100).

With **new_cost = cost_so_far[current] + step_cost** the code takes the distance it had already traveled to get to the current point (cost_so_far[current]) and adds the step to the neighbor (step_cost) to it. This becomes a possible new route.

With **if ni not in cost_so_far or new_cost < cost_so_far[ni]:** the code checks whether it has never visited this neighbor before (not in cost_so_far) AND whether its newly calculated *new_cost* is shorter than the route it had previously saved for this neighbor.

With **cost_so_far[ni] = new_cost** if the route is shorter, the old distance is overwritten with the new, shorter distance (new_cost).

**priority = new_cost** and **frontier.put((priority, ni))** ensures that when the algorithm finds a shorter route to this point, it places this point into the queue again. Now it will explore this point faster.

**came_from[ni] = current** to get to neighbor *ni* the fastest way, you have to loop from the point *current*. This is important for finding the route back later.

## Reading route
Create an empty list with **path = []**.

**if current not in came_from and current != start: return [start]** if the algorithm has stopped but a valid route to a goal was never found, then return the starting point to flip.

**while current != start and current is not None: path.append(current) current = came_from.get(current)** ensures the code loops backward using **came_from**. It then adds the current point to the route and check who the predecessor was via **came_from.get(current)**. It repeats this process until it ends up back at the starting point.

With **path.append(start)** and **path.reverse()** add the starting point as the last item to the list. Because the code has been worked from back to front, the route is currently in the wrong order. With **path.reverse()** flip the list around so that the route is correct.

Finally, return the route with **return path**.

# Setup
For the full setup of the code you can navigate to the [Path-finding README](../path-finding-demo/README.md) for more details.

# Advice
For the advice of the code navigate to the [Path-finding README](../path-finding-demo/README.md) for more details. This also includes the advice for Dijkstra
# Source
D, W. (2018, juli 24th). How do you program diagonal movement? Game Development Stack Exchange. https://gamedev.stackexchange.com/questions/162045/how-do-you-program-diagonal-movement

GeeksforGeeks. (2026, januari 21th). Dijkstra’s algorithm. GeeksforGeeks. https://www.geeksforgeeks.org/dsa/dijkstras-shortest-path-algorithm-greedy-algo-7/

Moving Diagonally Within a Grid. (2023, december 16th). GameMaker. https://forum.gamemaker.io/index.php?threads/moving-diagonally-within-a-grid.107759/

Patel, A. J. (2014). Introduction to the A* Algorithm. https://www.redblobgames.com/pathfinding/a-star/introduction.html

Wikipedia-bijdragers. (2025, december 20th). Kortstepad-algoritme. Wikipedia. https://nl.wikipedia.org/wiki/Kortstepad-algoritme

