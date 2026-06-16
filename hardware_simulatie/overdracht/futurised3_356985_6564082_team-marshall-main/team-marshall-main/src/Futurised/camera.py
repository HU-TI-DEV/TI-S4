#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Bool
from cv_bridge import CvBridge
import cv2
import numpy as np

class DoorDetectorNode(Node):
    def __init__(self):
        super().__init__('door_detector_node')
        
        self.subscription = self.create_subscription(
            Image, '/camera', self.image_callback, 10
        )
        self.bridge = CvBridge()
        self.door_pub = self.create_publisher(Bool, '/door_detected', 10)
        
        self.latest_frame = None
        self.get_logger().info('Door Detector Actief')

    def image_callback(self, msg):
        try:
            rgb_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
            cv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        except Exception as foutmelding:
            self.get_logger().error(f'Fout bij omzetten afbeelding: {foutmelding}')
            return

        hoogte, breedte, _ = cv_image.shape
        
        # Voor Sobel filter is het belangerijk om de image eerst grijs te maken en een gaussain-blur toe te passen, voor beste resultaat.
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Sobel-X filter toepassen om ALLES wat verticaal is te highlighten
        # Dit negeert horizontale vloerlijnen en reageert puur op de muren/obstakel hun randen.
        sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        sobelx_abs = np.absolute(sobelx)
        sobel_8u = np.uint8(sobelx_abs)
        
        # Filtert lichte ruis weg
        _, thresh = cv2.threshold(sobel_8u, 40, 255, cv2.THRESH_BINARY)

        # We focussen op het midden-horizontale gedeelte van het scherm (waar de muren stoppen)
        roi_top = int(hoogte * 0.2)
        roi_bottom = int(hoogte * 0.8)
        roi = thresh[roi_top:roi_bottom, :]

        column_counts = np.sum(roi == 255, axis=0)

        # Vebreding zoekzones zodat de muren ook te zien zijn van grotere afstanden
        left_zone = column_counts[0:int(breedte * 0.50)]
        left_wall_x = np.argmax(left_zone) if len(left_zone) > 0 else None
        
        # Checkt of de piek krachtig genoeg is (minimale hoogte van de muur in pixels)
        if left_wall_x is not None and left_zone[left_wall_x] < 20:
            left_wall_x = None

        right_zone_start = int(breedte * 0.50)
        right_zone = column_counts[right_zone_start:breedte]
        if len(right_zone) > 0:
            right_wall_x = np.argmax(right_zone) + right_zone_start
            if column_counts[right_wall_x] < 20:
                right_wall_x = None
        else:
            right_wall_x = None

        # Checkt deurgat: filtert op bruikbare breedte en negeert objecten te ver in de verte 
        door_found = False
        if left_wall_x is not None and right_wall_x is not None:
            afstand = right_wall_x - left_wall_x
            
            # > 25%: Negeer gaten die te ver weg zijn (voorkomt ruis)
            # < 98%: Voorkom dat muren buiten het camerabeeld verdwijnen als we er te dichtbij staan
            if (breedte * 0.25) < afstand < (breedte * 0.98):
                
                # Dieptecheck: telt de muurhoogtes op om te meten of de muren dichtbij (hoog) of ver weg (laag) zijn
                totale_hoogte_indicator = column_counts[left_wall_x] + column_counts[right_wall_x]
                
                # Afstandscheck: muren moeten hoog genoeg zijn (groot in beeld) om ruis in de verte te negeren.
                # Lager dan 50 = robot reageert sneller van veraf; hoger = robot moet dichterbij zijn.
                if totale_hoogte_indicator > 50:
                    door_found = True

        # Publiceer status naar explorer.py
        bool_msg = Bool()
        bool_msg.data = door_found
        self.door_pub.publish(bool_msg)

        # Opencv Visuals
        if left_wall_x is not None:
            # Rinker-muurrand
            cv2.line(cv_image, (left_wall_x, 0), (left_wall_x, hoogte), (255, 0, 0), 2)
        if right_wall_x is not None:
            # Rechter-muurrand
            cv2.line(cv_image, (right_wall_x, 0), (right_wall_x, hoogte), (255, 0, 0), 2)

        if door_found:
            mitten_y = int(hoogte / 2)
            midden_x = int((left_wall_x + right_wall_x) / 2)
            # Groene balk tussen de gedetecteerde lijnen.
            cv2.line(cv_image, (left_wall_x, mitten_y), (right_wall_x, mitten_y), (0, 255, 0), 4)
            cv2.putText(cv_image, "DEURPAS GEDETECTEERD", (midden_x - 120, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        else:
            cv2.putText(cv_image, "Scannen op deurstijlen...", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        self.latest_frame = cv_image


def main(args=None):
    rclpy.init(args=args)
    node = DoorDetectorNode()
    window_name = "Door Detection - Live Demo"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)

    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.01)
            if node.latest_frame is not None:
                cv2.imshow(window_name, node.latest_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()