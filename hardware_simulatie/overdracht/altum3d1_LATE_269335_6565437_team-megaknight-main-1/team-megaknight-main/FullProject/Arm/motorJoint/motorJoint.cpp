#include "motorJoint.hpp"

#include <iostream>
#include <stdexcept>
#include <string>

// Topic helpers.
static std::string stateTopicFor(const std::string& /*joint_name*/)
{
    // All joints arrive in a single Model message on this topic.
    return "/world/default/model/robot-arm/joint_state";
}

static std::string forceTopicFor(const std::string& joint_name)
{
    return "/model/robot-arm/joint/" + joint_name + "/cmd_force";
}

// Constructor

MotorJoint::MotorJoint(const std::string& joint_name, gz::transport::Node& node, const MotorJointConfig& cfg) : joint_name_(joint_name), cfg_(cfg)
{
    // Advertise force topic
    const std::string force_topic = forceTopicFor(joint_name_);
    force_pub_ = node.Advertise<gz::msgs::Double>(force_topic);
    if (!force_pub_)
        throw std::runtime_error(
            "[MotorJoint:" + joint_name_ + "] Failed to advertise " + force_topic);

    // Subscribe to joint state (shared topic; callback filters by name)
    const std::string state_topic = stateTopicFor(joint_name_);
    if (!node.Subscribe(state_topic, &MotorJoint::onJointState, this))
        throw std::runtime_error(
            "[MotorJoint:" + joint_name_ + "] Failed to subscribe to " + state_topic);
}

// Destructor

MotorJoint::~MotorJoint()
{
    stopPidThread(); // Stops any current thread
    publishForce(0.0); // Makes it so there is no force accidentally left over from an old thread.
}


std::future<void> MotorJoint::setAngle(double target_rad)
{
    // Cancel any running PID thread and start fresh
    stopPidThread();

    {
        std::lock_guard<std::mutex> lock(target_mutex_);
        target_ = target_rad;
    }

    // Create a new promise / future pair
    settled_promise_ = std::promise<void>{};
    std::future<void> future = settled_promise_.get_future();
    promise_valid_.store(true);

    // Launch background PID thread
    stop_requested_.store(false);
    thread_running_.store(true);
    pid_thread_ = std::thread(&MotorJoint::pidLoop, this);

    return future;
}

double MotorJoint::getAngle() const
{
    return current_pos_.load(std::memory_order_relaxed);
}

bool MotorJoint::isReady() const
{
    return has_state_.load(std::memory_order_relaxed);
}

// Gazebo stuff
void MotorJoint::onJointState(const gz::msgs::Model& msg)
{
    for (int i = 0; i < msg.joint_size(); ++i)
    {
        const auto& joint = msg.joint(i);
        if (joint.name() == joint_name_)
        {
            current_pos_.store(joint.axis1().position(),
                               std::memory_order_relaxed);
            has_state_.store(true, std::memory_order_relaxed);
            return;
        }
    }
}

void MotorJoint::publishForce(double force_nm)
{
    gz::msgs::Double msg;
    msg.set_data(force_nm);
    force_pub_.Publish(msg);
}

// PID stuff

void MotorJoint::pidLoop()
{
    // The chrono calls are to use steady_clock which maintains a constant timing unlike system time.
    using clock    = std::chrono::steady_clock;
    using duration = std::chrono::duration<double>;

    const double dt     = 1.0 / cfg_.loop_hz;
    const auto   period = std::chrono::duration<double>(dt);

    double integral   = 0.0;
    double prev_error = 0.0;

    // Initialise prev_error with current position
    {
        std::lock_guard<std::mutex> lock(target_mutex_);
        prev_error = target_ - current_pos_.load(std::memory_order_relaxed);
    }

    double settled_elapsed = 0.0;   // seconds within threshold

    while (!stop_requested_.load(std::memory_order_relaxed))
    {
        auto loop_start = clock::now();

        double target;
        {
            std::lock_guard<std::mutex> lock(target_mutex_);
            target = target_;
        }

        const double current = current_pos_.load(std::memory_order_relaxed);
        const double error   = target - current;

        // Integral with anti-windup
        integral = clamp(integral + error * dt,
                         -cfg_.integral_limit, cfg_.integral_limit);

        // Derivative (backward difference)
        const double derivative = (error - prev_error) / dt;
        prev_error = error;

        // PID output
        const double force = clamp(
            cfg_.kp * error + cfg_.ki * integral + cfg_.kd * derivative,
            -cfg_.max_force, cfg_.max_force);

        publishForce(force);

        // Settling detection
        if (std::abs(error) < cfg_.settled_thresh)
        {
            settled_elapsed += dt;
            if (settled_elapsed >= cfg_.settled_time)
            {
                // Fulfil the promise exactly once
                if (promise_valid_.exchange(false))
                    settled_promise_.set_value();

                // Keep holding position — don't exit the loop
                // (a new setAngle() will stop us if needed)
            }
        }
        else
        {
            settled_elapsed = 0.0;
        }

        std::this_thread::sleep_until(loop_start + period);
    }

    thread_running_.store(false);
}

void MotorJoint::stopPidThread()
{
    if (pid_thread_.joinable())
    {
        stop_requested_.store(true);
        pid_thread_.join();
    }

    // If the promise was never fulfilled (e.g. cancelled mid-move),
    // fulfil it now so callers don't block forever.
    if (promise_valid_.exchange(false))
        settled_promise_.set_value();
}