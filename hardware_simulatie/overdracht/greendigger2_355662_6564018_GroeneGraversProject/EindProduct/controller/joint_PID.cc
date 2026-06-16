#include "joint_PID.hh"
#include <iostream>

jointPID::jointPID(double setpoint, double Kp, double Ki, double Kd, 
         std::string joint_name, std::string publish_topic, std::string subscribe_topic)
: setpoint(setpoint), Kp(Kp), Ki(Ki), Kd(Kd), 
  joint_name(joint_name), publish_topic(publish_topic), subscribe_topic(subscribe_topic)
{
    last = std::chrono::steady_clock::now();
}

void jointPID::changeSetpoint(double newSetpoint) { setpoint = newSetpoint; }

void jointPID::onJointState(const gz::msgs::Model &msg)
{
    for (int i = 0; i < msg.joint_size(); ++i) // Loop to gather the usefull joint data to perform PID actions 
    {
        const auto &j = msg.joint(i);

        if (j.name() != joint_name)
            continue;

        double angle = j.axis1().position();

        auto now = std::chrono::steady_clock::now();
        double dt = std::chrono::duration<double>(now - last).count();
        if (dt <= 0) return; 
        last = now;

        double error = setpoint - angle;

        integral += error * dt;
        double derivative = (error - prev_error) / dt;
        prev_error = error;

        double command = Kp * error + Ki * integral + Kd * derivative;

        gz::msgs::Double cmd;
        cmd.set_data(command);
        
        torquePub.Publish(cmd);
        
        static int count = 0;
        if (count++ % 100 == 0) { 
            std::cout << joint_name << " | Target: " << setpoint 
            << " | Current: " << angle 
            << " | Cmd: " << command << std::endl;
        }
    }
}

void jointPID::activate(gz::transport::Node& node)
{
    torquePub = node.Advertise<gz::msgs::Double>(publish_topic);
    node.Subscribe(subscribe_topic, &jointPID::onJointState, this);
}