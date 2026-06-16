#pragma once

/**
 * @file JointController.hpp
 * @brief Owns all joints, Gazebo publishers, and the background control loop.
 */

#include "Joint.hpp"

#include <array>
#include <atomic>
#include <mutex>
#include <thread>

#include <gz/msgs.hh>
#include <gz/transport.hh>
#include <JointDefintions.h>

class JointController {
public:
    JointController();
    ~JointController();

    /** Set a single joint target by index (radians). */
    void setJointTarget(int index, double targetRad);

    /** Set all joint targets at once called by the IK path. */
    void setAllTargets(const std::vector<double>& targetsRad);

    /** Returns a copy of the joint (safe to call from any thread). */
    Joint getJoint(int index);

    /** Snapshot of all current positions (radians). */
    std::vector<double> getCurrentPositions();
    std::vector<double>  getRealPositions();

    void start();
    void stop();
    bool isRunning() { return controllerRunning.load(); }

private:
    std::vector<Joint>                          controllerJoints;
    std::vector<std::unique_ptr<gz::transport::Node>>            controllerNodes;
    std::vector<gz::transport::Node::Publisher> controllerPublishers;

    std::atomic<bool>  controllerRunning{false};
    std::thread        controllerLoopThread;
    std::mutex         controllerJointsMutex; // Guards controllerJoints across threads

    gz::transport::Node                    controllerSubscriberNode;
    std::vector<double>                   controllerRealPositions;
    std::mutex                             controllerRealPosMutex;
    void initSubscriber();
    void onJointState(const gz::msgs::Model& msg);
    void initJoints();
    void initPublishers();
    void publishAll();
    void controlLoop();
};