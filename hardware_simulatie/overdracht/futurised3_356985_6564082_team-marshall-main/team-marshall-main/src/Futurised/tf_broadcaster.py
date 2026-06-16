#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster, StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry


class TFBroadcaster(Node):

    def __init__(self):
        super().__init__('tf_broadcaster')
        # NO use_sim_time here — use wall time for TF
        self.dynamic_br = TransformBroadcaster(self)
        self.static_br = StaticTransformBroadcaster(self)
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.timer = self.create_timer(1.0, self.publish_static_transforms)
        self.get_logger().info('TF broadcaster started')

    def odom_callback(self, msg):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()  # wall time, not msg.header.stamp
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = 0.0
        t.transform.rotation = msg.pose.pose.orientation
        self.dynamic_br.sendTransform(t)

    def publish_static_transforms(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()  # now uses sim time
        t.header.frame_id = 'base_link'
        t.child_frame_id = 'Flip/front_block/gpu_lidar'
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.1
        t.transform.rotation.w = 1.0
        self.static_br.sendTransform(t)



def main():
    rclpy.init()
    node = TFBroadcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()