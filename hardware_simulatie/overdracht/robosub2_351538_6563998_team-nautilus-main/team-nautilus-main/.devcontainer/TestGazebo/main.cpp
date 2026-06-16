#include <iostream>
#include <thread>
#include <chrono>
#include <gz/transport/Node.hh>
#include <gz/msgs/twist.pb.h>


int main()
{
    gz::transport::Node node;
    auto pub = node.Advertise<gz::msgs::Twist>("cmd_vel");
    if (!pub)
    {
        std::cerr << "Error advertising topic\n";
        return -1;
    }

    // Wait for subscriber to connect
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));

    gz::msgs::Twist msg;
    msg.mutable_linear()->set_x(1);
    msg.mutable_angular()->set_z(0);

    pub.Publish(msg);

    // Give the message time to be delivered before the node is destroyed
    std::this_thread::sleep_for(std::chrono::milliseconds(200));

    return 0;
}