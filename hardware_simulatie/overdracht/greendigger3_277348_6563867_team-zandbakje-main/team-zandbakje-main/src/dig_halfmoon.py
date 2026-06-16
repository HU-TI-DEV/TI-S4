"""Digging script for half-moon pattern that consists of 4 phases:
1. Lift from current actual position to digging location
2. Plunge
3. Scrape
4. Retract

To change the pattern, adjust the START_ANGLE and END_ANGLE, and the parameters in each phase. The current parameters are tuned for a half-moon pattern that covers a 2.4 radian sweep in front of the robot.

To change the number of digs, adjust DIG_COUNT. The current value of 16 results in a sweep with 16 evenly spaced digs across the 2.4 radian range, which is about one dig every 0.15 radians (8.6 degrees).

To change the fallback travel positions, adjust the TRAVEL_SHOULDER, TRAVEL_ELBOW, and TRAVEL_WRIST parameters. The current values are tuned to be a safe position that is above any holes dug by the GreenDigger so that the arm can move across the surface without colliding with the terrain.

To change the angle of the digs, adjust the joint parameters in the desired phase. The first value in each joint parameter is the starting position for that phase, and the second value is the ending position. The duration of each phase can be adjusted by changing the number of iterations and the sleep time in each loop. 

    Author: Ocarian
"""

import time
import sys
sys.path.append("interface")
import interface

SIDE = 1.57
DIG_COUNT = 16
START_ANGLE = -1.2
END_ANGLE = 1.2

# Safe fallback positions for moving across the surface without colliding with the terrain
TRAVEL_SHOULDER = -1.5
TRAVEL_ELBOW    = 0.6
TRAVEL_WRIST    = -0.8

def dig_halfmoon():
    for dig_index in range(DIG_COUNT):
        dig_progress = dig_index / (DIG_COUNT - 1)
        sweep = START_ANGLE + (END_ANGLE - START_ANGLE) * dig_progress

        # Phase 1 — lift from current actual position to digging location
        arm = interface.get_state().get("arm", {})
        s_start = arm.get("shoulder_lift_joint") or TRAVEL_SHOULDER
        e_start = arm.get("elbow_joint")         or TRAVEL_ELBOW
        w_start = arm.get("wrist_1_joint")       or TRAVEL_WRIST

        for i in range(60):
            p = i / 59.0
            interface.publish_arm_command(
                shoulder_pan_joint=SIDE + sweep,
                shoulder_lift_joint=s_start + (TRAVEL_SHOULDER - s_start) * p,
                elbow_joint        =e_start + (TRAVEL_ELBOW    - e_start) * p,
                wrist_1_joint      =w_start + (TRAVEL_WRIST    - w_start) * p,
            )
            time.sleep(0.005)

        # To make sure we are at the digging location before plunging
        time.sleep(0.3)

        # PHASE 2 — plunge
        for i in range(50):
            p = i / 49.0
            interface.publish_arm_command(
                shoulder_pan_joint=SIDE + sweep,
                shoulder_lift_joint=-1.0 - 0.2 * p,
                elbow_joint        = 1.0 + 1.2 * p,
                wrist_1_joint      =-1.5 - 0.2 * p,
            )
            time.sleep(0.005)

        # PHASE 3 — scrape
        for i in range(300):
            p = i / 299.0
            interface.publish_arm_command(
                shoulder_pan_joint=SIDE + sweep,
                shoulder_lift_joint=-1.2 + 0.3 * p,
                elbow_joint        = 2.2 - 0.2 * p,
                wrist_1_joint      =-1.7 + 0.2 * p,
            )
            time.sleep(0.005)
        
        time.sleep(0.3)

        # PHASE 4 — retract
        for i in range(40):
            p = i / 39.0
            interface.publish_arm_command(
                shoulder_pan_joint=SIDE + sweep,
                shoulder_lift_joint=-1.1 + 0.6 * p,
                elbow_joint        = 1.8 - 0.2 * p,
                wrist_1_joint      =-1.5 + 0.3 * p,
            )
            time.sleep(0.005)

    interface.publish_arm_pose("arm_out_of_the_way")