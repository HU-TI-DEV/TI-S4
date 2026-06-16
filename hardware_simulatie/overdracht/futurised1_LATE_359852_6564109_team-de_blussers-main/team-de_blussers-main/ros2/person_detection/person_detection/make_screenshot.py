import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2
import os
import threading
from datetime import datetime

import sys
import termios
import tty
import time


class MakeScreenshot(Node):
    def __init__(self):
        super().__init__('make_screenshot')
        
        self.bridge = CvBridge()
        
        self.sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.callback,
            10
        )
        
        self.latest_frame = None
        
        self.save_dir = "/workspace/vision/dataset/images/unlabeled"
        os.makedirs(self.save_dir, exist_ok=True)
        
        self.counter = 0
        
        # auto screenshot mode
        self.auto_mode = False
        
        # Keyboard thread
        self.thread = threading.Thread(target=self.keyboard_listener)
        self.thread.daemon = True
        self.thread.start()
        
        self.get_logger().info("Make screenshot node started")
        self.get_logger().info("Press ENTER to snap 1 image")
        self.get_logger().info("Press SPACE to toggle auto capture image")
        
    def callback(self, msg):
        self.latest_frame = msg
        
        
    def get_key(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key
    
    
    def keyboard_listener(self):
        while rclpy.ok():
            
            key = self.get_key()
            
            # SPACE Toggle auto mode
            if key == " ":
                self.auto_mode = not self.auto_mode
                self.get_logger().info(f"AUTO mode: {self.auto_mode}")
                
                if self.auto_mode:
                    threading.Thread(target=self.auto_capture, daemon=True).start()
                    
            # ENTER
            elif key == "\r" or key == "\n":
                self.save_image()
                
    def auto_capture(self):
        self.get_logger().info("AUTO capture started")
        
        while self.auto_mode and rclpy.ok():
            self.save_image()
            time.sleep(2)
        self.get_logger().info("AUTO capture stopped")
    
    def save_image(self):
        if self.latest_frame is None:
            return
    
        frame = self.bridge.imgmsg_to_cv2(
            self.latest_frame,
            desired_encoding='bgr8'
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        filename = f"{self.save_dir}/img_{timestamp}.jpg"
        
        cv2.imwrite(filename, frame)
        
        self.counter += 1
        
        self.get_logger().info(f"Saved image {self.counter}: {filename}")
            
def main(args=None):
    rclpy.init(args=args)
    node = MakeScreenshot()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    