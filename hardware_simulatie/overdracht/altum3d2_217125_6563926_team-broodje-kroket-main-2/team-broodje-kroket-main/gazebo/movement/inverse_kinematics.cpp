#include "inverse_kinematics.hpp"
#include <algorithm>

inline constexpr double PI = 3.14159265358979323846;
inline constexpr double L1 = 0.77; // Length of the first arm segment
inline constexpr double L2 = 0.77; // Length of the second arm segment

// curing station: 
// X: -1.6912
// Y: -0.4775
// Z: 0.6908

// table
// X: -1.7011
// Y: -1.2627
// Z: 0.2553

// dryer 
// X: -1.6965
// Y: -1.9387
// Z: 0.7563

// bin
// X: 1.7388
// Y: -1.4156
// Z: 0.3785

// joint:
// X:-0.0650
// Y: 0.0135
// Z: -0.2218

inline constexpr double deg2rad(double degrees) {
    return degrees * PI / 180.0;
}


// affected joints: joint, joint1, joint2





/*
double solveJoint1(Vec3 targetPosition){
    // x1 = L1 * cos(joint1_angle)
    // cos(joint1_angle) = x1 / L1
    // joint1_angle = acos(x1 / L1)


}

double solveJoint2(Vec3 targetPosition){
    // x2 = x1 +l2 * cos(joint1_angle + joint2_angle)
    // cos(joint1_angle + joint2_angle) = (x2 - x1) / l2
    // joint1_angle + joint2_angle = acos((x2 - x1) / l2)
    // joint2_angle = acos((x2 - x1) / l2) - joint1_angle
}

double solveJoint3(Vec3 targetPosition){
    // x = x2 * cos(joint3_angle)
    // cos(joint3_angle) = x / x2
    // joint3_angle = acos(x / x2)

    double x = targetPosition.x;
    double x2 = ...;
    double joint3_angle = acos(x / x2);
    return joint3_angle;
}


Vec3d forwardKinematics(const std::vector<double>& jointAngles) {
    const double joint1_angle = jointAngles[0];
    const double joint2_angle = jointAngles[1];
    const double joint3_angle = jointAngles[2];

    // joint1
    const double x1 = L1 * cos(joint2_angle);
    const double z1 = L1 * sin(joint2_angle);
    // joint2

    const double x2 = x1 + L2 * cos(joint2_angle + joint3_angle);
    const double z2 = z1 + L2 * sin(joint2_angle + joint3_angle);
    // joint

    const double x3 = x2 * cos(joint1_angle);
    const double y3 = x2 * sin(joint1_angle);
    const double z3 = z2;

    return {x3, y3, z3};
}
*/



Vec3d solve_inverse_kinematics(const Vec3d& targetPosition) {
    // base of first revolute joint in world space (from SDF)
    constexpr double BASE_X =  0.000000;
    constexpr double BASE_Y = -1.337465;
    constexpr double BASE_Z =  0.240018;

    const double x = targetPosition.x - BASE_X;
    const double y = targetPosition.y - BASE_Y;
    const double z = targetPosition.z - BASE_Z;

    const double joint1_angle = atan2(y, x);
    const double r = sqrt(x * x + y * y);

    double cos_angle = (L1*L1 + L2*L2 - r*r - z*z) / (2.0 * L1 * L2);
    cos_angle = std::clamp(cos_angle, -1.0, 1.0);
    const double joint2_angle = -acos(cos_angle);
    const double joint3_angle = atan2(z, r) - atan2(L2 * sin(joint2_angle), L1 + L2 * cos(joint2_angle));

    return {joint1_angle, joint2_angle, joint3_angle};
}