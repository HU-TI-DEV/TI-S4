#include "poseSubscriber.hpp"

#include <cmath>
#include <mutex>

PoseSubscriber::PoseSubscriber(const std::string &pose_topic){
    node.Subscribe(pose_topic, &PoseSubscriber::poseCallback, this);
}

void PoseSubscriber::poseCallback(const gz::msgs::Pose &msg){
    std::lock_guard<std::mutex> lock(mtx);
    // Using the pose function in the sdf to find the x and y coordinate of the AMP
    x = msg.position().x();
    y = msg.position().y();

    // The orientation of the AMP is of importance to now how the AMP needs to change direction
    auto q = msg.orientation();

    // quaternion to yaw
    double siny_cosp = 2 * (q.w()*q.z() + q.x()*q.y());
    double cosy_cosp = 1 - 2 * (q.y()*q.y() + q.z()*q.z());

    yaw = std::atan2(siny_cosp, cosy_cosp);

    active = true; 
}