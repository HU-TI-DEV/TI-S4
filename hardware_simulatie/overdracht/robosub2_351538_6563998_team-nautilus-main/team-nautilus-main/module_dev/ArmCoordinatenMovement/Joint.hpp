#pragma once

/**
 * @file Joint.hpp
 * @brief Single revolute joint with position tracking and velocity-based control.
 */

#include <string>
#include <cmath>
#include <gz/math.hh>
#include "JointSpec.h"

static const int    UPDATE_RATE_MS     = 100;

class Joint {
public:
    Joint() = default;
    Joint(const JointSpec& spec, double initialPosRad = 0.0);

    // Getters delegate to spec
    const std::string& getName()  { return spec.name; }
    const std::string& getTopic() { return spec.topic; }
    double getLowerLimit()        { return spec.lowerLimitRad; }
    double getUpperLimit()        { return spec.upperLimitRad; }
    double getCurrentPos()        { return jointCurrentPos; }
    double getTargetPos()         { return jointTargetPos; }
    double getDirection()         { return jointDirection; }
    bool   isMoving()             { return std::abs(jointDirection) > 0.000000001; }

    double setTarget(double targetRad);
    void updatePosition(double elapsed);
    void printInfo();
    void setCurrentPos(double pos) { jointCurrentPos = pos; }
    static double degreesToRadians(double deg);
    static double radiansToDegrees(double rad);
    double clamp(double val);

private:
    JointSpec spec;
    static constexpr double MOVE_VELOCITY      = 1.0;
    static constexpr double POSITION_TOLERANCE = 0.001;
    static constexpr double MAX_VELOCITY       = 5.0;
    double jointCurrentPos = 0.0;
    double jointTargetPos  = 0.0;
    double jointDirection  = 0.0;

    // PID runtime state
    double integralError = 0.0;
    double previousError = 0.0;
};