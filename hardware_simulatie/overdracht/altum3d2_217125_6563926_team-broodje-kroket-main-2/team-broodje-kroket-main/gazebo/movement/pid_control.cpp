#include "pid_control.hpp"
#include <algorithm>
PidController::PidController(double p, double i, double d) : Kp(p), Ki(i), Kd(d), integral(0.0), prev_error(0.0) {}

double PidController::compute(double desired, double current, double dt)
{
    double error = desired - current;
    integral += error * dt;

    // clamp integral to prevent windup
    integral = std::max(-10.0, std::min(10.0, integral));

    double derivative = (error - prev_error) / dt;
    prev_error = error;

    return Kp * error + Ki * integral + Kd * derivative;
}