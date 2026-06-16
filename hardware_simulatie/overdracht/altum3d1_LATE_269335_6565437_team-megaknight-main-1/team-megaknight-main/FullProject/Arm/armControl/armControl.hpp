#pragma once

#include "motorJoint.hpp"

#include <gz/transport/Node.hh>

#include <array>
#include <future>
#include <iostream>

//==============================================================================
// ArmControl
//
// Controls two joints:
//   - pivot_arm1   (joint between the pivot and arm segment 1)
//   - arm1_arm2    (joint between arm segment 1 and arm segment 2)
//==============================================================================

class ArmControl
{
public:
    enum Joint { PIVOT_ARM1 = 0, ARM1_ARM2 = 1 };

    ArmControl(gz::transport::Node&    node,
               const MotorJointConfig& pivot_arm1_cfg,
               const MotorJointConfig& arm1_arm2_cfg);

    // Drive joint to target_rad. Non-blocking.
    std::future<void> setAngle(Joint joint, double target_rad);

    // Returns the current angle (rad) of the requested joint.
    double getAngle(Joint joint) const;

    // Returns true if both joints have received state from Gazebo.
    bool isReady() const;

    // Move the tip to (reach, height) in the arm's local plane.
    //   reach  — horizontal distance from pivot_arm1 (metres)
    //   height — vertical distance from pivot_arm1 (metres)
    std::array<std::future<void>, 2>
    inverseKinematics(double reach, double height);

private:
    MotorJoint pivot_arm1_;
    MotorJoint arm1_arm2_;
};