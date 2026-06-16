#include <iostream>
#include <cmath>
#include "calc_Functions.hh"


// From this website is the explaination of Inverse Kinematics and pseudocode used in the setTargetPoint function
// link: https://motion.cs.illinois.edu/RoboticSystems/InverseKinematics.html 
// The pseudocode is from the 2D 2-link problem, our arm has 2 links but 3 dimentions. We came up with the first part
// of the function that determents the q1 angle to line the arm up with the setpoint. 

const double pi = 3.14159265358979323846;

double squared(double number){ //usefull help function
    return number*number;
}

void setTargetPoint(double x, double y, double z, double L1, double L2, double& q1, double& q2, double& q3){
    double r = std::sqrt(squared(x) + squared(y));
    double Xd2 = squared(r) + squared(z);
    double c2 = (Xd2 - squared(L1) - squared(L2)) / (2 * L1 * L2);

    if (c2 > 1 || c2 < -1) {
        std::cout << "unreachable point\n";
        return;
    }

    double theta = atan2(z, r);

    if(c2 == 1){ // arm streched fully
        q2 = theta;
        q3 = 0;
        return;
    }

    if(c2 == -1 && r!=0){ // arm closed
        q2 = theta;
        q3 = pi;
        return;
    }

    if(c2 == -1 && r==0){ // arm closed, on shoulder joint
        q3 = pi;
        return;
    }
    // For this project we decided to only do the elbow-up calculation:
    q1 = atan2(y, x);
    q3 = std::acos(c2);
    q2 = theta - atan2((L2 * sin(q3)), (L1 + L2 * cos(q3)));
}

std::vector<point> pointGenerator(float z_coordinate, float radius, int amount_setpoints){
    std::vector<point> points;

    if (amount_setpoints < 1){
        std::cout << "not enough setpoints to generate";
        return points;
    }

    // angle step over half circle (0 to pi)
    float angle_step = pi / (amount_setpoints - 1);

    for (int i = 0; i < amount_setpoints; i++){
        float theta = i * angle_step;

        float x = radius * std::cos(theta);
        float y = radius * std::sin(theta);

        if (y <0){
            y = 0;
        }

        points.push_back(point{x, y, z_coordinate});
    }

    return points;
}