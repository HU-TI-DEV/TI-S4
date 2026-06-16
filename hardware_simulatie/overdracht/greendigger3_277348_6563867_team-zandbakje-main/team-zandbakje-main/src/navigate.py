"""
Navigate through all points of interest by repeatedly selecting the nearest unvisited target.

    Author: GrijzePanda
"""
import math
import time
import sys
import code.tests.navigate_to_point as navigate_to_point

INTERFACE_DIRECTORY = "interface"
if INTERFACE_DIRECTORY not in sys.path:
    sys.path.insert(0, INTERFACE_DIRECTORY)

import interface 

POINTS_OF_INTEREST = [
    (20.0, 20.0),  # marker1
    (0.0, 20.0),  # marker2
    (-20.0, 20.0),  # marker3
    (20.0, 0.0),  # marker4
    (0.0, 0.0),  # marker5
    (-20.0, 0.0),  # marker6
    (20.0, -20.0),  # marker7
    (0.0, -20.0),  # marker8
    (-20.0, -20.0),  # marker9
]

visited_points_of_interest = []

navigate_to_point.node, navigate_to_point.pub = navigate_to_point.setup()


def find_nearest_poi():
    state = interface.get_state()

    current_x = state["pose"]["current_x"]
    current_y = state["pose"]["current_y"]
    
    nearest_poi = None
    shortest_distance = float("inf")  # maybe this works?

    for point in POINTS_OF_INTEREST:
        if point in visited_points_of_interest:
            continue

        x, y = point

        dx = x - current_x
        dy = y - current_y

        distance = math.sqrt(dx * dx + dy * dy)

        if distance < shortest_distance:
            shortest_distance = distance
            nearest_poi = point

    return nearest_poi


def main():
    while True:
        target = find_nearest_poi()

        if target is None:
            print("All points of interest are visited, the digger will now take a nap ^_^")
            break
            
        x, y = target

        print(f"\n\nNew target selected: " f"({x:.1f}, {y:.1f})")

        navigate_to_point.navigate_to(x, y)
        visited_points_of_interest.append(target)

        print("\nWait 5 seconds.")  # Just so you don't miss it when you blink...
        time.sleep(5)


if __name__ == "__main__":
    main()
