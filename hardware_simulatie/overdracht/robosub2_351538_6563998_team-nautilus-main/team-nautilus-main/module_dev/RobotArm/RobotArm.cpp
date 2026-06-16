#include "RobotArm.hpp"
#include <iostream>


void RobotArm::start() { jointController.start(); }
void RobotArm::stop() { jointController.stop(); }


void RobotArm::onArmTarget(const gz::msgs::Vector3d& msg) {
    if (!autoControl) return;
    setJointTarget(5,M_PI/4);
    setJointTarget(6,-M_PI/4);
    moveToPosition(gz::math::Vector3d(msg.x(), msg.y(), msg.z()));
}

void RobotArm::setJointTarget(int index, double targetRad) {
    jointController.setJointTarget(index, targetRad);
}

void RobotArm::setAllTargets(const std::vector<double>& targetsRad) {
    jointController.setAllTargets(targetsRad);
}

Joint RobotArm::getJoint(int index) {
    return jointController.getJoint(index);
}

std::vector<double> RobotArm::getCurrentPositions() {
    return jointController.getCurrentPositions();
}

std::vector<double>RobotArm::getRealPositions() {
    return jointController.getRealPositions();
}
void RobotArm::moveToPosition(const gz::math::Vector3d& targetPos) {
    // get current arm joint angles
    auto currentAngles = getCurrentPositions();

    // use only the joints from the arm (not the gripper)
    std::vector<double> armAngles;
    for (size_t i = 0; i < currentAngles.size(); ++i) {
        if (JOINT_DEFINITIONS[i].actsInIK){
            armAngles.push_back(currentAngles[i]);
        }
    }
    // calculate current FK positions
    auto currentPositions = solver.computeForwardKinematics(armAngles);

    auto solvedAngles = solver.solveIK(targetPos, currentPositions);

    size_t ikIndex = 0;
    for (size_t i = 0; i < JOINT_DEFINITIONS.size(); ++i)
        if (JOINT_DEFINITIONS[i].actsInIK)
            setJointTarget(i, solvedAngles[ikIndex++]);
}
    // Interactive menu
    void RobotArm::runMenu() {
        while (jointController.isRunning()) {
            std::cout << "\n--- Joint Control Menu ---\n";
            for (int i = 0; i < JOINT_DEFINITIONS.size(); ++i)
                std::cout << "  " << i << ": " << jointController.getJoint(i).getName() << "\n";
            std::cout << "  97: Toggle auto control (CV)\n";
            std::cout << "  98: Test IK (voer coords in)\n";
            std::cout << "  99: Print FK diagnostics\n";

            std::cout << "Choice: ";

            std::string input;
            std::cin >> input;

            if (!std::cin) {
                std::cin.clear();
                std::cin.ignore(1000, '\n');
                continue;
            }

            int choice = -1;
            try { choice = std::stoi(input); } catch (...) {
                std::cout << "Invalid input.\n";
                continue;
            }
            if (choice == 97) {
                autoControl = !autoControl;
                std::cout << "Auto control: " << (autoControl ? "ON" : "OFF") << "\n";
                continue;
            }
            if (choice == 98) {
                double x;
                double y;
                double z;
                std::cin >> x;
                std::cin >> y;
                std::cin >> z;
                moveToPosition(gz::math::Vector3d(x, y, z));
                std::cout << "IK target sent.\n";
                continue;
            }
            // Debug: Get the current angles of the robotic arm
            if (choice == 99) {
                auto currentAngles = getCurrentPositions();

                std::cout << "\n--- Joint Angles ---\n";
                for (int i = 0; i < currentAngles.size(); ++i)
                    std::cout << "  angles[" << i << "] = " << currentAngles[i]
                              << " rad (" << Joint::radiansToDegrees(currentAngles[i]) << " deg)\n";

                std::vector<double> armAngles;
                for (size_t i = 0; i < currentAngles.size(); ++i) {
                    if (JOINT_DEFINITIONS[i].actsInIK){
                    armAngles.push_back(currentAngles[i]);
                    }
                }
                auto points3D = solver.computeForwardKinematics(armAngles);

                std::cout << "\n--- FK Chain ---\n";
                for (size_t i = 0; i < points3D.size(); ++i)
                    std::cout << "  [" << i << "] " << points3D[i].X() << ", "
                              << points3D[i].Y() << ", " << points3D[i].Z() << "\n";

                gz::math::Vector3d endEffector = points3D.back();
                std::cout << "\nComputed Hand Position (X, Y, Z): "
                          << endEffector.X() << ", "
                          << endEffector.Y() << ", "
                          << endEffector.Z() << "\n";
                continue;
            }

            if (choice < 0 || choice >= static_cast<int>(JOINT_DEFINITIONS.size())) {
                std::cout << "Invalid joint index.\n";
                continue;
            }


            // Print information directly from the controller
            jointController.getJoint(choice).printInfo();


            // Fetch limits and convert without using a temporary snapshot object
            std::cout << "  Enter target angle in degrees ["
                      << Joint::radiansToDegrees(jointController.getJoint(choice).getLowerLimit()) << " to "
                      << Joint::radiansToDegrees(jointController.getJoint(choice).getUpperLimit()) << "]: ";

            auto realPositions = getRealPositions();
            std::cout << "  Real pos (Gazebo) : "
                      << Joint::radiansToDegrees(realPositions[choice])
                      << " deg\n";
            double degrees;
            std::cin >> degrees;
            if (!std::cin) {
                std::cin.clear();
                std::cin.ignore(1000, '\n');
                continue;
            }

            setJointTarget(choice, Joint::degreesToRadians(degrees));
        }
    }