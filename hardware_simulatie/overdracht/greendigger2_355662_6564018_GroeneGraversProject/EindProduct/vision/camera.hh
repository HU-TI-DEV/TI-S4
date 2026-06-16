#ifndef CAMERA_HH
#define CAMERA_HH

#include <gz/transport/Node.hh>
#include <gz/msgs/image.pb.h>

#include <opencv2/opencv.hpp>

#include <mutex>
#include <string>

class Camera {
    public:
        Camera();

        bool Subscribe(const std::string &topic);

        void OnImage(const gz::msgs::Image &msg);

        cv::Mat latestGray;
        std::mutex mtx;
        bool newFrame;

    private:
        gz::transport::Node node;
};

#endif