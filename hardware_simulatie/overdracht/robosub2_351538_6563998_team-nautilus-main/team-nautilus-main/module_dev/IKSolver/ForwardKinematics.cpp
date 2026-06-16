#include "KinematicsSolver.h"


std::vector<gz::math::Vector3d> KinematicsSolver::computeForwardKinematics(
    const std::vector<double>& angles)
{
    std::vector<gz::math::Vector3d> jointPositions;
    jointPositions.reserve(angles.size() + 1);

    gz::math::Pose3d currentPose(0, 0, 0.1, 0, 0, 0); // Set Z to be at 0.1 initially for base offset
    jointPositions.push_back(currentPose.Pos());

    size_t angleIdx = 0; // Tracks position in the angles vector, only incremented for IK-participating joints.
    for (size_t i = 0; i < JOINT_DEFINITIONS.size() && angleIdx < angles.size(); ++i) {
        const JointSpec& spec = JOINT_DEFINITIONS[i];

        if (!spec.actsInIK) {
            continue; // Skip but don't consume an angle
        }

        // Build rotation properly using axis-angle via Quaternion
        gz::math::Quaterniond rotation(spec.rotationAxis, angles[angleIdx]);

        // Compose translation and rotation as a proper transform
        gz::math::Pose3d jointTransform;
        jointTransform.Set(spec.translation, rotation);

        currentPose = currentPose * jointTransform;
        jointPositions.push_back(currentPose.Pos());

        ++angleIdx;
    }
    return jointPositions;
}