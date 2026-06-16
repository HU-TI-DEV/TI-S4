#include "camera.hh"

#include <iostream>

Camera::Camera()
    : newFrame(false)
{
}

bool Camera::Subscribe(const std::string &topic)
{
    if (!node.Subscribe(topic, &Camera::OnImage, this))
    {
        std::cerr << "couldn't subscribe to topic\n";
        return false;
    }

    return true;
}

void Camera::OnImage(const gz::msgs::Image &msg)
{
    cv::Mat rgb(
        msg.height(),
        msg.width(),
        CV_8UC3,
        (void *)msg.data().data());

    cv::Mat bgr;
    cv::cvtColor(rgb, bgr, cv::COLOR_RGB2BGR);

    cv::Mat gray;
    cv::cvtColor(bgr, gray, cv::COLOR_BGR2GRAY);

    {
        std::lock_guard<std::mutex> lock(mtx);
        latestGray = gray.clone();
        newFrame = true;
    }

    cv::imshow("Grayscale Camera", gray);
    cv::waitKey(1);
}