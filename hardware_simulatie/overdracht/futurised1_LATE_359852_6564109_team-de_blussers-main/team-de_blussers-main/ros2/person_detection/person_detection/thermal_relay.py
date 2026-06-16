import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class ThermalRelay(Node):
    def __init__(self):
        super().__init__('thermal_relay')
        self.pub = self.create_publisher(Image, '/camera/image_raw', 10)
        self.create_subscription(
            Image, '/thermal_camera_8bit/image',
            self.pub.publish, 10
        )
        self.get_logger().info('Thermal relay: /thermal_camera_8bit/image → /camera/image_raw')


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(ThermalRelay())
    rclpy.shutdown()
