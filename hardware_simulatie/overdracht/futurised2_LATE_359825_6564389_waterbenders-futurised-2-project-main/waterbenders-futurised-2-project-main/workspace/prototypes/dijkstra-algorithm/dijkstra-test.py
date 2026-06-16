from queue import PriorityQueue
import numpy as np

def find_neighbouring_cells(array, iy, ix, diagonals=True):
    height, width = array.shape
    neighbours = []
    
    # Format: (dy, dx) matching (row, col) format of numpy (iy, ix)
    directions = [
        (0, 1),
        (0, -1),
        (1, 0),
        (-1, 0),
        (1, 1),
        (1, -1), 
        (-1, 1),
        (-1, -1) 
    ]
    
    for i, (x, y) in enumerate(directions):
        if diagonals == False and i > 3:
            break
        ny = iy + x
        nx = ix + y
        # Check whether each cell has a neighbour (isn't at the edge of the map)
        if 0 <= nx < width and 0 <= ny < height:
            cost = 1.414 if i > 3 else 1.0
            neighbours.append(((ny, nx), cost))
            
    return neighbours

# Scans the occupancy grid and identifies all free cells (0) adjacent to unknown cells (-1), resulting in frontier edge cells or candidate boundaries
def candidate_boundaries(grid):

    height, width = grid.shape
    candidate_boundaries = []
    
    for iy in range(height):
        for ix in range(width):

            if grid[iy, ix] == 0:  
                for ni, _ in find_neighbouring_cells(grid, iy, ix, diagonals=False):
                    if grid[ni] == -1 and ni not in candidate_boundaries:
                        candidate_boundaries.append(ni)
                        
    return candidate_boundaries

# Source: https://www.redblobgames.com/pathfinding/a-star/introduction.html
# uses a priority queue to explore paths based on their cumulative cost ensuring that it finds the most efficient route to the frontier edge cells while navigating around obstacles and unknown areas
def dijkstra_search(grid, start: tuple):
    edge_cells = candidate_boundaries(grid)
    print(f"Detected Frontier Edge Cells: {edge_cells}")

    if not edge_cells:
        print("No frontier cells found")
        return [start]
    
    frontier = PriorityQueue() 
    frontier.put((0.0, start)) 
    
    came_from = dict()
    cost_so_far = dict()
    came_from[start] = None
    cost_so_far[start] = 0.0
    current = start

    while not frontier.empty():
        if not edge_cells:
            break

        current_cost, current = frontier.get()

        if current in edge_cells:
            edge_cells.remove(current)

        neighbours = find_neighbouring_cells(grid, current[0], current[1], diagonals=True)

        for ni, step_cost in neighbours:
            if grid[ni] == 100:  # Skip obstacles
                continue

            new_cost = cost_so_far[current] + step_cost
            if ni not in cost_so_far or new_cost < cost_so_far[ni]:
                cost_so_far[ni] = new_cost
                priority = new_cost
                
                frontier.put((priority, ni))
                came_from[ni] = current

    # path reconstruction
    path = []
    if current not in came_from and current != start:
        return [start]
        
    while current != start and current is not None:
        path.append(current)
        current = came_from.get(current)
        
    path.append(start)
    path.reverse()
    
    return path

# TEST 
if __name__ == "__main__":
    
    # Values meaning:
    # -1 = unknown
    # 0  = free
    # 100 = occupied

    # Width of 4 and height of 3
    arr = np.array([ 
        [0,  100, 100, -1], 
        [0,  0,   0,   100],
        [-1, 0,   0,   -1]
    ])
    
    start_pose = (0, 0)
    print(f"Starting Dijkstra from: {start_pose}")
    
    generated_path = dijkstra_search(arr, start_pose)
    print(f"Generated Path: {generated_path}")