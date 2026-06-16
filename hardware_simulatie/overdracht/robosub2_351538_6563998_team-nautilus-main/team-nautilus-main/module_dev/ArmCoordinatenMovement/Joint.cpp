#include "Joint.hpp"

#include <algorithm>
#include <iostream>

Joint::Joint(const JointSpec& spec, double initialPosRad)
    : spec(spec)
    , jointCurrentPos(initialPosRad)
    , jointTargetPos(initialPosRad)
    , jointDirection(0.0)
    , integralError(0.0)
    , previousError(0.0)
{
    jointCurrentPos = clamp(jointCurrentPos);
    jointTargetPos  = jointCurrentPos;
}

double Joint::degreesToRadians(double deg) {
    return deg * M_PI / 180.0;
}

double Joint::radiansToDegrees(double rad) {
    return rad * 180.0 / M_PI;
}

double Joint::clamp(double val) {
    return std::clamp(val, spec.lowerLimitRad, spec.upperLimitRad);
}

double Joint::setTarget(double targetRad) {
    double clamped = clamp(targetRad);

    if (std::abs(clamped - targetRad) > 1e-9) {
        std::cout << "  [" << spec.name << "] Warning: Target clamped to limits ["
                  << radiansToDegrees(spec.lowerLimitRad) << ", "
                  << radiansToDegrees(spec.upperLimitRad) << "] deg\n";
    }

    jointTargetPos = clamped;

    // Clear PID history variables to handle the fresh setpoint trajectory properly
    integralError = 0.0;
    previousError = jointTargetPos - jointCurrentPos;

    double diff = jointTargetPos - jointCurrentPos;
    if (std::abs(diff) < POSITION_TOLERANCE) {
        std::cout << "  [" << spec.name << "] Already at target.\n";
        jointDirection = 0.0;
    } else {
        jointDirection = (diff > 0) ? MAX_VELOCITY : -MAX_VELOCITY;
        std::cout << "  [" << spec.name << "] New target: "
                  << radiansToDegrees(clamped) << " deg. PID controller engaging.\n";
    }

    return clamped;
}

void Joint::updatePosition(double elapsed) {
    if (elapsed <= 0.0) return;

    double error = jointTargetPos - jointCurrentPos;

    // Inside tolerance target check
    if (std::abs(error) < POSITION_TOLERANCE) {
        jointCurrentPos = jointTargetPos;
        jointDirection = 0.0;
        integralError = 0.0;
        return;
    }

    // Accumulate the error over time and apply anti-windup clamping to prevent overshoot
    integralError += error * elapsed;
    integralError = std::clamp(integralError, -0.5, 0.5);

    // Calculate the rate of change of the error and cache the current error for the next cycle
    double derivativeError = (error - previousError) / elapsed;
    previousError = error;

    // Combine proportional, integral, and derivative terms to calculate the ideal control effort
    double pidOutput = (spec.kP * error) + (spec.kI * integralError) + (spec.kD * derivativeError);

    // Cap the PID output to respect physical velocity limitations of the joint hardware
    jointDirection = std::clamp(pidOutput, -MAX_VELOCITY, MAX_VELOCITY);

    // Advance the current physical state based on the calculated velocity and enforce hard bounds
    jointCurrentPos += jointDirection * elapsed;
    jointCurrentPos  = clamp(jointCurrentPos);
}

void Joint::printInfo() {
    std::cout << "\n  ========================================\n"
              << "  Joint Name   : " << spec.name << "\n"
              << "  Gains (P,I,D): [" << spec.kP << ", " << spec.kI << ", " << spec.kD << "]\n"
              << "  Limits       : [" << radiansToDegrees(spec.lowerLimitRad) << " deg, " << radiansToDegrees(spec.upperLimitRad) << " deg]\n"
              << "  Current Pos  : " << radiansToDegrees(jointCurrentPos) << " deg\n"
              << "  Target Pos   : " << radiansToDegrees(jointTargetPos) << " deg\n"
              << "  Velocity     : " << jointDirection << " rad/s\n"
              << "  ========================================\n";
}