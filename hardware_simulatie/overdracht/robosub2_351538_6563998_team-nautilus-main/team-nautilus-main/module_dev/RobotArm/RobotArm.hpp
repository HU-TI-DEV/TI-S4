#pragma once

#include "JointController.hpp"
#include "KinematicsSolver.h"
#include <array>

/**
 * @brief Top-level class where we can add kinematics and user interaction.
 */
class RobotArm {
public:
    RobotArm() : solver(JOINT_DEFINITIONS.size()) {
        if (!armTargetNode.Subscribe("/arm/target", &RobotArm::onArmTarget, this))
            std::cerr << "[RobotArm] Failed to subscribe to /arm/target\n";
        else
            std::cout << "[RobotArm] Subscribed to /arm/target\n";
    }
    void start();
    void stop();
    void runMenu();

private:
    JointController jointController;
    KinematicsSolver solver;
    // Getters
    std::vector<double> getRealPositions();
    Joint getJoint(int index);
    std::vector<double> getCurrentPositions();
    // Setters
    void setJointTarget(int index, double targetRad);
    void setAllTargets(const std::vector<double>& targetsRad);
    void moveToPosition(const gz::math::Vector3d& targetPos);
    // Used for getting info from camera topic, and autonomous control
    gz::transport::Node armTargetNode;
    std::atomic<bool> autoControl{false};
    void onArmTarget(const gz::msgs::Vector3d& msg);
};