#include "JointController.hpp"

#include <chrono>
#include <iostream>

// Joint definitions (limits in radians, from SDF)
void JointController::initJoints() {
        for (const auto& spec : JOINT_DEFINITIONS)
            controllerJoints.emplace_back(spec);
    };

void JointController::initPublishers() {
    // We're using a unique pointer here, Gazebo transport nodes don like being put inside of vectors.
    for (size_t i = 0; i < controllerJoints.size(); ++i) {
        controllerNodes.push_back(std::make_unique<gz::transport::Node>());
        controllerPublishers.push_back(
            controllerNodes[i]->Advertise<gz::msgs::Double>(controllerJoints[i].getTopic())
        );
    }
}

// Publish velocity commands to Gazebo
void JointController::publishAll() {
    for (size_t i = 0; i < controllerJoints.size(); ++i) {
        gz::msgs::Double msg;
        double dir = controllerJoints[i].getDirection();
        msg.set_data(dir);
        controllerPublishers[i].Publish(msg);
    }
}

// Background thread loop for joint updates
void JointController::controlLoop() {
    auto lastTime = std::chrono::steady_clock::now();
    std::this_thread::sleep_for(std::chrono::milliseconds(UPDATE_RATE_MS));

    while (controllerRunning) {
        auto   now       = std::chrono::steady_clock::now();
        double elapsed = std::chrono::duration<double>(now - lastTime).count();
        lastTime = now;

        constexpr double maxElapsed = UPDATE_RATE_MS / 1000.0 * 2.0;
        if (elapsed > maxElapsed) elapsed = maxElapsed;

        {
            std::lock_guard<std::mutex> lock(controllerJointsMutex);

            // Sync PID state met echte Gazebo posities
            {
                std::lock_guard<std::mutex> realLock(controllerRealPosMutex);
                for (size_t i = 0; i < controllerJoints.size(); ++i)
                    controllerJoints[i].setCurrentPos(controllerRealPositions[i]);
            }

            for (auto& joint : controllerJoints)
                joint.updatePosition(elapsed);

            publishAll();
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(UPDATE_RATE_MS));
    }
}

// Public interface
JointController::JointController() {
    initJoints();
    initPublishers();
    initSubscriber();
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
}

JointController::~JointController() {
    stop();
}

void JointController::setJointTarget(int index, double targetRad) {
    if (index < 0 || index >= controllerJoints.size()) {
        std::cerr << "JointController: index " << index << " out of range.\n";
        return;
    }
    std::lock_guard<std::mutex> lock(controllerJointsMutex);
    controllerJoints[index].setTarget(targetRad);
}

void JointController::setAllTargets(const std::vector<double>& targetsRad) {
    std::lock_guard<std::mutex> lock(controllerJointsMutex);
    for (size_t i = 0; i < controllerJoints.size(); ++i)
        controllerJoints[i].setTarget(targetsRad[i]);
}

Joint JointController::getJoint(int index) {
    std::lock_guard<std::mutex> lock(controllerJointsMutex);
    return controllerJoints[index];
}

std::vector<double>JointController::getCurrentPositions() {
    std::lock_guard<std::mutex> lock(controllerJointsMutex);
    std::vector<double> out;
    for (size_t i = 0; i < controllerJoints.size(); ++i)
        out.push_back(controllerJoints[i].getCurrentPos());
    return out;
}

void JointController::start() {
    if (controllerRunning) return;
    controllerRunning    = true;
    controllerLoopThread = std::thread(&JointController::controlLoop, this);
}

void JointController::stop() {
    if (!controllerRunning) return;
    controllerRunning = false;
    if (controllerLoopThread.joinable())
        controllerLoopThread.join();
}

void JointController::initSubscriber() {
    controllerRealPositions.resize(JOINT_DEFINITIONS.size(), 0.0);
    if (!controllerSubscriberNode.Subscribe(
            "/world/robosubSimulationV4/model/robosub/joint_state",
            &JointController::onJointState, this))
        std::cerr << "[JointController] Failed to subscribe to joint state topic\n";
}

void JointController::onJointState(const gz::msgs::Model& msg) {
    std::lock_guard<std::mutex> lock(controllerRealPosMutex);
    for (const auto& joint : msg.joint()) {
        for (size_t i = 0; i < JOINT_DEFINITIONS.size(); ++i) {
            if (joint.name() == JOINT_DEFINITIONS[i].name) {
                controllerRealPositions[i] = joint.axis1().position();
                break;
            }
        }
    }
}

std::vector<double> JointController::getRealPositions() {
    std::lock_guard<std::mutex> lock(controllerRealPosMutex);
    return controllerRealPositions;
}