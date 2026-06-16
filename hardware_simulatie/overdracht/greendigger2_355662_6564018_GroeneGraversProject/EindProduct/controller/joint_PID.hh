#ifndef JOINT_PID_HH
#define JOINT_PID_HH

#include <string> 
#include <chrono> 
#include <gz/msgs.hh>
#include <gz/transport.hh>

class jointPID {
public:
    jointPID(double setpoint, double Kp, double Ki, double Kd, 
             std::string joint_name, std::string publish_topic, std::string subscribe_topic);

    void changeSetpoint(double newSetpoint);
    void onJointState(const gz::msgs::Model &msg);
    void activate(gz::transport::Node& node);

private:
    double setpoint, Kp, Ki, Kd;
    std::string joint_name, publish_topic, subscribe_topic;
    double prev_error = 0.0;
    double integral = 0.0;
    
    std::chrono::steady_clock::time_point last;
    gz::transport::Node::Publisher torquePub;
};

#endif