"""Keyboard movement for the GreenDigger.

This script reads arrow key input from the terminal and publishes
`gz.msgs.twist_pb2.Twist` messages to the GreenDigger command velocity
topic. The left/right arrows turn the vehicle, up/down move it forward
and backward, and `q` quit the loop.

    Author: Ocarian
"""

import sys
import termios
import tty

from gz.msgs.twist_pb2 import Twist
from gz.transport import Node

CMD_VEL_TOPIC = "/model/digger/cmd_vel"
FORWARD_SPEED = 2.0
TURN_SPEED = 6.0


def get_key():
    """Read a single keyboard keypress from the terminal.

    This function temporarily switches the terminal into raw mode so it can
    capture arrow keys.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)

        if ch1 == '\x1b':
            # Arrow keys produce a three-character escape sequence.
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch1 + ch2 + ch3
        else:
            return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def get_twist_from_keyboard():
    """Convert a keypress into a Twist command.

    Returns a `Twist` message with linear and angular velocity values.
    If the user presses `q`, it returns None to signal the main loop to quit.
    """
    key = get_key()

    linear = 0.0
    angular = 0.0

    if key == '\x1b[A':      # UP
        linear = FORWARD_SPEED
    elif key == '\x1b[B':    # DOWN
        linear = -FORWARD_SPEED
    elif key == '\x1b[C':    # RIGHT
        angular = -TURN_SPEED
    elif key == '\x1b[D':    # LEFT
        angular = TURN_SPEED
    elif key == " " or key == "s":
        # Stop command: keep velocity at zero.
        pass
    elif key == 'q':
        return None  # signal quit

    msg = Twist()
    msg.linear.x = linear
    msg.angular.z = angular

    return msg


def main():
    node = Node()
    publisher = node.advertise(CMD_VEL_TOPIC, Twist)

    print("Keyboard drive control")
    print("Arrow up/down: forward/backward")
    print("Arrow left/right: turn")
    print("Space or s: stop")
    print("q: quit")

    while True:
        msg = get_twist_from_keyboard()

        if msg is None:
            # Publish a zero command before exiting to stop the robot.
            publisher.publish(Twist())
            break

        publisher.publish(msg)
        print(
            f"linear_x={msg.linear.x:.2f}, "
            f"angular_z={msg.angular.z:.2f}"
        )


if __name__ == "__main__":
    main()
