import subprocess
import rclpy
import sys
from rclpy.node import Node
from visualization_msgs.msg import Marker
import threading
import time

class GazeboAudioToRvizBridge(Node):
    def __init__(self):
        super().__init__('gazebo_audio_rviz_bridge')
        
        # Setup Marker Publisher
        self.publisher_ = self.create_publisher(Marker, '/robot_audio_status', 10)
        
        self.gazebo_topic = "/model/FLIP/model/car_mic/sensor/mic_1/detection"
        self.last_heartbeat = time.time()
        
        self.get_logger().info(f"Starting bridge. Publishing 3D Text Markers for RViz (Fixed Frame: map)...")

        # Thread 1: Read data from Gazebo topic
        self.bridge_thread = threading.Thread(target=self.stream_gazebo_data, daemon=True)
        self.bridge_thread.start()
        
        # Thread 2: Check for data timeouts and update RViz accordingly
        self.watchdog_thread = threading.Thread(target=self.audio_watchdog, daemon=True)
        self.watchdog_thread.start()

    def publish_text_marker(self, text, is_active=True):
        marker = Marker()
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.header.frame_id = "map" 
        marker.ns = "audio_sensor"
        marker.id = 0
        marker.type = Marker.TEXT_VIEW_FACING
        marker.action = Marker.ADD
        
        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 2.5 
        
        marker.text = text
        marker.scale.z = 0.5 
        
        # Color: green for active audio, orange for no audio
        if is_active:
            marker.color.r = 0.0; marker.color.g = 1.0; marker.color.b = 0.0
        else:
            marker.color.r = 1.0; marker.color.g = 0.3; marker.color.b = 0.0
            
        marker.color.a = 1.0 
        self.publisher_.publish(marker)

    def stream_gazebo_data(self):
        command = f"source /usr/share/gz/setup.sh 2>/dev/null || true; gz topic -e -t {self.gazebo_topic}"
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                shell=True,
                executable="/bin/bash"
            )
            
            current_source = "Unknown"
            
            for line in process.stdout:
                clean_line = line.strip()
                
                if 'key:' in clean_line:
                    parts = clean_line.split("/")
                    if parts:
                        current_source = parts[-1].replace('"', '')
                
                elif clean_line.startswith("data:"):
                    raw_val = clean_line.split(":")[-1].strip()
                    try:
                        volume = float(raw_val)
                    except ValueError:
                        continue
                    
                    # Update timestamp of last received data
                    self.last_heartbeat = time.time()
                    
                    display_text = f"Audio Detected!\nSource: {current_source}\nVolume: {volume:.3f}"
                    self.publish_text_marker(display_text, is_active=True)
                    
                    # print(f"-> Bridged: {current_source} | Vol: {volume:.3f}")
                    # sys.stdout.flush()
                    
                    current_source = "Unknown"
                    
        except Exception as e:
            self.get_logger().error(f"Failed to stream Gazebo data: {e}")

    def audio_watchdog(self):
        # If no audio data is received for more than 2 seconds, update RViz to show "No Audio Detected"
        while rclpy.ok():
            if time.time() - self.last_heartbeat > 2.0:
                display_text = "No Audio Detected\n(Volume < 0.100)"
                self.publish_text_marker(display_text, is_active=False)
            time.sleep(0.5)

def main(args=None):
    rclpy.init(args=args)
    node = GazeboAudioToRvizBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # ── USE try_shutdown() INSTEAD OF shutdown() ────────────────────────
        rclpy.try_shutdown()

if __name__ == "__main__":
    main()