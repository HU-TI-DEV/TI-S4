#ifndef IKTEST_JOINTSPEC_H
#define IKTEST_JOINTSPEC_H
#include <string>
#include <vector>
#include <gz/math.hh>

struct JointSpec {
    std::string name;
    std::string topic; // Topic to communicate with Gazebo

    // Set upper and lower limits in radians
    double lowerLimitRad;
    double upperLimitRad;

    // PID Gains
    double kP;
    double kI;
    double kD;

    gz::math::Vector3d translation; // 3D offset factor from previous join tś
    gz::math::Vector3d rotationAxis; // The axis on which the joint rotates, X, Y and Z values. Derived from SDF
    // Checks if the Joint needs to be used in FK/IK calculations
    bool actsInIK;
    bool invertPublish;
};
#endif //IKTEST_JOINTSPEC_H
