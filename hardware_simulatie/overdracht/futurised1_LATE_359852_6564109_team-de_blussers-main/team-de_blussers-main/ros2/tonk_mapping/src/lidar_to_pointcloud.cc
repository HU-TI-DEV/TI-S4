#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sensor_msgs/point_cloud2_iterator.hpp>
#include <tf2_ros/static_transform_broadcaster.h>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <tf2/LinearMath/Quaternion.h>

// Filter out ground returns and near-field noise
// Z is in sensor frame: LiDAR zit op ~0.8m hoogte, vloer zit op z ≈ -0.8m
static constexpr float Z_MIN = -0.75f;  // vloer-hits weggooien, auto-onderkant bewaren
static constexpr float Z_MAX = 1.2f;    // plafond van volgende verdieping weggooien
static constexpr float RANGE_MIN = 0.5f; // punten dichter dan 50cm weggooien

class LidarToPointcloud : public rclcpp::Node
{
public:
    LidarToPointcloud() : Node("lidar_to_pointcloud")
    {
        cloud_sub_ = create_subscription<sensor_msgs::msg::PointCloud2>(
            "/lidar/points", 10,
            std::bind(&LidarToPointcloud::cloudCallback, this, std::placeholders::_1));

        cloud_pub_ = create_publisher<sensor_msgs::msg::PointCloud2>(
            "/lidar/pointcloud", 10);

        tf_broadcaster_ = std::make_shared<tf2_ros::StaticTransformBroadcaster>(this);

        publishStaticTransform();

        RCLCPP_INFO(get_logger(), "LiDAR 3D to PointCloud node started");
    }

private:
    void publishStaticTransform()
    {
        geometry_msgs::msg::TransformStamped tf;
        tf.header.stamp = now();
        // base_link → lidar: LiDAR zit 0.8 m boven het rijvlak van de robot.
        // Chain: map → odom → base_link → lidar
        // Zo staan de punten stil in de wereld terwijl de robot rijdt/draait.
        tf.header.frame_id = "base_link";
        tf.child_frame_id = "lidar";
        tf.transform.translation.x = 0.0;
        tf.transform.translation.y = 0.0;
        tf.transform.translation.z = 0.8;

        tf2::Quaternion q;
        q.setRPY(0, 0, 0);
        tf.transform.rotation.x = q.x();
        tf.transform.rotation.y = q.y();
        tf.transform.rotation.z = q.z();
        tf.transform.rotation.w = q.w();

        tf_broadcaster_->sendTransform(tf);
    }

    void cloudCallback(const sensor_msgs::msg::PointCloud2::SharedPtr msg)
    {
        sensor_msgs::msg::PointCloud2 out;
        out.header = msg->header;
        out.header.frame_id = "lidar";
        out.fields = msg->fields;
        out.point_step = msg->point_step;
        out.is_bigendian = msg->is_bigendian;
        out.is_dense = false;

        sensor_msgs::PointCloud2ConstIterator<float> iter_x(*msg, "x");
        sensor_msgs::PointCloud2ConstIterator<float> iter_y(*msg, "y");
        sensor_msgs::PointCloud2ConstIterator<float> iter_z(*msg, "z");

        uint32_t kept = 0;
        const uint32_t total = msg->width * msg->height;
        out.data.reserve(total * msg->point_step);

        for (uint32_t i = 0; i < total; ++i, ++iter_x, ++iter_y, ++iter_z) {
            float x = *iter_x, y = *iter_y, z = *iter_z;

            if (!std::isfinite(x) || !std::isfinite(y) || !std::isfinite(z))
                continue;

            float range = std::sqrt(x*x + y*y + z*z);
            if (range < RANGE_MIN)
                continue;

            if (z < Z_MIN || z > Z_MAX)
                continue;

            const uint8_t* src = msg->data.data() + i * msg->point_step;
            out.data.insert(out.data.end(), src, src + msg->point_step);
            ++kept;
        }

        out.width = kept;
        out.height = 1;
        out.row_step = kept * msg->point_step;

        cloud_pub_->publish(out);
    }

    rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr cloud_sub_;
    rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr cloud_pub_;
    std::shared_ptr<tf2_ros::StaticTransformBroadcaster> tf_broadcaster_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<LidarToPointcloud>());
    rclcpp::shutdown();
    return 0;
}
