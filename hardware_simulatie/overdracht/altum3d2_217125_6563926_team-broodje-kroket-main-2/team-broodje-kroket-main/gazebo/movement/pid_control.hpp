#pragma once

/**
 * @brief Discrete PID controller with anti-windup integral clamping.
 *
 * Computes a velocity command from the proportional, integral, and derivative
 * terms of the error between a desired set-point and a measured value.
 */
class PidController
{
private:
    double Kp;         ///< Proportional gain.
    double Ki;         ///< Integral gain.
    double Kd;         ///< Derivative gain.
    double integral;   ///< Accumulated integral term (clamped to prevent windup).
    double prev_error; ///< Error value from the previous control step (used for derivative).
public:
    /**
     * @brief Construct a PidController with the given gains.
     * @param p Proportional gain.
     * @param i Integral gain.
     * @param d Derivative gain.
     */
    PidController(double p, double i, double d);

    /**
     * @brief Compute the PID control output for one time step.
     * @param desired  The set-point (target joint angle in radians).
     * @param current  The measured joint angle in radians.
     * @param dt       Time step in seconds since the last call.
     * @return The computed control signal (joint velocity command in rad/s).
     */
    double compute(double desired, double current, double dt);

    /**
     * @brief Reset the integral accumulator and previous error to zero.
     *
     * Should be called whenever the target changes or a new state is entered
     * to avoid transient velocity spikes from stale state.
     */
    void reset() { integral = 0.0; prev_error = 0.0; }
};