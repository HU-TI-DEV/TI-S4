import gz.transport as gz
from gz.msgs import image_pb2, vector3d_pb2
import numpy as np
import cv2
import time
from gz.msgs.double_pb2 import Double
from gz.msgs.pose_v_pb2 import Pose_V
from gz.msgs.vector3d_pb2 import Vector3d
class Camera:
    def __init__(self):
        self.TOPIC = ""
        self.TOPIC_Depth = ""
        self.TOPIC_pose = ""

        self.data = 1.0
        self.data2 = 0.0

        self.cx = 0
        self.cy = 0

        self.depth_image = None
        self.camera_pose = None
        self.Pw = None
        self.depth_vis = None

        self.depth = 0.0
        self.fov = 1.047

        self.X = 0.0
        self.Y = 0.0
        self.Z = 0.0
        self.angle = 0.0

        self.shape = ""

    def show_depth(self, depth_image):
        # Deze functie wordt gebruikt om een dieptebeeld weer te geven.

        self.depth_vis = depth_image.copy()

        self.depth_vis[~np.isfinite(self.depth_vis)] = 0

        depth_norm = cv2.normalize(self.depth_vis, None, 0, 255, cv2.NORM_MINMAX)
        depth_norm = depth_norm.astype(np.uint8)

        depth_color = cv2.applyColorMap(depth_norm, cv2.COLORMAP_JET)

        cv2.imshow("Depth", depth_color)
        cv2.waitKey(1)

    def quaternion_to_matrix(self, qx, qy, qz, qw):
        # Zet quaternion om naar een 3x3 rotatiematrix
        # qx, qy, qz = vector deel
        # qw = scalaire deel
        return np.array([
            [1 - 2*qy*qy - 2*qz*qz, 2*qx*qy - 2*qz*qw, 2*qx*qz + 2*qy*qw],
            [2*qx*qy + 2*qz*qw, 1 - 2*qx*qx - 2*qz*qz, 2*qy*qz - 2*qx*qw],
            [2*qx*qz - 2*qy*qw, 2*qy*qz + 2*qx*qw, 1 - 2*qx*qx - 2*qy*qy]
        ])

    def pose_cb(self, msg: Pose_V):
        # De oriëntatie van de camera ophalen
        for p in msg.pose:
            if p.name == "camera_link":
                self.camera_pose = p
    def camera_to_world(self, Pc):
        # Coördinaten van het cameraframe naar wereldcoördinaten transformeren

        if self.camera_pose is None:
            return None

        # camera position
        tx = self.camera_pose.position.x
        ty = self.camera_pose.position.y
        tz = self.camera_pose.position.z

        T = np.array([tx, ty, tz])

        # Camera pose (quaternion)
        q = self.camera_pose.orientation
        R = self.quaternion_to_matrix(q.x, q.y, q.z, q.w)

        self.Pw = np.round(R @ Pc + T, 2)
        return self.Pw


    def depth_cb(self, msg):
        # Deze functie ontvangt depth camera data uit Gazebo en zet deze om naar een bruikbare depth image.

        if msg.pixel_format_type == 13:  # float32
            # Zet ruwe bytes om naar float32 numpy-array
            self.depth_image = np.frombuffer(msg.data, dtype=np.float32)

        elif msg.pixel_format_type == 10:  # uint16
            # Zet uint16 om naar meters
            self.depth_image = np.frombuffer(msg.data, dtype=np.uint16).astype(np.float32) * 0.001

        else:
            print("Unknown depth format")
            return

        # Vorm de array om naar een 2D afbeelding
        self.depth_image = self.depth_image.reshape((msg.height, msg.width))

        # Vervang ongeldige waarden (inf/nan)
        self.depth_image = np.where(np.isfinite(self.depth_image), self.depth_image, np.nan)

        self.show_depth(self.depth_image)

    def image_cb(self, msg: image_pb2.Image):
        # Determine number of channels
        if msg.pixel_format_type == 3:   # RGB_INT8
            channels = 3
        elif msg.pixel_format_type == 4: # RGBA_INT8
            channels = 4
        elif msg.pixel_format_type == 1: # L_INT8
            channels = 1
        else:
            print("Unsupported pixel format:", msg.pixel_format_type)
            return

        # Convert message to numpy array
        img = np.frombuffer(msg.data, dtype=np.uint8)
        img = img.reshape((msg.height, msg.width, channels))

        # Convert to BGR for OpenCV
        if channels == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif channels == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Orange color range
        lower_orange = np.array([8, 80, 80])
        upper_orange = np.array([30, 255, 255])

        mask1 = cv2.inRange(hsv, lower_orange, upper_orange)
        mask = mask1

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        crop = img.copy()
        for cnt in contours:
            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            if len(approx) == 3:
                self.shape = "triangle"

            elif len(approx) == 4:
                self.shape = "rectangle"
            elif len(approx) > 6:
                self.shape = "circle"

                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)

                cv2.circle(img, center, radius, (0, 255, 0), 2)

                (x, y), radius = cv2.minEnclosingCircle(cnt)
                self.cx, self.cy = int(x), int(y)

                cv2.circle(img, (self.cx, self.cy), 5, (0, 0, 255), -1)

                # Crop the image to the valve, so anything outside of it becomes irrelevant
                crop = crop[int(center[1]-radius):int(center[1]+radius), int(center[0]-radius):int(center[0]+radius)]
                # Increase contrast
                crop = cv2.convertScaleAbs(crop, alpha=3, beta=0)
                crop = cv2.Canny(crop, 50, 150)
                lines = cv2.HoughLinesP(crop, 1, np.pi/180, threshold=30, minLineLength=int(radius/3), maxLineGap=10)
                crop = cv2.cvtColor(crop, cv2.COLOR_GRAY2BGR)

                angles = []
                if lines is not None:
                    for line in lines:
                        x1, y1, x2, y2 = line[0]
                        # Calculate distance from centre of valve
                        if x1 == x2:
                            dist = abs(radius-x1)
                            line_angle = 1.5707
                        else:
                            a = (y1-y2)/(x1-x2)
                            b = -1
                            c = y1-a*x1
                            dist = abs(a*radius+b*radius+c)/(((a**2)+(b**2))**0.5)
                            line_angle = None
                        if dist < radius/3: # If the line is appropriately close to the centre of the valve
                            if not line_angle:
                                line_angle = np.arctan(a)
                                line_angle = (np.pi+line_angle)%np.pi
                            angles.append(line_angle)
                            cv2.line(img, (int(center[0]-radius)+x1, int(center[1]-radius)+y1), (int(center[0]-radius)+x2, int(center[1]-radius)+y2), (0, 255, 0), 2)
                    if angles:
                        self.angle = round(np.average(angles), 2)
                        print("Handle angle:", self.angle)

                if self.depth_image.shape is not None:
                    h, w = self.depth_image.shape

                roi = self.depth_image[self.cy-5:self.cy+5, self.cx-5:self.cx+5]
                valid = roi[np.isfinite(roi)]
                depth = np.median(valid)
                self.Z = depth

                if not np.isfinite(depth):
                    return

                fx = w / (2 * np.tan(self.fov / 2))
                fy = fx

                cx0 = w / 2
                cy0 = h / 2

                Xn = (self.cx - cx0) / fx
                Yn = (self.cy - cy0) / fy

                Pc_optical = np.array([Xn * self.Z, Yn * self.Z, self.Z])

                R_opt_to_link = np.array([
                    [0, 0, 1],
                    [-1, 0, 0],
                    [0, -1, 0]
                ])

                Pc_link = R_opt_to_link @ Pc_optical


                # wereldcoördinaten transformeren
                self.Pw = self.camera_to_world(Pc_link)

                print("depth:", self.depth)
                print("Pc:", Pc_link)

                if self.Pw is not None:
                    self.X = float(self.Pw[0])
                    self.Y = float(self.Pw[1])
                    self.Z = float(self.Pw[2])
                    print("World Position:", self.Pw)
        # Show image
        cv2.imshow("Gazebo Camera", img)
        cv2.waitKey(1)

camera = Camera()
camera.TOPIC = "/camera/image"
camera.TOPIC_Depth = "camera/depth_image"
camera.TOPIC_pose = "/world/robosubSimulationV4/pose/info"

node = gz.Node()
# Subscribe;
node.subscribe(image_pb2.Image, camera.TOPIC, camera.image_cb)
node.subscribe(image_pb2.Image, camera.TOPIC_Depth, camera.depth_cb)
node.subscribe(Pose_V, camera.TOPIC_pose, camera.pose_cb)

print(f"Subscribed to {camera.TOPIC}.")

# Publisher
pub_angle = node.advertise("/handle_angle", Double)
pub_target = node.advertise("/arm/target", Vector3d)

if __name__ == "__main__":
    # 1. Initialize variables before entering the loop
    last_published_target = np.array([0.0, 0.0, 0.0])
    threshold = 0.15  # 15 centimeter deadband, to prevent noise
    try:
        while True:
            current_target = np.array([camera.X, camera.Y, camera.Z])

            # Calculate distance between current target and last published target
            dist = np.linalg.norm(current_target - last_published_target)

            if dist > threshold:
                target_msg = Vector3d()
                target_msg.x = float(camera.X)
                target_msg.y = float(camera.Y)
                target_msg.z = float(camera.Z)

                pub_target.publish(target_msg)

                # Update the last published target
                last_published_target = current_target

            time.sleep(0.01)

    except KeyboardInterrupt:  # 2. Aligned correctly with 'try'
        print("Exiting...")

    finally:
        cv2.destroyAllWindows()

cv2.destroyAllWindows()