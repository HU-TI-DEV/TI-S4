import time

import cv2
import numpy as np
from gz.msgs.image_pb2 import Image
from gz.transport import Node

CAMERA_TOPIC = "/digger/camera"
WINDOW_NAME = "Digger POV :)"

latest_frame = None


def image_to_frame(message):
    width = message.width
    height = message.height
    image_data = np.frombuffer(message.data, dtype=np.uint8)

    if image_data.size == width * height * 3:
        rgb_frame = image_data.reshape((height, width, 3))
        return cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

    if image_data.size == width * height:
        return image_data.reshape((height, width))

    print(
        "Unsupported camera frame size: "
        f"{image_data.size} bytes for {width}x{height}"
    )
    return None


def camera_cb(message):
    global latest_frame

    latest_frame = image_to_frame(message)


def main():
    node = Node()
    node.subscribe(Image, CAMERA_TOPIC, camera_cb)

    print(f"Listening to {CAMERA_TOPIC}")
    print("Press q to quit.")

    while True:
        if latest_frame is not None:
            cv2.imshow(WINDOW_NAME, latest_frame)

            if cv2.waitKey(5) & 0xFF == ord("q"):
                break
        else:
            time.sleep(0.05)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
