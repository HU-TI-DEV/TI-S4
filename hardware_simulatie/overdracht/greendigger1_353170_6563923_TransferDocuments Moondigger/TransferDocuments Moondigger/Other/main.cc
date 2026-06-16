#include "aStar.cc"
#include "driving.cc"
#include "objectRecognition.hpp"
#include "poseSubscriber.hpp"

#include <iostream>
#include <vector>
#include <utility>
#include <thread>
#include <chrono>
#include <cmath> // For std:round


class ProcessController{
public:
    ProcessController(PoseSubscriber &poseSub) : 
    poseSubscriber(poseSub),
    pathfind(row_length, column_length), 
    courier(current_x, current_y),
    objectRecognition(poseSubscriber)
    {
        mainFunction();
    }

private:
    const int row_length = 150;
    const int column_length = 50;

    const int bunds_per_row = 15;
    const int rows_of_bunds = 5;

    int current_x = 0;
    int current_y = 0;

    bool at_goal = false;
    std::vector<std::pair<int,int>> path;

    PoseSubscriber& poseSubscriber;
    AStar pathfind;
    GoToPointController courier;
    ObjectRecognition objectRecognition;

    void mainFunction(){    
        pathfind.setStart(current_x, current_y);

        std::vector<std::pair<int,int>> poi = POIPositions(bunds_per_row, rows_of_bunds);
        std::cout << "=== " << poi.size() << " POI punten berekend ===\n";
        
        for(int poi_index = 0; poi_index < (int)poi.size(); poi_index ++){
            int poi_x = poi[poi_index].first;
            int poi_y = poi[poi_index].second;

            if(!findObstacles(poi_x, poi_y)){continue;}
            std::vector<std::pair<int,int>> concise_path = simplifyPath(path);
            courier.loadPath(concise_path); 
            courier.reached = false;

            while(!courier.reached){
                // TODO: Change this to take longer between obstacle checks
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                std::vector<std::pair<int,int>> new_obstacles = objectRecognition.obstacles;
                objectRecognition.obstacles.clear();
                if(!new_obstacles.empty()){
                    bool obstacleAdded = false;
                    for(auto& obs : new_obstacles){
                        if(pathfind.setObstacle(obs.first, obs.second)){
                            obstacleAdded = true;
                        }
                    }
                    if(obstacleAdded){ // Replan only when there is a new obstacle
                        // std::cout << "[OBSTACLE] Nieuw obstakel gedetecteerd, herplannen...\n";
                        // std::cout << "Positie AMP: (" << poseSubscriber.getX() << ", " << poseSubscriber.getY() << ")\n";
                        // std::cout << "Posities obstakels:\n";
                        // for (const auto& obs : new_obstacles) {
                        //     std::cout << "(" << obs.first << ", " << obs.second << ")\n";
                        // }
                        current_x = std::round(poseSubscriber.getX());
                        current_y = std::round(poseSubscriber.getY());
                        if(!replan(current_x, current_y, poi_x, poi_y)){break;} // Replan, if POI is unreachable, skip to next one
                        courier.loadPath(simplifyPath(path));
                    }
                }
            }
            current_x = std::round(poseSubscriber.getX());
            current_y = std::round(poseSubscriber.getY());
        }
    }


    std::vector<std::pair<int,int>> simplifyPath(const std::vector<std::pair<int,int>>& path){
        if (path.size() <= 2){
            std::cout << "[SIMPLIFY] Nieuw pad gevonden: " << path.size() << " stap(pen)\n"; 
            return path;
        } 
        std::vector<std::pair<int,int>> simplified;
        // simplified.push_back(path[0]); // We can skip the first point since it's the current position of the AMP, we will update this every time we replan

        for (int i = 1; i < (int)path.size() - 1; i++){
            // Direction from previous kept point to current
            int x_in = path[i].first - path[i-1].first;
            int y_in = path[i].second - path[i-1].second;
            // Direction from current to next
            int x_out = path[i+1].first - path[i].first;
            int y_out = path[i+1].second - path[i].second;
            // If the two are in line this will not push back
            if (x_in * y_out != x_out * y_in){simplified.push_back(path[i]);}
        }
        simplified.push_back(path.back());
        std::cout << "[SIMPLIFY] Nieuw pad gevonden: " << simplified.size() << " stap(pen)\n";
        return simplified;
    }


    bool replan(int current_x, int current_y, int target_x, int target_y){
        path.clear();
        pathfind.setStart(current_x, current_y);
        pathfind.setGoal(target_x, target_y);
        // Voer A* uit en sla het resultaat op
        bool found = pathfind.findGoal();
        path = pathfind.getPath();

        // Als het pad leeg is kan het doel niet bereikt worden
        if (path.empty()){
            std::cout << "[REPLAN] Geen pad mogelijk naar dit POI.\n"; 
            // Toon het foutieve pad op het grid
            // pathfind.printGrid();
            return false;
        }

        std::cout << "[REPLAN] Nieuw pad gemaakt!\n";
        // Toon het nieuwe pad op het grid
        // pathfind.printGrid();
        return true;
    }

    bool findObstacles(int target_x, int target_y){
        std::vector<std::pair<int,int>> found_obstacles = objectRecognition.obstacles;
        objectRecognition.obstacles.clear();
        if(!found_obstacles.empty()){
            for(std::pair<int,int>& obstacle : found_obstacles){
                pathfind.setObstacle(obstacle.first, obstacle.second);
            }   
        }
        // Bereken het initiële pad van huidige positie naar dit POI
        // Eventueel gevonden obstakels zijn nu al verwerkt in het grid
        path.clear();
        if (!replan(current_x, current_y, target_x, target_y)){
            std::cout << "[SKIP] POI Cannot be reached\n"; return false;
        }
        return true;
    }

    std::vector<std::pair<int,int>> POIPositions(int poi_per_row, int rows_of_poi){
        std::vector<std::pair<int,int>> positions;
        for(int j = 0; j < rows_of_bunds; j++){
            // Even rij: links -> rechts
            if(j % 2 == 0){
                for(int i = 0; i < poi_per_row; i++){
                    positions.push_back({i * 10, j * 10});
                }
            }
            // Oneven rij: rechts -> links met +5 offset
            else {
                for(int i = poi_per_row - 1; i >= 0; i--) {
                    positions.push_back({i * 10 + 5, j * 10});
                }
            }
        }
        return positions;
    }
};


int main(){
    const std::string pose_topic = "/model/vehicle/pose";
    PoseSubscriber poseSubscriber(pose_topic);
    ObjectRecognition ObR(poseSubscriber);
    std::thread controlThread([&poseSubscriber]() { ProcessController process(poseSubscriber); });
    while (true){
        cv::Mat boxed = ObR.getLatestBoundingBoxedImage();
        if (!boxed.empty()) {cv::imshow("Boxes", boxed);}
        if (cv::waitKey(1) == 27) {break;}
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    cv::destroyAllWindows();
    return 1;
}