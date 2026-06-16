import os
import sys
import termios
import tty

# Positie bijhouden
targets = {
    "base": 0.0,
    "upper_arm": 0.0,
    "lower_arm": 0.0,
    "palm": 0.0,
    "claw_rot": 0.0,
    "fingers": 0.0
}

# Stapgrootte per toetsaanslag (in radialen, +/- 5.7 graden)
STEP = 0.1

# Koppeling gazebo joints
JOINTS = {
    "base": "robosub_base_to_robosub_rotating_base",
    "upper_arm": "robosub_rotating_base_to_upper_arm_segment",
    "lower_arm": "upper_arm_segment_to_lower_arm_segment",
    "palm": "lower_arm_segment_to_palm_segment",
    "claw_rot": "palm_segment_to_rotating_base_claw",
    "upper_finger": "rotating_base_claw_to_upper_finger_claw",
    "lower_finger": "rotating_base_claw_to_lower_finger_claw"
}

# Vingers tegelijkertijd bewegen
def move_fingers(direction):

    targets["fingers"] += (direction * 0.05)

    if targets["fingers"] < 0: targets["fingers"] = 0.0
    if targets["fingers"] > 0.785: targets["fingers"] = 0.785
    
    angle_upper = targets["fingers"]
    angle_lower = -targets["fingers"] 
    
    topic_upper = f"/model/Robosub_arm/joint/{JOINTS['upper_finger']}/0/cmd_pos"
    topic_lower = f"/model/Robosub_arm/joint/{JOINTS['lower_finger']}/0/cmd_pos"
    
    os.system(f"gz topic -t {topic_upper} -m gz.msgs.Double -p 'data: {angle_upper}'")
    os.system(f"gz topic -t {topic_lower} -m gz.msgs.Double -p 'data: {angle_lower}'")



def send_position(joint_key):
    joint_name = JOINTS[joint_key]
    angle = targets[joint_key]
    topic = f"/model/Robosub_arm/joint/{joint_name}/0/cmd_pos"
    cmd = f"gz topic -t {topic} -m gz.msgs.Double -p 'data: {angle}'"
    os.system(cmd)

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

print("--- Robosub Arm Position Controller ---")
print("Besturing:")
print("Base: A / D | Upper Arm: W / S | Lower Arm: Q / E")
print("Palm: R / F | Claw Rotation T / G | Claw: Z / X | STOP: ESC")
print("---------------------------------------")

try:
    while True:
        key = get_key()
        
        if key == '\x1b': 
            break
            
        # Logica voor elke toets
        if key == 'w': targets["upper_arm"] += STEP; send_position("upper_arm")
        elif key == 's': targets["upper_arm"] -= STEP; send_position("upper_arm")
        elif key == 'a': targets["base"] += STEP; send_position("base")
        elif key == 'd': targets["base"] -= STEP; send_position("base")
        elif key == 'q': targets["lower_arm"] += STEP; send_position("lower_arm")
        elif key == 'e': targets["lower_arm"] -= STEP; send_position("lower_arm")
        elif key == 'r': targets["palm"] += STEP; send_position("palm")
        elif key == 'f': targets["palm"] -= STEP; send_position("palm")
        elif key =='t' : targets["claw_rot"] += STEP; send_position("claw_rot")
        elif key == 'g': targets["claw_rot"] -= STEP; send_position("claw_rot")
        elif key == 'z': move_fingers(1)
        elif key == 'x': move_fingers(-1)


except KeyboardInterrupt:
    pass

print("\nBesturing gestopt.")