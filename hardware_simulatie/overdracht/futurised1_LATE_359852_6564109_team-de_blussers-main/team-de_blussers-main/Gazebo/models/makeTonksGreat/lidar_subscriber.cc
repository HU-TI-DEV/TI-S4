#include <gz/transport/Node.hh>
#include <gz/msgs/laserscan.pb.h>
#include <gz/msgs/pointcloud_packed.pb.h>
#include <iostream>
#include <thread>
#include <chrono>

void lidarCallback(const gz::msgs::PointCloudPacked &msg)
{
    std::cout << "---- 3D Point Cloud Received ----" << std::endl;

    // PointCloudPacked field accessor
    gz::msgs::PointCloudPacked::Field x_field, y_field, z_field;

    int point_step = msg.point_step();
    int num_points = msg.data().size() / point_step;

    std::cout << "Total amount of 3D points: " << num_points << std::endl;
    
    if (num_points > 0)
    {
        float x, y, z;
        memcpy(&x, &msg.data()[0], sizeof(float));
        memcpy(&y, &msg.data()[4], sizeof(float));
        memcpy(&z, &msg.data()[8], sizeof(float));

        std::cout << "First point coordinate: X=" << x << " Y=" << y << " Z=" << z << std::endl;
    }
    std::cout << "----------------------------" << std::endl;
}

int main()
{
    gz::transport::Node node;

    std::string topic = "/lidar/points";

    if (!node.Subscribe(topic, lidarCallback))
    {
        std::cerr << "Error with subscriben" << topic << std::endl;
        return -1;
    }

    while (true)
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    return 0;
}