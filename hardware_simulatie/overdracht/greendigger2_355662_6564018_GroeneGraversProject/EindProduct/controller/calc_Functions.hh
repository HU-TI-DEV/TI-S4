#ifndef CALC_FUNCTIONS_HH
#define CALC_FUNCTIONS_HH
#include <vector>

struct point { // useful struct to store coordinates
    float x;
    float y;
    float z;
};
void setTargetPoint(double x, double y, double z, double L1, double L2, double& q1, double& q2, double& q3);

std::vector<point> pointGenerator(float z_coordinate, float radius, int amount_setpoints);

#endif