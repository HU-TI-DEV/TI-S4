#pragma once

#include <gz/transport/Node.hh>
#include <gz/msgs/double.pb.h>
#include <gz/msgs/model.pb.h>

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <future>
#include <mutex>
#include <string>
#include <thread>

//==============================================================================
// MotorJoint
//
// Boundary class representing a single revolute joint on the robot arm.
// Encapsulates:
//   - Gazebo transport (subscribe to joint state, publish cmd_force)
//   - PID controller state (kp, ki, kd, integral, prev_error)
//   - A background thread that drives the PID loop until the target is reached
//
// Usage:
//   MotorJoint joint("base_pivot", gz_node, config);
//   auto done = joint.setAngle(1.57);   // non-blocking, returns future
//   done.wait();                         // optional: block until settled
//   double pos = joint.getAngle();
//==============================================================================

// Default values for Joint configuration
struct MotorJointConfig
{
    double kp;
    double ki;
    double kd;
    double integral_limit; // anti-windup clamp (Nm·s)
    double max_force; // output clamp (Nm)
    double settled_thresh; // rad — "close enough" to target
    double settled_time; // seconds within threshold before done
    double loop_hz;
};

class MotorJoint
{
public:
    // Constructor.
    MotorJoint(const std::string& joint_name, gz::transport::Node& node, const MotorJointConfig& cfg);

    // Destructor.
    ~MotorJoint();

    // Non-copyable, non-movable (owns a thread + atomics).
    MotorJoint(const MotorJoint&) = delete;
    MotorJoint& operator=(const MotorJoint&) = delete;

    // Moves the joint to the targeted angle in the background.
    // Returns a future that becomes ready when the joint has settled.
    // Calling setAngle() again while a move is in progress cancels the old one.
    std::future<void> setAngle(double target_rad);

    // Returns the most recently received joint position (radians).
    double getAngle() const;

    // Returns true if the joint state has been received at least once.
    bool isReady() const;

    // Name of the joint.
    const std::string& name() const { return joint_name_; }

private:
    // Receives joint position from Gazebo.
    void onJointState(const gz::msgs::Model& msg);

    // Publishes the force to be allied to the joint.
    void publishForce(double force_nm);

    // PID loop using the values configured in the Constructor.
    void pidLoop();

    // Stops any current PID loop.
    void stopPidThread();

    // Basic function for clamps.
    static double clamp(double v, double lo, double hi)
    {
        return v < lo ? lo : (v > hi ? hi : v);
    }

    // Joint name again
    const std::string joint_name_;

    // Struct that contains all the values that will be used in the PID loop.
    const MotorJointConfig cfg_;

    // Node for setting up the publisher.
    gz::transport::Node::Publisher force_pub_;

    // Current position being read from Gazebo (using atomic so the values dont corrupt eachother).
    std::atomic<double> current_pos_{0.0};

    // Flag to ensure a message has arrived before you start doing things.
    std::atomic<bool> has_state_{false};

    // This is the thread for PID
    std::thread pid_thread_;

    // Basic boolean to show the thread is running.
    std::atomic<bool> thread_running_{false};

    // Stops the PID loop immediately.
    std::atomic<bool> stop_requested_{false};

    // Target is written by setAngle(), read by pid thread
    std::mutex target_mutex_;
    double target_{0.0};

    // Promise fulfilled when the joint settles
    std::promise<void> settled_promise_;
    std::atomic<bool> promise_valid_{false};
};