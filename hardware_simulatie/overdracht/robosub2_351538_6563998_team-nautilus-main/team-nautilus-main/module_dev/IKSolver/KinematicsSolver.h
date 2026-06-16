#ifndef KINEMATICSSOLVER_H
#define KINEMATICSSOLVER_H

#include <gz/math/Vector3.hh>
#include <gz/math/Pose3.hh>
#include <gz/math/Helpers.hh>
#include <vector>
#include <cmath>
#include <algorithm>
#include <JointDefintions.h>
#include <iostream>

class KinematicsSolver {
private:
    const int iterations = 32;

public:
    // Pass the number of joints to the constructor
    KinematicsSolver(int numJoints) {};

    std::vector<gz::math::Vector3d> computeForwardKinematics(
        const std::vector<double>& jointAngles
    );

    std::vector<double> solveIK(
        const gz::math::Vector3d& targetPos,
        const std::vector<gz::math::Vector3d>& currentJointPositions
    );
};

#endif //KINEMATICSSOLVER_H