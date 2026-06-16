/**
 * @file main.cpp
 * @brief Entry point for the Gazebo robotic arm joint controller.
 *
 * Implements a state-machine-based controller that sequences a 3-DOF robotic arm
 * through a series of world-space targets using PID-controlled joint velocities
 * and inverse kinematics solved per target.
 *
 * @todo Fix inverse kinematics getting stuck in joint limits.
 */

#include <chrono>
#include <cmath>
#include <iostream>
#include <string>
#include <thread>
#include <vector>
#include <functional>

#include <gz/msgs/model.pb.h>
#include <gz/msgs/double.pb.h>
#include <gz/msgs/pose.pb.h>
#include <gz/msgs/pose_v.pb.h>
#include <gz/transport/Node.hh>
#include <gz/math/Quaternion.hh>

#include "pid_control.hpp"
#include "utils.hpp"
#include "inverse_kinematics.hpp"

/// @brief Names of the controlled joints in the Gazebo model.
std::vector<std::string> joint_names = {"joint", "joint1", "joint2"};

/// @brief Names of the links associated with each controlled joint.
std::vector<std::string> link_names  = {"robot_arm_2_link", "robot_arm_3_link", "robot_arm_4_link"};

/// @brief Desired target angles for each joint (radians), set by the state machine.
std::vector<double> target_angles    = {0.0, 0.0, 0.0};

/// @brief Current measured angles for each joint (radians), updated by JointStateCallback.
std::vector<double> joint_angles     = {0.0, 0.0, 0.0};

/**
 * @brief Gazebo transport callback that updates #joint_angles from joint state messages.
 * @param msg The incoming joint state model message published by Gazebo.
 */
void JointStateCallback(const gz::msgs::Model &msg)
{
    for (const auto &joint : msg.joint())
    {
        if (joint.name() == "joint")
            joint_angles[0] = joint.axis1().position();
        else if (joint.name() == "joint1")
            joint_angles[1] = joint.axis1().position();
        else if (joint.name() == "joint2")
            joint_angles[2] = joint.axis1().position();
    }
}

/**
 * @brief States of the arm controller state machine.
 */
enum class State {
    YAW,     ///< Rotate joint0 (base) to face the current target.
    EXTEND,  ///< Extend joint1 and joint2 to reach the target position.
    RETRACT, ///< Return joint1 and joint2 to the home (retracted) position.
    WAIT,    ///< Hold at the target for a fixed duration before retracting.
};

/**
 * @brief Program entry point. Sets up Gazebo publishers/subscribers and runs the
 *        PID control loop driven by the arm state machine.
 * @param argc Argument count (unused).
 * @param argv Argument values (unused).
 * @return int Exit code (unreachable in practice — control loop runs indefinitely).
 */
int main(int argc, char **argv)
{
    std::string modelName    = "my_gazebo_model";
    const double update_rate = 200.0;
    const double Kp          = 1.5;
    const double Ki          = 0.05;
    const double Kd          = 0.5;
    const double MAX_CHANGE  = 2.0;

    // home position for joint1 and joint2 when retracted
    const double HOME_J1 = 0.0;
    const double HOME_J2 = 0.0;

    // thresholds
    const double YAW_THRESHOLD     = 0.05; // rad — yaw must be within this before extending
    const double REACHED_THRESHOLD = 0.05; // rad — all joints within this = reached
    const double RETRACT_THRESHOLD = 0.05; // rad — home reached
    const double WAIT_TIME_S       = 1.0;  // seconds to wait at target before retracting

    gz::transport::Node node;
    std::vector<gz::transport::Node::Publisher> pubs;
    std::vector<PidController> pid_controllers;

    for (std::size_t i = 0; i < joint_names.size(); ++i)
    {
        const std::string &joint = joint_names[i];
        const std::string topic  = "/model/" + modelName + "/joint/" + joint + "/cmd_vel";
        pubs.push_back(node.Advertise<gz::msgs::Double>(topic));
        pid_controllers.emplace_back(Kp, Ki, Kd);
    }

    node.Subscribe("/world/default/model/my_gazebo_model/joint_state", &JointStateCallback);
    std::this_thread::sleep_for(std::chrono::milliseconds(500));

    const auto period = std::chrono::duration<double>(1.0 / update_rate);

    const double joint_lower[3] = { -M_PI,    -M_PI/2.0, -1.0      };
    const double joint_upper[3] = {  M_PI,     M_PI/2.0,  M_PI/2.0 };

    // targets: {x, y, z} in world space
    const std::vector<Vec3d> targets = {
        {0.0062,  0.3772,  0.8791},   // printer
        {0.0022, -3.1070,  1.4791},   // curing
        {-1.6965, -1.9387, 0.7563},   // table
        {1.7388,  -1.4156, 0.3785},   // bin
    };
    const std::vector<std::string> target_names = {"printer", "curing", "table", "bin"};

    int current_target = 0;
    State state        = State::YAW;
    double wait_start  = 0.0;

    // compute IK for first target
    Vec3d ik = solve_inverse_kinematics(targets[current_target]);
    double target_yaw = ik.x;
    target_angles[0]  = std::max(joint_lower[0], std::min(joint_upper[0], ik.x));
    target_angles[1]  = HOME_J1; // start retracted
    target_angles[2]  = HOME_J2;

    printf("Starting -> target: %s  yaw=%.4f\n", target_names[current_target].c_str(), target_yaw);

    const auto start = std::chrono::steady_clock::now();

    while (true)
    {
        const auto now = std::chrono::steady_clock::now();
        const double t = std::chrono::duration<double>(now - start).count();

        // state machine
        switch (state)
        {
            case State::YAW:
            {
                // only control joint0, keep arm retracted
                target_angles[0] = std::max(joint_lower[0], std::min(joint_upper[0], ik.x));
                target_angles[1] = HOME_J1;
                target_angles[2] = HOME_J2;

                double yaw_err = std::abs(target_angles[0] - joint_angles[0]);
                if (yaw_err < YAW_THRESHOLD)
                {
                    printf("Yaw reached (err=%.4f) -> EXTEND\n", yaw_err);
                    // now set full IK target
                    target_angles[1] = std::max(joint_lower[1], std::min(joint_upper[1], ik.y));
                    target_angles[2] = std::max(joint_lower[2], std::min(joint_upper[2], ik.z));
                    for (auto &pid : pid_controllers) pid.reset();
                    state = State::EXTEND;
                }
                break;
            }

            case State::EXTEND:
            {
                double err0 = std::abs(target_angles[0] - joint_angles[0]);
                double err1 = std::abs(target_angles[1] - joint_angles[1]);
                double err2 = std::abs(target_angles[2] - joint_angles[2]);

                if (err0 < REACHED_THRESHOLD &&
                    err1 < REACHED_THRESHOLD &&
                    err2 < REACHED_THRESHOLD)
                {
                    printf("Target %s reached -> waiting %.1fs\n",
                           target_names[current_target].c_str(), WAIT_TIME_S);
                    wait_start = t;
                    state = State::WAIT;
                }
                break;
            }

            case State::WAIT:
            {
                if (t - wait_start >= WAIT_TIME_S)
                {
                    printf("Wait done -> RETRACT\n");
                    target_angles[1] = HOME_J1;
                    target_angles[2] = HOME_J2;
                    for (auto &pid : pid_controllers) pid.reset();
                    state = State::RETRACT;
                }
                break;
            }

            case State::RETRACT:
            {
                double err1 = std::abs(HOME_J1 - joint_angles[1]);
                double err2 = std::abs(HOME_J2 - joint_angles[2]);

                if (err1 < RETRACT_THRESHOLD && err2 < RETRACT_THRESHOLD)
                {
                    // move to next target
                    current_target = (current_target + 1) % (int)targets.size();
                    ik = solve_inverse_kinematics(targets[current_target]);

                    target_angles[0] = std::max(joint_lower[0], std::min(joint_upper[0], ik.x));
                    target_angles[1] = HOME_J1;
                    target_angles[2] = HOME_J2;

                    printf("Retracted -> next target: %s  yaw=%.4f\n",
                           target_names[current_target].c_str(), ik.x);
                    for (auto &pid : pid_controllers) pid.reset();
                    state = State::YAW;
                }
                break;
            }
        }

        // PID control loop
        for (std::size_t i = 0; i < joint_names.size(); ++i)
        {
            const double joint_angle  = joint_angles[i];
            const double target_angle = target_angles[i];

            double vel = pid_controllers[i].compute(target_angle, joint_angle, period.count());
            vel = clampd(vel, -10.0,      10.0);
            vel = clampd(vel, -MAX_CHANGE, MAX_CHANGE);

            if (joint_angle >= joint_upper[i] && vel > 0.0) vel = 0.0;
            if (joint_angle <= joint_lower[i] && vel < 0.0) vel = 0.0;

            gz::msgs::Double msg;
            msg.set_data(vel);
            pubs[i].Publish(msg);

            printf("joint%zu:  pos=%.4f  target=%.4f  err=%.4f  vel=%.4f\n",
                   i, joint_angle, target_angle,
                   target_angle - joint_angle, vel);
        }

        printf("State: %s\n",
               state == State::YAW     ? "YAW" :
               state == State::EXTEND  ? "EXTEND" :
               state == State::WAIT    ? "WAIT" :
                                         "RETRACT");

        std::this_thread::sleep_for(period);
    }

    std::cout << "Joint mover finished.\n";
    return 0;
}