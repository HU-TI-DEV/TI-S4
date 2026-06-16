#include <gz/transport/Node.hh>
#include <gz/msgs/twist.pb.h>

#include <chrono>
#include <thread>
#include <iostream>

int main()
{
    gz::transport::Node node;

    auto pub = node.Advertise<gz::msgs::Twist>("/cmd_vel");
    if (!pub)
    {
        std::cerr << "Failed to advertise /cmd_vel\n";
        return -1;
    }

    gz::msgs::Twist msg;

    const double forward_speed = 1;
    const double forward_time = 3.0;
    
    const double stand_time = 2.0;
    
    const double angular_speed = 5;           // rad/s
    const double turn_time = 40 / angular_speed;  // 180°

    std::cout << "Robot controller started\n";

    while (true)
    {
        // -------- DRIVE FORWARD --------
        auto start = std::chrono::steady_clock::now();
        std::cout << "DRIVE FORWARD\n";

        while (true)
        {
            double elapsed =
                std::chrono::duration<double>(
                    std::chrono::steady_clock::now() - start).count();

            if (elapsed >= forward_time)
                break;

            msg.mutable_linear()->set_x(forward_speed);
            msg.mutable_linear()->set_y(0);
            msg.mutable_linear()->set_z(0);

            msg.mutable_angular()->set_x(0);
            msg.mutable_angular()->set_y(0);
            msg.mutable_angular()->set_z(0);

            pub.Publish(msg);
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }

        //         // -------- stand still --------
        // start = std::chrono::steady_clock::now();
        // std::cout << "stand still\n";

        // while (true)
        // {
        //     double elapsed =
        //         std::chrono::duration<double>(
        //             std::chrono::steady_clock::now() - start).count();

        //     if (elapsed >= stand_time)
        //         break;

        //     msg.mutable_linear()->set_x(0);
        //     msg.mutable_linear()->set_y(0);
        //     msg.mutable_linear()->set_z(0);

        //     msg.mutable_angular()->set_x(0);
        //     msg.mutable_angular()->set_y(0);
        //     msg.mutable_angular()->set_z(0);

        //     pub.Publish(msg);
        //     std::this_thread::sleep_for(std::chrono::milliseconds(25));
        // }

        // -------- TURN 180 DEG --------
        start = std::chrono::steady_clock::now();
        std::cout << "TURN 180 DEG\n";

        while (true)
        {
            double elapsed =
                std::chrono::duration<double>(
                    std::chrono::steady_clock::now() - start).count();

            if (elapsed >= turn_time)
                break;

            msg.mutable_linear()->set_x(0);
            msg.mutable_linear()->set_y(0);
            msg.mutable_linear()->set_z(0);

            msg.mutable_angular()->set_x(0);
            msg.mutable_angular()->set_y(0);
            msg.mutable_angular()->set_z(angular_speed);

            pub.Publish(msg);
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
    }

    return 0;
}