#include "camera.hh"

#include <iostream>
#include <thread>
#include <chrono>
#include <cstdio>

int main()
{
    Camera Camera;

    std::string topic =
        "/world/desert_wereld/model/greendigger_complete/link/camera_link/sensor/camera/image";

    if (!Camera.Subscribe(topic))
    {
        return 1;
    }

    std::cout << "listening to: "
              << topic
              << std::endl;

    while (true)
    {
        std::this_thread::sleep_for(std::chrono::seconds(2));

        std::remove("photoVision.jpg");

        std::lock_guard<std::mutex> lock(Camera.mtx);

        if (!Camera.latestGray.empty())
        {
            std::string name = "photoVision.jpg";

            cv::imwrite(name, Camera.latestGray);

            std::cout << "saved: "
                      << name
                      << std::endl;
        }
    }

    return 0;
}