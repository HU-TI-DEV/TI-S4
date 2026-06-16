#pragma once

#include "poseSubscriber.hpp"

#include <gz/transport/Node.hh>
#include <gz/msgs/image.pb.h>
#include <gz/msgs/pose.pb.h>

#include <opencv2/opencv.hpp>

#include <cmath>
#include <vector>
#include <tuple>
#include <set>
#include <mutex>
#include <limits>

struct Box{ float x, y, width, height;};

/*
Object recognition class for handling image processing and bounding box decoding.

Attributes:
    node (gz.Node): The Gazebo node for subscribing to topics.
    depth_camera_topic (str): The topic to subscribe to for image data.
    pose_publisher_topic (str): The topic to subscribe to for pose data.
    y_value_horizon (int): The y-value of the horizon in the image, this is used to adjust the threshold that filters background from object. 
    value_threshold (int): Threshold for the depth camera values, anything above this value is considered too far away and will be ignored.
    bounding_box_list (list[Box]): A list of Box objects representing the bounding boxes of detected objects.

    area_threshold (int): Minimum area size to be considered an obstacle.

    latest_depth_image (numpy.ndarray): The latest visual representation of the depth image.
    latest_edges_image (numpy.ndarray): The latest edge-detected image.
    latest_boxed_image (numpy.ndarray): The latest image with bounding boxes drawn.
*/
class ObjectRecognition{
public:
    // Constructor, No other one is necessary
    ObjectRecognition(PoseSubscriber &poseSubscriber);
    // Getter functions to display image
    cv::Mat getLatestDepthImage();
    cv::Mat getLatestEdgesImage();
    cv::Mat getLatestBoundingBoxedImage();

    std::vector<std::pair<int, int>> obstacles;
private:
    //---- Attributes -------------------------------------------------------------------
    gz::transport::Node node;
    std::mutex mtx;

    // Shared images between callback and main thread
    cv::Mat latest_depth_image;
    cv::Mat latest_edges_image;
    cv::Mat latest_boxed_image;

    // List of structs for all recognized objects
    std::vector<Box> bounding_box_list;

    std::string depth_camera_topic;
    std::string pose_publisher_topic;

    // The y-value of the horizon in the image, this is used to adjust the threshold that filters background from object. 
    int y_value_horizon = 277; // Note that the underlying function is only a temporary solution and should be replaced with a more concrete solution in the future.
    // Threshold for the depth camera values, anything above this value is considered too far away and will be ignored
    // Using this results in less false positives on the horizon
    int value_threshold = 215;
    // Minimum area size to be considered an obstacle
    int area_threshold = 100;

    int padding = 1.0f; // This is used to add a margin around the detected object, to account for inaccuracies in detection and to create a safety buffer

    // Note the following: 
    // - The robot is 4.5m long, 2 meters wide, this means that the furthest edge is ~2.46 meter away from the center.
    // - The depth camera including the analysis isn't fully accurate, so we already have some safety margin built in.
    // - We use ceil() and floor() because we need to round to ints, this also means that we round outwards, which adds to the safety margin.

    float fov_camera = 60; // Field of view of the camera in degrees

    float image_width = 640; // Width of the image in pixels
    float image_height = 480; // Height of the image in pixels

    float min_distance_depthcamera = 0; // Minimum distance that the depth camera can measure in meters
    float max_distance_depthcamera = 15; // Maximum distance that the depth camera can measure in meters

    // The following offsets are used to correct the position of the depth camera relative to the robot's center.
    // These offsets are the base values when the AMP hasn't rotated yet. When the AMP rotates, these offsets will be adjusted accordingly to maintain accurate distance measurements.
    float offset_x_depthcamera = 0.5; // Horizontal offset of the depth camera in meters
    float offset_y_depthcamera = 0.0; // Vertical offset of the depth camera in meters

    PoseSubscriber& poseSubscriber;

    //---- Methods -------------------------------------------------------------------

    // Interface for functions in calcs.py
    // Returns distance based on pixel grayscale value.
    float convertPixelValueToDistance(float minimal_scaled_value, float maximal_scaled_value, float minimal_unscaled_value, float maximal_unscaled_value, float input_value);

    // Helper function
    float calculateAngleToPoint(int point_x_position, bool flipped = false);
    std::tuple<float, float> angledDistanceToComponents(float distance, float angle);
    std::tuple<float, float> rotateXYVectorBasedOnYaw(float x, float y, float yaw);

    // Combines multiple functions into one using the following structure:
    std::tuple<float, float> simplifyCalcs(int x_pixel, float value, float yaw_local);

    /*
    Extracts the x, y and orientation of the AMP, which it uses to calculate yaw in radians. Updates this to class members.

    Parameters:
    msg (gz.msgs.pose_pb2.Pose):  message received from gazebo.
    */

    void imageCallback(const gz::msgs::Image &msg);

    /*
    Decodes the bounding boxes and calculates the relative vectors to the objects.
    Proceeds to use these to create a set of vectors that represents the absolute positions of the objects, which it then uses to update pathfinding.
    */
    void decodeBB(double amp_x, double amp_y, double amp_yaw);
};