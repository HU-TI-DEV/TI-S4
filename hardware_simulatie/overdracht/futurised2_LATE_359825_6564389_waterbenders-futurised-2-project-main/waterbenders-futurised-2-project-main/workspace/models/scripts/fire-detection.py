import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
import numpy as np
import cv2
import time
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist


class ObjectTemperature(Node):
    def __init__(self):
        super().__init__('object_temperature')

        # Subscribers
        self.sub_rgb = self.create_subscription(
            Image,
            '/front/image',
            self.rgb_cb,
            10)
        
        self.sub_thermal = self.create_subscription(
            Image,
            '/FLIP/thermal_camera',
            self.thermal_cb,
            10)
        
        # sub flip
        self.sub_cmd = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_cb,
            10)
        
        # Publishers
        self.pub_heatmap = self.create_publisher(
            Image,
            '/thermal/heatmap_image',
            10)
        
        self.pub_status = self.create_publisher(
            String,
            '/fire_detection/status',
            10)

        # Variables
        self.bridge = CvBridge()
        self.rgb = None
        self.thermal = None
        self.previous_gray = None
        self.last_pub_time = 0
        self.min_interval = 0.1

        # Temperature scale
        self.min_temp = 0.0
        self.max_temp = 300.0

        # Fire threshold
        self.fire_temp_threshold = 80.0
        
        # velocity of flip
        self.angular_velocity = 0.0

        self.get_logger().info('===== Fire Detection Node Started =====')

    # RGB CALLBACK
    def rgb_cb(self, msg):
        self.rgb = msg
        self.try_process()

    # THERMAL CALLBACK
    def thermal_cb(self, msg):
        self.thermal = msg
        self.try_process()
        
    # FLIP CALLBACK
    def cmd_cb(self, msg):
        self.angular_velocity = abs(msg.angular.z)

    # MAIN PROCESS
    def try_process(self):
        if self.rgb is None or self.thermal is None:
            return

        now = time.time()
        if now - self.last_pub_time < self.min_interval:
            return
        self.last_pub_time = now
 
        # RGB IMAGE
        rgb_image = self.bridge.imgmsg_to_cv2(                  # converts ROS image to OpenCV format
            self.rgb,
            desired_encoding='bgr8')
        rgb_h, rgb_w = rgb_image.shape[:2]

        # THERMAL IMAGE
        thermal_raw = np.frombuffer(
            self.thermal.data,
            dtype=np.uint16
        ).reshape((self.thermal.height, self.thermal.width))        # reshape raw data into image form

        temp_celsius = (thermal_raw.astype(np.float32) * 0.01) - 273.15                 # from kelvin to celsius

        # =====THERMAL FIRE DETECTION=====
        thermal_fire_mask = (temp_celsius > self.fire_temp_threshold).astype(np.uint8)

        hot_pixels = np.sum(thermal_fire_mask)
        thermal_fire_detected = hot_pixels > 500

        # Resize thermal mask to RGB size
        thermal_mask_resized = cv2.resize(
            thermal_fire_mask,
            (rgb_w, rgb_h))

        # =====RGB FIRE COLOR DETECTION=====
        hsv = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2HSV)

        # Fire-like colors
        lower_fire = np.array([5, 100, 100])
        upper_fire = np.array([35, 255, 255])

        rgb_fire_mask = cv2.inRange(
            hsv,
            lower_fire,
            upper_fire)

        # cleanup
        kernel = np.ones((5, 5), np.uint8)

        rgb_fire_mask = cv2.morphologyEx(
            rgb_fire_mask,
            cv2.MORPH_OPEN,                 # remove some noise
            kernel)

        rgb_fire_mask = cv2.morphologyEx(
            rgb_fire_mask,
            cv2.MORPH_DILATE,               # expands detected regions
            kernel)

        fire_pixels = cv2.countNonZero(rgb_fire_mask)
        rgb_fire_detected = fire_pixels > 300

        # =====MOTION DETECTION=====
        gray = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)
        motion_detected = False
        motion_mask = np.zeros_like(gray)

        if self.previous_gray is not None:
            # Difference between frames
            diff = cv2.absdiff(gray, self.previous_gray)

            # Threshold difference image
            _, motion_mask = cv2.threshold(
                diff,
                25,
                255,
                cv2.THRESH_BINARY)

            # Remove noise
            motion_mask = cv2.morphologyEx(
                motion_mask,
                cv2.MORPH_OPEN,
                kernel)

            moving_pixels = cv2.countNonZero(motion_mask)

            # only detect if flip not turning
            if self.angular_velocity > 0.3:
                motion_detected = False
            else:
                motion_detected = moving_pixels > 400

        # Save current frame for next iteration
        self.previous_gray = gray.copy()

        # --FINAL FIRE DETECTION--
        fire_detected = (
            thermal_fire_detected and
            rgb_fire_detected and
            motion_detected)

        # CREATE HEATMAP
        norm = (temp_celsius - self.min_temp) / (self.max_temp - self.min_temp + 1e-6)
        norm = np.clip(norm, 0.0, 1.0)
        heatmap_gray = (norm * 255).astype(np.uint8)

        heatmap_color = cv2.applyColorMap(
            heatmap_gray,
            cv2.COLORMAP_TURBO)

        heatmap_resized = cv2.resize(
            heatmap_color,
            (rgb_w, rgb_h))

        # VISUALIZATION
        debug = rgb_image.copy()

        # Draw RGB fire contours
        contours, _ = cv2.findContours(
            rgb_fire_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)

        cv2.drawContours(
            debug,
            contours,
            -1,
            (0, 255, 255),
            2)

        # Draw motion contours
        motion_contours, _ = cv2.findContours(
            motion_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)

        cv2.drawContours(
            debug,
            motion_contours,
            -1,
            (255, 0, 0),
            1)

        # STATUS TEXT
        if fire_detected:
            cv2.putText(
                debug,
                'FIRE DETECTED',
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                3)
            
            self.get_logger().warn('FIRE DETECTED!')
            status = String()
            status.data = 'FIRE'
            self.pub_status.publish(status)
        else:
            cv2.putText(
                debug,
                '     ',
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2)

            status = String()
            status.data = 'NO_FIRE'
            self.pub_status.publish(status)

        # DEBUG
        center_temp = temp_celsius[
            temp_celsius.shape[0] // 2,
            temp_celsius.shape[1] // 2]

        cv2.putText(
            debug,
            f'Center Temp: {center_temp:.1f}C',
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2)

        cv2.putText(
            debug,
            f'Hot Pixels: {hot_pixels}',
            (50, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2)

        cv2.putText(
            debug,
            f'Motion: {motion_detected}',
            (50, 180),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2)

        # COMBINE WITH HEATMAP
        combined = cv2.hconcat([
            debug,
            heatmap_resized])

        # PUBLISH IMAGE
        msg = self.bridge.cv2_to_imgmsg(
            combined,
            encoding='bgr8')

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera_frame'
        self.pub_heatmap.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ObjectTemperature()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

