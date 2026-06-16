#include "objectRecognition.hpp"

#include <limits>

ObjectRecognition::ObjectRecognition(PoseSubscriber &poseSubscriber): 
poseSubscriber(poseSubscriber)
{
    // Constructor starts listening to topics
    depth_camera_topic = "/camera";
    node.Subscribe(depth_camera_topic, &ObjectRecognition::imageCallback, this);
}

// In order to view the latest image, one of these 3 functions is called
// Mutex is used to lock the image and keep it from being changed by other functions
cv::Mat ObjectRecognition::getLatestDepthImage(){
    std::lock_guard<std::mutex> lock(mtx);
    return latest_depth_image.clone();
}
cv::Mat ObjectRecognition::getLatestEdgesImage(){
    std::lock_guard<std::mutex> lock(mtx);
    return latest_edges_image.clone();
}
cv::Mat ObjectRecognition::getLatestBoundingBoxedImage(){
    std::lock_guard<std::mutex> lock(mtx);
    return latest_boxed_image.clone();
}


// Scales a value
float ObjectRecognition::convertPixelValueToDistance(float minimal_scaled_value, float maximal_scaled_value, float minimal_unscaled_value, float maximal_unscaled_value, float input_value){    
    // Determine the range of which the two values are in
    float scaled_range = maximal_scaled_value - minimal_scaled_value;
    float unscaled_range = maximal_unscaled_value - minimal_unscaled_value;
    // Find factor of the two ranges
    float factor = scaled_range / unscaled_range;
    // Normalise the value
    input_value -= minimal_unscaled_value;
    // Return scaled value
    return input_value * factor + minimal_scaled_value;
}

float ObjectRecognition::calculateAngleToPoint(int point_x_position, bool flipped){
    // Calculate new width of the image, keeping in mind that pixel positions start at 0, so the image width for calculations is (image_width - 1)
    int corrected_width = image_width - 1;
    // Calculate the center of the image
    float center_x = corrected_width / 2;
    // Calculate the offset from the center
    float offset = point_x_position - center_x;
    // Calculate the angle per pixel
    float angle_per_pixel = fov_camera / corrected_width;
    // Calculate the angle to the point
    float angle_to_point = offset * angle_per_pixel;
    if (flipped){return angle_to_point * -1;}  
    return angle_to_point;
}

std::tuple<float,float> ObjectRecognition::angledDistanceToComponents(float distance, float angle){
    const float PI = 3.1415926535f;
    // Convert angle from degrees to radians
    float angle_rad =  angle * (PI / 180.0f);
    // bovenstaande code moet hetzelfde doen als dit: angle_rad = math.radians(angle)
    // Calculate x and y components
    float x_component = distance * std::cos(angle_rad);
    float y_component = distance * std::sin(angle_rad);
    return {x_component, y_component};
}


std::tuple<float, float> ObjectRecognition::rotateXYVectorBasedOnYaw(float x, float y, float yaw_rad){

    // Calculate the rotated components
    float rotated_x = x * std::cos(yaw_rad) - y * std::sin(yaw_rad);
    float rotated_y = x * std::sin(yaw_rad) + y * std::cos(yaw_rad);

    return {rotated_x, rotated_y};
}

std::tuple<float,float> ObjectRecognition::simplifyCalcs(int x_pixel, float value, float yaw_local){
    float distance = convertPixelValueToDistance(min_distance_depthcamera, max_distance_depthcamera, 0, 255, value);
    float angle = calculateAngleToPoint(x_pixel, true);
    auto [x_component, y_component] = angledDistanceToComponents(distance, angle);
    auto [rx, ry] = rotateXYVectorBasedOnYaw(x_component, y_component, yaw_local);
    return {rx, ry};
}

void ObjectRecognition::imageCallback(const gz::msgs::Image &msg){
    if (msg.pixel_format_type() != 13) {return;}

    // Solely a sanity check
    size_t expected = msg.width() * msg.height();
    size_t actual = msg.data().size() / sizeof(float);
    if (actual != expected) {return;}

    double AMP_x = poseSubscriber.getX();
    double AMP_y = poseSubscriber.getY();
    double AMP_yaw = poseSubscriber.getYaw();

    // Read depth buffer as float32
    // Create OpenCV matrix that references the depth buffer without copying
    cv::Mat depth(msg.height(), msg.width(), CV_32FC1, (void*)msg.data().data());
    depth = depth.clone();
    // Track invalid pixels (NaN or Inf)
    // Replace invalid values so normalization works
    // np.nan_to_num replaces NaN (np.nan) in an array (ndarray) with any values like 0
    cv::Mat invalid_mask = cv::Mat::zeros(depth.size(), CV_8UC1);
    for (int r = 0; r < depth.rows; r++){
        for (int c = 0; c < depth.cols; c++){
            float &v = depth.at<float>(r, c);
            if (!std::isfinite(v)){
                invalid_mask.at<uchar>(r, c) = 255;
                v = max_distance_depthcamera;
            }
        }
    }

    // numpy.clip() function is used to Clip (limit) the values in an array. 
    // Given an interval, values outside the interval are clipped to the interval edges. 
    // For example, if an interval of [0, 1] is specified, values smaller than 0 become 0, and values larger than 1 become 1.
    cv::Mat depth_clipped;
    cv::min(depth, max_distance_depthcamera, depth_clipped);
    cv::max(depth_clipped, 0.0f, depth_clipped);

    // astype functions converts vis datatype to 8-bit image
    cv::Mat vis;
    depth_clipped.convertTo(vis, CV_8UC1, 255.0 / max_distance_depthcamera);
    
    // TODO Did we not just do this?
    // set invalid pixels to black
    vis.setTo(240, invalid_mask);

    // Edge detection based on Canny edge filter
    // Uses a threshold to decide what gets drawn
    cv::Mat edges;
    cv::Canny(vis, edges, 50, 150);

    // Erases a band of horizontal pixels of the canny edge image
    int band = 3;

    // Only delete horizon
    int y1 = y_value_horizon - band;
    int y2 = y_value_horizon + band;

    edges.rowRange(y1, y2).setTo(0);

    // Make an array with values of 1, with size 3x3
    cv::Mat kernel = cv::Mat::ones(2, 2, CV_8UC1);
    // If the kernel is too big, objects can melt together 
    // Run kernel over edges image and increases the size of the edges
    cv::dilate(edges, edges, kernel);

    // Find contours
    // Contour detection creates a shape around an object of the same color and intensity
    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(edges, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    // Convert grayscale depth image to BGR so we can draw green boxes
    cv::Mat boxed;
    cv::cvtColor(vis, boxed, cv::COLOR_GRAY2BGR);

    bounding_box_list.clear();

    for (const auto &c : contours){
        // Skip areas that are too small to be an obstacle
        if (cv::contourArea(c) < area_threshold) {continue;}
        // Get the dimension values of the bounding box rectangle 
        cv::Rect rect = cv::boundingRect(c);
        // Draw the bounding box rectangle based on the parameter inputs
        cv::rectangle(boxed, rect, cv::Scalar(0,255,0), 2);
        // Store bounding box structs in list
        bounding_box_list.push_back({(float)rect.x, (float)rect.y, (float)rect.width, (float)rect.height});
    }
    // Lock until after block and not until after function
    {
        std::lock_guard<std::mutex> lock(mtx);
        latest_depth_image = vis;
        latest_edges_image = edges;
        latest_boxed_image = boxed;
    }

    decodeBB(AMP_x, AMP_y, AMP_yaw);
}

void ObjectRecognition::decodeBB(double amp_x, double amp_y, double amp_yaw){
    auto [depth_cam_x_vec, depth_cam_y_vec] = rotateXYVectorBasedOnYaw(offset_x_depthcamera, offset_y_depthcamera, amp_yaw);

    // copy image under lock once
    cv::Mat vis_copy;
    {
        std::lock_guard<std::mutex> lock(mtx);
        if (latest_depth_image.empty()){return;}
        vis_copy = latest_depth_image.clone();
    }

    obstacles.clear(); 

    for (const auto &rect : bounding_box_list){
        int x0 = (int)rect.x;
        int y0 = (int)rect.y;
        int width  = (int)rect.width;
        int height  = (int)rect.height;

        int xf_object = std::numeric_limits<int>::max();
        int yf_object = std::numeric_limits<int>::max();

        int xc_object = std::numeric_limits<int>::lowest();
        int yc_object = std::numeric_limits<int>::lowest();

        for (int xi = x0; xi < x0 + width + 1; xi += 2){
            for (int yi = y0; yi < y0 + height + 1; yi += 2){
                // bounds check
                if (xi < 0 || yi < 0 || xi >= vis_copy.cols || yi >= vis_copy.rows){continue;}
                float value = vis_copy.at<uchar>(yi, xi);
                float threshold;
                if(yi < y_value_horizon){threshold = value_threshold;}
                else{threshold = value_threshold - convertPixelValueToDistance(0, value_threshold, y_value_horizon, image_height - 1, yi);}

                if (value < threshold){
                    auto [dx, dy] = simplifyCalcs(xi, value, amp_yaw);
                    float x_abs = amp_x + depth_cam_x_vec + dx;
                    float y_abs = amp_y + depth_cam_y_vec + dy;

                    int xf = std::floor(x_abs - padding);
                    int yf = std::floor(y_abs - padding);
                    int xc = std::ceil(x_abs + padding);
                    int yc = std::ceil(y_abs + padding);

                    xf_object = std::min(xf_object, xf);
                    yf_object = std::min(yf_object, yf);
                    xc_object = std::max(xc_object, xc);
                    yc_object = std::max(yc_object, yc);
                }
            }
        }
        if (xf_object != std::numeric_limits<int>::max() && yf_object != std::numeric_limits<int>::max() && xc_object != std::numeric_limits<int>::lowest() && yc_object != std::numeric_limits<int>::lowest()){
            for (int x = xf_object; x <= xc_object; x++){
                for (int y = yf_object; y <= yc_object; y++){
                    obstacles.push_back({x, y});
                }
            }
        }
    }
}