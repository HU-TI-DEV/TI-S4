import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from message_filters import ApproximateTimeSynchronizer, Subscriber
import numpy as np
import cv2
from ultralytics import YOLO


class ObjectTemperature(Node):
    def __init__(self):
        super().__init__('object_temperature')

        # ROS subscriptions
        self.sub_thermal = Subscriber(self, Image, '/FLIP/thermal_camera')
        self.sub_rgb = Subscriber(self, Image, '/camera/image')

        self.ts = ApproximateTimeSynchronizer(
            [self.sub_rgb, self.sub_thermal],
            queue_size=10,
            slop=0.1
        )
        self.ts.registerCallback(self.sync_callback)

        # YOLO model
        self.model = YOLO("yolov8n.pt")

        # expected temperature range (adjust if needed)
        self.min_temp = 0.0
        self.max_temp = 200.0

    # -----------------------------
    # CALLBACK (ROS sync function)
    # -----------------------------
    def sync_callback(self, rgb_msg, thermal_msg):

        rgb = np.frombuffer(rgb_msg.data, dtype=np.uint8).reshape(
            (rgb_msg.height, rgb_msg.width, 3)
        )

        # IMPORTANT: thermal is usually float32 OR uint16 depending on Gazebo setup
        thermal_raw = np.frombuffer(thermal_msg.data, dtype=np.uint16).reshape(
            (thermal_msg.height, thermal_msg.width)
        )

        self.process(rgb, thermal_raw)

    # -----------------------------
    # MAIN PROCESSING PIPELINE
    # -----------------------------
    def process(self, rgb, thermal_raw):

        # Resize thermal to RGB resolution
        thermal_resized = cv2.resize(
            thermal_raw,
            (rgb.shape[1], rgb.shape[0]),
            interpolation=cv2.INTER_NEAREST
        )

        # -----------------------------
        # NORMALIZATION (IMPORTANT FIX)
        # -----------------------------
        min_val = np.min(thermal_resized)
        max_val = np.max(thermal_resized)

        norm = (thermal_resized.astype(np.float32) - min_val) / (max_val - min_val + 1e-6)

        # temperature map
        temp = self.min_temp + norm * (self.max_temp - self.min_temp)

        # -----------------------------
        # TERMINAL OUTPUT
        # -----------------------------
        print(
            f"[THERMAL] avg={np.mean(temp):.2f}C "
            f"min={np.min(temp):.2f}C "
            f"max={np.max(temp):.2f}C"
        )

        # -----------------------------
        # YOLO DETECTION
        # -----------------------------
        results = self.model(rgb, verbose=False)[0]

        # thermal visualization
        thermal_color = cv2.applyColorMap(
            (norm * 255).astype(np.uint8),
            cv2.COLORMAP_INFERNO
        )

        # -----------------------------
        # OBJECT LOOP (YOLO BOXES)
        # -----------------------------
        if results.boxes is not None:

            for box in results.boxes:

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                label = self.model.names[cls]

                # clamp ROI to avoid crash
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(temp.shape[1], x2), min(temp.shape[0], y2)

                region = temp[y1:y2, x1:x2]

                if region.size == 0:
                    continue

                avg_temp = np.mean(region)
                max_temp = np.max(region)

                # print per object
                print(f"{label} → avg {avg_temp:.2f}C | max {max_temp:.2f}C")

                # draw box
                cv2.rectangle(thermal_color, (x1, y1), (x2, y2), (255, 255, 255), 2)

                # label text
                text = f"{label}: {avg_temp:.1f}C ({max_temp:.1f}C max)"

                cv2.putText(
                    thermal_color,
                    text,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                )

        # -----------------------------
        # LEGEND (FIXED SCALE)
        # -----------------------------
        legend = self.create_legend(
            height=rgb.shape[0],
            min_temp=np.min(temp),
            max_temp=np.max(temp)
        )

        # combine views
        display_img = cv2.hconcat([thermal_color, legend])

        # global overlay text
        global_text = f"Temp: {np.min(temp):.1f}C - {np.max(temp):.1f}C"

        cv2.putText(
            display_img,
            global_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.imshow("Thermal Object Temperature", display_img)
        cv2.waitKey(1)

    # -----------------------------
    # LEGEND GENERATION
    # -----------------------------
    def create_legend(self, height, min_temp, max_temp):

        legend = np.zeros((height, 60, 3), dtype=np.uint8)

        for i in range(height):
            ratio = 1 - (i / height)
            temp_val = min_temp + ratio * (max_temp - min_temp)

            color_val = int(ratio * 255)
            color = cv2.applyColorMap(
                np.uint8([[color_val]]),
                cv2.COLORMAP_INFERNO
            )[0][0]

            legend[i, :, :] = color

            if i % 60 == 0:
                cv2.putText(
                    legend,
                    f"{temp_val:.1f}C",
                    (5, i),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 255, 255),
                    1
                )

        return legend


# -----------------------------
# MAIN ROS2 ENTRY POINT
# -----------------------------
def main(args=None):
    rclpy.init(args=args)

    node = ObjectTemperature()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()