#include <atomic>
#include <csignal>
#include <iostream>
#include <fstream>
#include <string> 
#include <chrono> 
#include <thread> 
#include <cmath>
#include <gz/msgs.hh>
#include <gz/transport.hh>
#include "calc_Functions.hh"
#include "joint_PID.hh"

static std::atomic<bool> g_terminate(false);

void signal_handler(int)
{
    g_terminate = true;
}

bool stopSignal()
{
    std::ifstream file("/workspace/EindProduct/controller/stopSignal.txt");

    int value;
    if (file >> value) {
        std::cout << "Read stop signal value: " << value << std::endl; 
        return value != 0; 
    }
    std::cout << "Failed to read stop signal from file." << std::endl;
    return false;  
}

std::vector<point> points = pointGenerator(0.5f, 2.8f, 6); // (float z_coordinate, float radius, int amount_setpoints)

int main()
{
    std::signal(SIGINT, signal_handler);
    gz::transport::Node node;

    // (setpoint, Kp, Ki, Kd, joint_name, publish_topic, subscribe_topic)
    jointPID slewjoint(0.0, 3.0, 0.0, 0.5, "slew_joint", "/slew_ctrl", "/slew_observer");
    jointPID shoulderjoint(0.0, 1.5, 0.0, 0.1, "shoulder_joint", "/shoulder_ctrl", "/shoulder_observer");
    jointPID elbowjoint(0.0, 1.5, 0.0, 0.1, "elbow_joint", "/elbow_ctrl", "/elbow_observer");

    double q1, q2, q3; //placeholder variables for the angles of the joints, will be used in the setTargetPoint function
    double L1 = 1.73, L2 = 1.73; // Lenght of the arm segments
   
    // Connection via Gazebo 
    slewjoint.activate(node);
    shoulderjoint.activate(node);
    elbowjoint.activate(node);

    while (!g_terminate){

        for(point p : points) { // every point in the vector
            setTargetPoint(p.x*0.1, p.y*0.1, -0.5, L1, L2, q1, q2, q3); // moves arm to base, in line to the next point. -0.5 so it goes up when retracting

            slewjoint.changeSetpoint(q1);
            shoulderjoint.changeSetpoint(q2);
            elbowjoint.changeSetpoint(q3);

            std::this_thread::sleep_for(std::chrono::milliseconds(2500)); // time to move there

            float steps = 10.0;
            for (int i = 1; i <= int(steps); i++){ // move arm to point with 'steps' amount of in between steps
                float percentage = i / steps; // percentage in .n numbers
                setTargetPoint(p.x*percentage, p.y*percentage, p.z, L1, L2, q1, q2, q3);

                slewjoint.changeSetpoint(q1);
                shoulderjoint.changeSetpoint(q2);
                elbowjoint.changeSetpoint(q3);
                std::this_thread::sleep_for(std::chrono::milliseconds(300));
            }

            if (stopSignal()) {std::cout << "Stop signal received!" << std::endl; 
            break;
            }; // seen a tree, 1 in the .txt file
            if (g_terminate) break; // for ctrl C
            
            std::this_thread::sleep_for(std::chrono::milliseconds(2000));
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(2000));
    }
    return 0;
}