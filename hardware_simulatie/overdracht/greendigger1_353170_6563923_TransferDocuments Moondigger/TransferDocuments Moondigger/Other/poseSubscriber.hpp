#pragma once

#include <gz/transport/Node.hh>
#include <gz/msgs/pose.pb.h>

class PoseSubscriber{
    public:
        PoseSubscriber(const std::string &poseTopic);

        double getX(){return x;}
        double getY(){return y;}
        double getYaw(){return yaw;}

        bool active = false; // For checking if the subscriber has received any messages yet, this is important for the object recognition to not use uninitialized values and debugging.
    private:
        gz::transport::Node node;
        std::mutex mtx;

        double x = 0;
        double y = 0;
        double yaw = 0;

        void poseCallback(const gz::msgs::Pose &msg);
};