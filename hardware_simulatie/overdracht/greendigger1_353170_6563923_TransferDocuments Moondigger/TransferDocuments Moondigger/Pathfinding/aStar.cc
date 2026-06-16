#include <iostream>
#include <vector>
#include <cmath>
#include <utility>
#include <limits>
#include <algorithm>
#include <string>

struct Node{
    double g,h,f;
    std::pair<int,int> parent;
    std::pair<int,int>position;
};

class minHeap{
private:
    // By filling the vector from the first possible moment we can keep a 1 indexed heap.
    std::vector<std::pair<double, Node>> heap = {{0, {0,0,0,{0,0},{0,0}}}};

    int findLeftChild(int index){return index * 2;}
    int findRightChild(int index){return index * 2 + 1;}
    int findParent(int childIndex){return childIndex /2;}

    void siftUp(int index){
        int parentIndex = findParent(index);
        if (parentIndex == 0){return;}

        while(index > 1 && heap[parentIndex].first > heap[index].first){
            std::pair<double,Node> parentPair = heap[parentIndex];
            heap[parentIndex] = heap[index];
            heap[index] = parentPair;
            index = parentIndex;
            parentIndex = findParent(index);
        }
    }

    void siftDown(int index){
        double leftPrio;
        double rightPrio;

        int leftChildIndex = findLeftChild(index);
        int rightChildIndex = findRightChild(index);
        int amountOfElements = heap.size();
        
        if (leftChildIndex >= amountOfElements){return;}
        else if (rightChildIndex >= amountOfElements){
            rightPrio = std::numeric_limits<double>::infinity();
            leftPrio = heap[leftChildIndex].first;
        }
        else{leftPrio = heap[leftChildIndex].first; rightPrio = heap[rightChildIndex].first;}

        while(heap[index].first > leftPrio || heap[index].first > rightPrio){
            std::pair<double,Node> storagePair = heap[index];
            // When Prio is equal we choose for left path
            if(leftPrio <= rightPrio){
                heap[index] = heap[leftChildIndex];
                heap[leftChildIndex] = storagePair;
                index = leftChildIndex;
            }
            else if(rightPrio < leftPrio){
                heap[index] = heap[rightChildIndex];
                heap[rightChildIndex] = storagePair;
                index = rightChildIndex;
            }

            // Same code as above while loop. Cant find a reason to work it into the while loop though
            leftChildIndex = findLeftChild(index);
            rightChildIndex = findRightChild(index);
            if (leftChildIndex >= amountOfElements){return;}
            else if (rightChildIndex >= amountOfElements){
                rightPrio = std::numeric_limits<double>::infinity();
                leftPrio = heap[leftChildIndex].first;
            }
            else{leftPrio = heap[leftChildIndex].first; rightPrio = heap[rightChildIndex].first;}
        }
    }

public:

    bool isEmpty(){ return heap.size() == 1; }

    void queue(double prio, Node node){
        heap.push_back({prio, node});
        siftUp((int) heap.size() - 1);
    }

    std::pair<double, Node> dequeue(){
        Node zeroNode = {0,0,0,{0,0},{0,0}}; 
        std::pair<double,Node> zeros = {0, zeroNode};

        if ((int) heap.size() == 1){return zeros;}

        if (heap.size() == 2) { 
            std::pair<double,Node> output = heap[1];
            heap.pop_back();
            return output;
        }

        std::pair<double,Node> output = heap[1];
        heap[1] = heap.back();
        heap.pop_back();
        siftDown(1);
        return output;
    }
};




class AStar{
private:
    int width;
    int height;
    std::vector<std::vector<int>> grid;
    std::vector<std::vector<bool>> closedSet;  // tracks visited nodes

    std::vector<std::vector<Node>> nodeMap;
    std::vector<std::pair<int,int>> path;

    bool startSet = false;
    bool goalSet = false;

    int startX, startY;
    int goalX, goalY;

    bool inBounds(int x, int y){
        if(x >= 0 && x < width && y >= 0 && y < height){return true;}
        return false;
    }

    void resetSearch(){
        closedSet.assign(height, std::vector<bool>(width, false));
        // Set every Node in the nodemap to a nonexisting node
        nodeMap.assign(height,std::vector<Node>(width, {std::numeric_limits<double>::infinity(),0,0,{-1,-1},{-1,-1}})); 
    }

    double calculateHeuristic(double x, double y){
        double euclidianDistance = std::sqrt((goalX-x)*(goalX-x) + (goalY - y)*(goalY - y));
        return euclidianDistance;
    }

    void reconstructPath(int x, int y) {
        path.clear();
        int currentX = x;
        int currentY = y;

        while (!(currentX == startX && currentY == startY)){
            path.push_back({currentX, currentY});
            std::pair<int,int> parent = nodeMap[currentY][currentX].parent;
            currentX = parent.first;
            currentY = parent.second;
        }
        path.push_back({startX, startY});
        std::reverse(path.begin(), path.end());
    }

public:
    AStar(int inputWidth, int inputHeight):
        width(inputWidth), height(inputHeight), 
        grid(inputHeight, std::vector<int>(inputWidth, 0)),
        closedSet(inputHeight, std::vector<bool>(inputWidth, false)),
        nodeMap(inputHeight, std::vector<Node>(inputWidth,{std::numeric_limits<double>::infinity(), 0, 0, {-1,-1}, {-1,-1}}))
        {}

    bool setGoal(int x, int y) {
        // If not in grid
        if(!inBounds(x,y)){return false;}
        // If goal is obstructed
        if(grid[y][x] == -1){return false;}
        grid[y][x] = 1;
        goalX = x; 
        goalY = y;
        return true;
    }

    bool setStart(int x, int y) {
        if(!inBounds(x,y)){return false;}
        // If a start has been set it needs to become a normal node
        if(startSet){grid[startY][startX] = 0;}
        grid[y][x] = 2;
        startSet = true; 
        startX = x; 
        startY = y;
        return true;
    }

    bool setObstacle(int x, int y){
        if(!inBounds(x,y)){return false;}
        if(grid[y][x] == -1){return false;}
        grid[y][x] = -1;
        return true;
    }

    std::vector<std::pair<int,int>> getPath(){return path;}

    bool moveStart(int x, int y){
        if(!inBounds(x,y)){return false;}
        // Old start needs to become normal Node
        if(startSet){grid[startY][startX] = 0;}
        grid[y][x] = 2;
        startX = x;
        startY = y;
        startSet = true;
        
        resetSearch();
        return findGoal();
    }

    bool findGoal(){
        if(!startSet){return false;}
        // Make sure no old path is stored
        resetSearch();

        // We want to establish a minHeap so we can filter based on most promising path.
        minHeap openSet;

        Node startNode = {0, calculateHeuristic(startX, startY), 0, {startX, startY}, {startX, startY}};
        startNode.f = startNode.h + startNode.g;
        nodeMap[startY][startX] = startNode;

        // We start working from the startNode so this is the first in our minheap
        openSet.queue((int)startNode.f, startNode);

        // Every time we need to check all neighbours we check all 8 gridspots next to our amp. This means we need to add these values onto our x and y
        int directions[8][2] = {
            {0,1}, {0,-1}, {1,0}, {-1,0},
            {1,1}, {1,-1}, {-1,-1}, {-1,1}
        };

        // While there are nodes to visit or handle we continue the loop
        while(!openSet.isEmpty()){
            // Take the first node yet to visit and store it in currentPair
            std::pair<int,Node> currentPair = openSet.dequeue();
            Node currentNode = currentPair.second;

            int currentX = currentNode.position.first;
            int currentY = currentNode.position.second;

            if (currentNode.g > nodeMap[currentY][currentX].g){continue;}

            if (currentX == goalX && currentY == goalY){
                reconstructPath(goalX,goalY);
                return true;
            }
            // Mark the coordinate for the current node as visited. 
            closedSet[currentY][currentX] = true; 

            for (int direction = 0; direction < 8; direction ++){
                int newX = currentX + directions[direction][0];
                int newY = currentY + directions[direction][1];

                // Check if node is in bounds
                if (newX < 0 || newY < 0 || newX >= width || newY >= height){continue;}
                // If it is an obstacle we can't visit it
                if (grid[newY][newX] == -1){continue;}
                // If we have already visited the node there is no need to visit it again
                if (closedSet[newY][newX]){continue;}

                // Every step is same cost in our algorithm. Adding weights will add to much complications.
                // We do want to add a different weight for diagonals. Otherwise it would always move diagonally.
                double moveCost = 1.0;
                if (directions[direction][0] != 0 && directions[direction][1] != 0){moveCost = std::sqrt(2);}

                Node neighbour;
                neighbour.g = currentNode.g + moveCost;
                neighbour.h = calculateHeuristic(newX,newY);
                neighbour.f = neighbour.h + neighbour.g;
                neighbour.position = {newX,newY};
                neighbour.parent = {currentX,currentY};

                if (neighbour.g < nodeMap[newY][newX].g){
                    nodeMap[newY][newX] = neighbour;
                    openSet.queue((double)neighbour.f, neighbour);
                }
            }
        }

        int   bestX   = startX;
        int   bestY   = startY;
        double bestDist = std::numeric_limits<double>::infinity();
 
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                if (!closedSet[y][x]) { continue; }  // only consider visited nodes
                double dx = goalX - x;
                double dy = goalY - y;
                double dist = std::sqrt(dx*dx + dy*dy);
                if (dist < bestDist) {
                    bestDist = dist;
                    bestX = x;
                    bestY = y;
                }
            }
        }
 
        // If the best node found is the start itself, no progress is possible at all.
        if (bestX == startX && bestY == startY) {path.clear();} 
        else {reconstructPath(bestX, bestY);}
        return false;
    }
    void printGrid() {
        // Build a set of path positions for O(1) lookup
        std::vector<std::vector<bool>> onPath(height, std::vector<bool>(width, false));
        for (std::pair<int,int> p : path) {
            onPath[p.second][p.first] = true;
        }

        for (int y = 0; y < height; y++) {
            std::string row = "";
            for (int x = 0; x < width; x++) {
                if      (x == startX && y == startY)  { row += "S "; }
                else if (x == goalX  && y == goalY)   { row += "G "; }
                else if (onPath[y][x])                { row += "* "; }
                else if (grid[y][x] == -1)            { row += "# "; }
                else                                  { row += ". "; }
            }
            std::cout << row << "\n";
        }
    }

};