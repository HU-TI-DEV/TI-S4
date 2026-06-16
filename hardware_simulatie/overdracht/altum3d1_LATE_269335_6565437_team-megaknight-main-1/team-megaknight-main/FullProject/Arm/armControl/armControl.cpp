#include "armControl.hpp"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <stdexcept>

// ─── Constructor ─────────────────────────────────────────────────────────────

ArmControl::ArmControl(gz::transport::Node&    node,
                       const MotorJointConfig& pivot_arm1_cfg,
                       const MotorJointConfig& arm1_arm2_cfg)
    : pivot_arm1_("pivot_arm1", node, pivot_arm1_cfg)
    , arm1_arm2_ ("arm1_arm2",  node, arm1_arm2_cfg)
{}

// ─── setAngle / getAngle ─────────────────────────────────────────────────────

std::future<void> ArmControl::setAngle(Joint joint, double target_rad)
{
    switch (joint)
    {
        case PIVOT_ARM1: return pivot_arm1_.setAngle(target_rad);
        case ARM1_ARM2:  return arm1_arm2_ .setAngle(target_rad);
        default:
            throw std::invalid_argument("[ArmControl] Unknown joint index");
    }
}

double ArmControl::getAngle(Joint joint) const
{
    switch (joint)
    {
        case PIVOT_ARM1: return pivot_arm1_.getAngle();
        case ARM1_ARM2:  return arm1_arm2_ .getAngle();
        default:
            throw std::invalid_argument("[ArmControl] Unknown joint index");
    }
}

bool ArmControl::isReady() const
{
    return pivot_arm1_.isReady() && arm1_arm2_.isReady();
}

// ─── inverseKinematics ───────────────────────────────────────────────────────

std::array<std::future<void>, 2>
ArmControl::inverseKinematics(double reach, double height)
{
    const double L1 = 1.1495;
    const double L2 = 1.65;

    const double dist_sq = reach * reach + height * height;
    const double dist    = std::sqrt(dist_sq);

    if (dist > L1 + L2)
        throw std::runtime_error(
            "[ArmControl::inverseKinematics] Target out of reach: distance "
            + std::to_string(dist) + " > max " + std::to_string(L1 + L2));

    if (dist < std::abs(L1 - L2))
        throw std::runtime_error(
            "[ArmControl::inverseKinematics] Target too close: distance "
            + std::to_string(dist) + " < min " + std::to_string(std::abs(L1 - L2)));

    // Law of cosines: solve for theta2
    const double cos_theta2 = (dist_sq - L1 * L1 - L2 * L2) / (2.0 * L1 * L2);
    const double theta2     = std::acos(std::clamp(cos_theta2, -1.0, 1.0));

    // Solve for theta1 — atan2(reach, height) orients correctly for
    // an arm that starts vertical and reaches forward
    const double alpha  = std::atan2(reach, height);
    const double beta   = std::atan2(L2 * std::sin(theta2),
                                     L1 + L2 * std::cos(theta2));
    const double theta1 = alpha - beta;

    // Negate both — positive Gazebo angles go backward for both joints
    std::array<std::future<void>, 2> futures;
    futures[0] = pivot_arm1_.setAngle(-theta1);
    futures[1] = arm1_arm2_ .setAngle(-theta2);
    return futures;
}