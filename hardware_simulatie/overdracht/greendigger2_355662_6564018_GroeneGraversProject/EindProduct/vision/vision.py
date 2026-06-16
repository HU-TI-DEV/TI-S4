import cv2
import numpy as np
import time

while True:

    # load picture
    image = cv2.imread("build/photoVision.jpg")

    if image is None:
        print("image not found")
        time.sleep(1)
        continue

    print("\nnew image loaded")

    output = image.copy()

    # lists for detection
    rectangles = []
    circles_list = []
    lines_list = []
    trees = []

    vertical_lines = []
    horizontal_lines = []

    # grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # blur
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    # edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # contour detection
    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    print("amount of contours found:", len(contours))

    # Contours
    for contour in contours:

        area = cv2.contourArea(contour)

        # ignore noise
        if area < 1000:
            continue

        peri = cv2.arcLength(contour, True)

        approx = cv2.approxPolyDP(
            contour,
            0.02 * peri,
            True
        )

        vertices = len(approx)

        x, y, w, h = cv2.boundingRect(approx)

        shape = "unknown"

        # triangle
        if vertices == 3:
            shape = "triangle"

        # rectangle
        elif vertices == 4:
            aspect_ratio = w / float(h)
            shape = "rectangle"

        # save rectangle for tree detection
        if shape == "rectangle":
            cx = x + w // 2
            cy = y + h // 2
            rectangles.append((x, y, w, h, cx, cy))

        # draw contours
        cv2.drawContours(output, [approx], -1, (0, 255, 0), 3)

        cv2.putText(
            output,
            shape,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    # circle detection
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=50,
        param1=100,
        param2=30,
        minRadius=20,
        maxRadius=100
    )

    if circles is not None:

        circles = np.round(circles[0, :]).astype("int")

        print("amount of circles found:", len(circles))

        for (x, y, r) in circles:

            circles_list.append((x, y, r))

            # draw circle
            cv2.circle(output, (x, y), r, (0, 255, 0), 3)

            # center
            cv2.circle(output, (x, y), 2, (0, 0, 255), 3)

            cv2.putText(
                output,
                "circle",
                (x - 40, y - r - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

    # line detection (NEW)
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=80,
        minLineLength=40,
        maxLineGap=10
    )

    if lines is not None:

        for line in lines:
            x1, y1, x2, y2 = line[0]
            lines_list.append((x1, y1, x2, y2))

            # draw lines (debug)
            cv2.line(output, (x1, y1), (x2, y2), (0, 255, 255), 1)

            dx = x2 - x1
            dy = y2 - y1

            if dx == 0:
                angle = 90
            else:
                angle = abs(np.degrees(np.arctan(dy / dx)))

            # classify line type
            if 70 <= angle <= 110:
                vertical_lines.append((x1, y1, x2, y2))

            elif angle <= 20 or angle >= 160:
                horizontal_lines.append((x1, y1, x2, y2))

    # Tree Detection
    trees = []

    for cx, cy, r in circles_list:

        v_count = 0

        circle_left = cx - r
        circle_right = cx + r
        trunk_top = cy + r

        for x1, y1, x2, y2 in vertical_lines:

            mx = (x1 + x2) // 2
            my = (y1 + y2) // 2

            # must be below circle
            if my < trunk_top:
                continue

            # must be inside circle width
            if not (circle_left <= mx <= circle_right):
                continue

            v_count += 1

        # final rule: at least 2 vertical lines
        if v_count >= 2:

            trees.append((cx, cy, r))

        # draw trees
        for (cx, cy, r) in trees:

            cv2.circle(output, (cx, cy), r, (255, 0, 0), 3)

            cv2.putText(
                output,
                "tree",
                (cx - r, cy - r - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2
            )


    print("amount of trees found:", len(trees))

    # set flag in stopSignal.txt
    if len(trees) >= 1:
        with open("../controller/stopSignal.txt", "w") as f:
            f.write("1")
    else:
        with open("../controller/stopSignal.txt", "w") as f:
            f.write("0")

    # OUTPUT
    cv2.imshow("edges", edges)
    cv2.imshow("output", output)

    key = cv2.waitKey(100)

    # ESC to close window
    if key == 27:
        break

    # small break so gazebo can write
    time.sleep(2)

cv2.destroyAllWindows()