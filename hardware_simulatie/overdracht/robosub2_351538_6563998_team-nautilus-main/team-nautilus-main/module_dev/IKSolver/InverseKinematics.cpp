#include "KinematicsSolver.h"


// Helper to normalize angles between [-PI, PI]
inline double normalizeAngle(double angle) {
    while (angle > M_PI)  angle -= 2.0 * M_PI;
    while (angle < -M_PI) angle += 2.0 * M_PI;
    return angle;
}

std::vector<double> KinematicsSolver::solveIK(const gz::math::Vector3d& targetPos,
    const std::vector<gz::math::Vector3d>& currentJointPositions)
{
    // 5-DOF Output: [subToBase, baseToUpperarm, upperarmToForearm, forearmToWrist, wristToHand]
     std::vector<double> relativeJointAngles(5, 0.0);

    //  Joint 0: Yaw (Base Rotation)
    relativeJointAngles[0] = std::atan2(targetPos.Y(), targetPos.X());

    //  Project Target into 2D Arm Plane (r, z)
    double targetRadial = std::sqrt(targetPos.X() * targetPos.X() + targetPos.Y() * targetPos.Y());
    double targetHeight = targetPos.Z();

    //  Extract Kinematic Data Dynamically from Joint Definitions
    // Extract base offsets
    const auto& baseSpec = JOINT_DEFINITIONS[0]; // baseToUpperarm
    double baseRadial = 0.0;
    double baseHeight = baseSpec.translation.Z() + JOINT_DEFINITIONS[1].translation.Z() + 0.1; // -0.0412, height of the arm base in world space

    // Extract link translations relative to parent joints
    const gz::math::Vector3d& upperarmTrans = JOINT_DEFINITIONS[2].translation; // {0.208, 0, -0.0292}
    const gz::math::Vector3d& forearmTrans  = JOINT_DEFINITIONS[3].translation; // {0.235, 0, 0}
    const gz::math::Vector3d& wristTrans    = JOINT_DEFINITIONS[4].translation; // {0.1601, 0, 0}

    // Calculate physical link lengths
    double upperArmLength = upperarmTrans.Length();
    double forearmLength = forearmTrans.Length();
    double wristLength = wristTrans.Length();

    // Put the lengths inside an array, and calculate the total length of the chain.
    std::array<double, 3> lengths = {upperArmLength, forearmLength, wristLength};
    double maximumReach = upperArmLength + forearmLength + wristLength;

    //  Initialize FABRIK Chain to Natural Zero-Pose
    // p[0]: Base, p[1]: Elbow, p[2]: Wrist, p[3]: Hand
    std::vector<std::array<double, 2>> jointPositions2D = {
        { baseRadial, baseHeight },
        { baseRadial + upperarmTrans.X(), baseHeight + upperarmTrans.Z() },
        { baseRadial + upperarmTrans.X() + forearmTrans.X(), baseHeight + upperarmTrans.Z() + forearmTrans.Z() },
        { baseRadial + upperarmTrans.X() + forearmTrans.X() + wristTrans.X(), baseHeight + upperarmTrans.Z() + forearmTrans.Z() + wristTrans.Z() }
    };

    // Array
    std::array<double, 2> fixedBaseOrigin = jointPositions2D[0];
    double distanceFromBaseToTarget  = std::sqrt((targetRadial - baseRadial) * (targetRadial - baseRadial) + (targetHeight - baseHeight) * (targetHeight - baseHeight));
    const int maxIterations = 100;
    const double epsilon = 0.001; // 1mm convergence target

    //  5. FABRIK Execution
    if (distanceFromBaseToTarget > maximumReach) {
        // Target out of reach: Stretch chain fully toward target
        for (size_t i = 0; i < lengths.size(); i++) {
            double deltaRadius = targetRadial - jointPositions2D[i][0];
            double deltaHeight = targetHeight - jointPositions2D[i][1];
            double len = std::sqrt(deltaRadius * deltaRadius + deltaHeight * deltaHeight);
            jointPositions2D[i+1][0] = jointPositions2D[i][0] + (deltaRadius / len) * lengths[i];
            jointPositions2D[i+1][1] = jointPositions2D[i][1] + (deltaHeight / len) * lengths[i];
        }
    } else {
        // Target within reach: Iterate until close enough
        double error = std::sqrt((jointPositions2D[3][0] - targetRadial) * (jointPositions2D[3][0] - targetRadial) + (jointPositions2D[3][1] - targetHeight) * (jointPositions2D[3][1] - targetHeight)); // Distance from the hand position to the target
        int iter = 0;

        while (error > epsilon && iter < maxIterations) {
            // Forward Pass (Hand to Base)
            jointPositions2D[3] = {targetRadial, targetHeight};
            for (int i = 2; i >= 0; i--) {
                double deltaRadius = jointPositions2D[i][0] - jointPositions2D[i+1][0];
                double deltaHeight = jointPositions2D[i][1] - jointPositions2D[i+1][1];
                double segmentLength = std::sqrt(deltaRadius * deltaRadius + deltaHeight * deltaHeight);
                jointPositions2D[i][0] = jointPositions2D[i+1][0] + (deltaRadius / segmentLength) * lengths[i];
                jointPositions2D[i][1] = jointPositions2D[i+1][1] + (deltaHeight / segmentLength) * lengths[i];
            }

            // Backward Pass (Base to Hand)
            jointPositions2D[0] = fixedBaseOrigin;
            for (size_t i = 0; i < lengths.size(); i++) {
                double deltaRadius = jointPositions2D[i+1][0] - jointPositions2D[i][0];
                double deltaHeight = jointPositions2D[i+1][1] - jointPositions2D[i][1];
                double segmentLength = std::sqrt(deltaRadius * deltaRadius + deltaHeight * deltaHeight);
                jointPositions2D[i+1][0] = jointPositions2D[i][0] + (deltaRadius / segmentLength) * lengths[i];
                jointPositions2D[i+1][1] = jointPositions2D[i][1] + (deltaHeight / segmentLength) * lengths[i];
            }

            error = std::sqrt((jointPositions2D[3][0] - targetRadial) * (jointPositions2D[3][0] - targetRadial) + (jointPositions2D[3][1] - targetHeight) * (jointPositions2D[3][1] - targetHeight)); // The error between the hand and the target position
            iter++;
        }
    }

    //  Extract Relative Joint Angles

    // Joint 1: baseToUpperarm (pitch +Y)
    // Compute the world-space angle of segment 1 in the (r, z) plane,
    // then subtract the zero-pose reference angle to get the relative joint angle.
    double shoulderToElbowRadius = jointPositions2D[1][0] - jointPositions2D[0][0];
    double shoulderToElbowHeight = jointPositions2D[1][1] - jointPositions2D[0][1];
    double upperArmRigidOffset = std::atan2(-upperarmTrans.Z(), upperarmTrans.X()); // the angle of the upperarm segment relative to the base in the (r, z) plane at zero pose.
    relativeJointAngles[1] = normalizeAngle(std::atan2(-shoulderToElbowHeight, shoulderToElbowRadius) - upperArmRigidOffset);

    // Joint 2: upperarmToForearm (pitch -Y, inverted)
    double elbowToWristRadius = jointPositions2D[2][0] - jointPositions2D[1][0];
    double elbowToWristHeight = jointPositions2D[2][1] - jointPositions2D[1][1];
    double forearmWorldPitch = std::atan2(-elbowToWristHeight, elbowToWristRadius);
    relativeJointAngles[2] = normalizeAngle(relativeJointAngles[1] - forearmWorldPitch);

    // Joint 3: forearmToWrist (pitch +Y)
    double wristToHandRadius = jointPositions2D[3][0] - jointPositions2D[2][0];
    double wristToHandHeight = jointPositions2D[3][1] - jointPositions2D[2][1];
    double wristWorldPitch = std::atan2(-wristToHandHeight, wristToHandRadius);
    relativeJointAngles[3] = normalizeAngle(wristWorldPitch - forearmWorldPitch);

    // Joint 4: wristToHand
    relativeJointAngles[4] = 0.0;

    return relativeJointAngles;
}