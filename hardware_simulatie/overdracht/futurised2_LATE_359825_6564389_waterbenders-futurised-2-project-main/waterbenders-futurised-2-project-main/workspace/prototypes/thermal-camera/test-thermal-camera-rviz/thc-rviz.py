import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import numpy as np
import cv2
import time
from cv_bridge import CvBridge

class ObjectTemperature(Node):
    def __init__(self):
        super().__init__('object_temperature')

        # Subscriptions
        self.sub_rgb = self.create_subscription(Image, '/front/image', self.rgb_cb, 10)
        self.sub_thermal = self.create_subscription(Image, '/FLIP/thermal_camera', self.thermal_cb, 10)

        # Publisher
        self.pub_heatmap = self.create_publisher(Image, '/thermal/heatmap_image', 10)

        self.bridge = CvBridge()

        # Fixed Scale for Heatmap (Adjust these to your needs)
        self.min_temp = 0.0  
        self.max_temp = 300.0  

        self.rgb = None
        self.thermal = None
        self.last_pub_time = 0
        self.min_interval = 0.1 

        self.get_logger().info("=====Thermal Heatmap Node started=====")

    def rgb_cb(self, msg):
        self.rgb = msg
        self.try_process()

    def thermal_cb(self, msg):
        self.thermal = msg
        self.try_process()

    def try_process(self):
        if self.rgb is None or self.thermal is None:
            return

        now = time.time()
        if now - self.last_pub_time < self.min_interval:
            return
        self.last_pub_time = now

        # 1. PROCESS THERMAL DATA
        thermal_raw = np.frombuffer(
            self.thermal.data,
            dtype=np.uint16
        ).reshape((self.thermal.height, self.thermal.width))

        temp_celsius = (thermal_raw.astype(np.float32) * 0.01) - 273.15

        # 3. NORMALIZE FOR HEATMAP
        norm = (temp_celsius - self.min_temp) / (self.max_temp - self.min_temp + 1e-6)
        norm = np.clip(norm, 0.0, 1.0)

        # 4. CREATE HEATMAP IMAGE
        # Resize to match RGB aspect ratio if needed
        heatmap_gray = (norm * 255).astype(np.uint8)
        heatmap_color = cv2.applyColorMap(heatmap_gray, cv2.COLORMAP_TURBO)
        
        # Resize heatmap to match RGB frame size for display
        heatmap_resized = cv2.resize(heatmap_color, (self.rgb.width, self.rgb.height))
        temp_resized = cv2.resize(temp_celsius, (self.rgb.width, self.rgb.height))

        # Real thermal image center
        thermal_h, thermal_w = temp_celsius.shape
        cx = thermal_w // 2
        cy = thermal_h // 2
        center_temp = temp_celsius[cy, cx]
        
        self.get_logger().info(f"CENTRE TEMP: {center_temp:.2f}C.")
        
        display_cx = int(cx * self.rgb.width / thermal_w)
        display_cy = int(cy * self.rgb.height / thermal_h)

        cv2.circle(
            heatmap_resized,
            (display_cx, display_cy),
            8,
            (255, 255, 255),
            2
        )
        cv2.putText(
            heatmap_resized,
            f"{center_temp:.1f}C",
            (display_cx + 15, display_cy),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            4
        )

        # 6. COMBINE WITH LEGEND
        legend = self.create_legend(height=heatmap_resized.shape[0])
        display = cv2.hconcat([heatmap_resized, legend])

        # 7. PUBLISH
        msg = self.bridge.cv2_to_imgmsg(display, encoding='bgr8')
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera_frame"
        self.pub_heatmap.publish(msg)

    def create_legend(self, height=300, width=60):
        legend = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(height):
            ratio = 1.0 - (i / height)
            color = cv2.applyColorMap(np.uint8([[int(ratio * 255)]]), cv2.COLORMAP_TURBO)[0][0]
            legend[i, :] = color
            if i % (height // 5) == 0:
                val = self.min_temp + ratio * (self.max_temp - self.min_temp)
                cv2.putText(legend, f"{int(val)}C", (5, i + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        return legend

def main(args=None):
    rclpy.init(args=args)
    node = ObjectTemperature()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()