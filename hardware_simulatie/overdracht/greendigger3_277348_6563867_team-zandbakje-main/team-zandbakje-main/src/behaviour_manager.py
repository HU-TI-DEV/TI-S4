"""State machine for automating decisions based on sensor data.

    Author: Replitard
    Contributors: GrijzePanda, Ocarian
"""

import argparse
import json
import sys
import time
from enum import Enum

INTERFACE_DIRECTORY = "interface"
if INTERFACE_DIRECTORY not in sys.path:
    sys.path.insert(0, INTERFACE_DIRECTORY)


# Imports for the behaviour manager to use
import interface
import drive_pid
import drive_poi
import dig_halfmoon


DEFAULT_PERIOD_S = 0.1
DEFAULT_DURATION_S = None
DEFAULT_DRIVE_LINEAR_X = 0.5
DEFAULT_DRIVE_ANGULAR_Z = 0.0

IDLE_ARM_POSE = "arm_out_of_the_way"
DIG_ARM_POSE = "dig"

# Uses json with coordinate data instead of hard coded list.
def load_poi_route(file_path: str) -> list[tuple[float, float]]:
    with open(file_path) as f:
        data = json.load(f)
    return [(entry["x"], entry["y"]) for entry in data]

# States.
class BehaviourState(Enum):
    MANUAL = "manual"
    IDLE = "idle"
    DRIVE = "drive"
    DIG = "dig"
    ERROR = "error"
    # AVOID = "avoid"


class BehaviourManager:
    # Initialise the behaviour manager.
    def __init__(
        self,
        state: BehaviourState,
        drive_linear_x: float,
        drive_angular_z: float,
        control_loop_interval_s: float = DEFAULT_PERIOD_S,
        target_heading_degrees: float | None = None,
        target_x: float | None = None,
        target_y: float | None = None,
        points_of_interest: list[tuple[float, float]] | None = None,
        dig_heading_degrees: float | None = None, # Temporary heading enforcement.
    ) -> None:
        self.state = state
        self.drive_linear_x = drive_linear_x
        self.drive_angular_z = drive_angular_z
        self.control_loop_interval_s = control_loop_interval_s
        self.target_heading_degrees = target_heading_degrees
        self.target_x = target_x
        self.target_y = target_y
        self.points_of_interest = points_of_interest or []
        self.current_poi_index = 0
        self.dig_command_sent = False
        self.idle_arm_pose_sent = False
        self.dig_heading_degrees = dig_heading_degrees # Temporary heading enforcement.
        drive_pid.reset_pid()

    def set_state(self, new_state: BehaviourState) -> None:
        """Transition to a new state and reset its entry flags."""
        self.state = new_state
        if new_state == BehaviourState.IDLE:
            self.idle_arm_pose_sent = False
        elif new_state == BehaviourState.DIG:
            self.dig_command_sent = False

    def step(self) -> None:
        """Run one(1) behaviour manager update."""
        sensor_state = interface.get_state()

        # Guard runs before the handler so ERROR is active this tick, not the next.
        if self.state != BehaviourState.MANUAL and self.chassis_has_contact(sensor_state):
            self.set_state(BehaviourState.ERROR)

        if self.state == BehaviourState.MANUAL:
            self.handle_manual()
        elif self.state == BehaviourState.IDLE:
            self.handle_idle()
        elif self.state == BehaviourState.DRIVE:
            self.handle_drive(sensor_state)
        elif self.state == BehaviourState.DIG:
            self.handle_dig()
        elif self.state == BehaviourState.ERROR:
            self.handle_error()

    def chassis_has_contact(self, sensor_state: dict) -> bool:
        """Return if the chassis contact sensor is touching something."""
        contact_state = sensor_state.get("contact", {})
        return bool(contact_state.get("chassis_touching", False))

    def handle_manual(self) -> None:
        """For keyboard control."""

    def handle_idle(self) -> None:
        """Stop active drive movement, reset arm."""
        interface.stop_drive()

        if not self.idle_arm_pose_sent:
            interface.publish_arm_pose(IDLE_ARM_POSE)
            self.idle_arm_pose_sent = True

    def handle_drive(self, sensor_state: dict) -> None:
        """Publish the configured drive command."""
        # Drive to a single target coordinate.
        if self.target_x is not None and self.target_y is not None:
            linear_x, angular_z, target_reached = drive_poi.compute_poi_command(
                sensor_state,
                self.target_x,
                self.target_y,
                self.control_loop_interval_s,
            )
            interface.publish_drive_command(linear_x=linear_x, angular_z=angular_z)
            if target_reached:
                drive_pid.reset_pid()
                self.set_state(BehaviourState.IDLE)
            return

        # Step through a multi-point route.
        if self.points_of_interest:
            target_x, target_y = self.points_of_interest[self.current_poi_index]
            linear_x, angular_z, target_reached = drive_poi.compute_poi_command(
                sensor_state,
                target_x,
                target_y,
                self.control_loop_interval_s,
            )
            interface.publish_drive_command(linear_x=linear_x, angular_z=angular_z)
            if target_reached:
                drive_pid.reset_pid()
                self.set_state(BehaviourState.DIG)
            return

        # Hold a heading using the PID controller.
        if self.target_heading_degrees is not None:
            linear_x, angular_z, target_reached = drive_pid.compute_heading_command(
                sensor_state,
                self.target_heading_degrees,
                self.control_loop_interval_s,
            )
            interface.publish_drive_command(linear_x=linear_x, angular_z=angular_z)
            if target_reached:
                drive_pid.reset_pid()
                self.set_state(BehaviourState.IDLE)
            return

        # Fallback: publish the raw speed values set at construction.
        interface.publish_drive_command(
            linear_x=self.drive_linear_x,
            angular_z=self.drive_angular_z,
        )

    def _advance_or_idle(self) -> None:
        self.current_poi_index += 1
        if self.current_poi_index < len(self.points_of_interest):
            self.set_state(BehaviourState.DRIVE)
        else:
            self.set_state(BehaviourState.IDLE)

    def handle_dig(self) -> None:
        """Block on the full dig sequence, then advance to the next POI or idle."""
        interface.stop_drive()

        if not self.dig_command_sent:
            self.dig_command_sent = True

            # Temporary heading fix.
            if self.dig_heading_degrees is not None:
                while True:
                    sensor_state = interface.get_state()
                    _, angular_z, done = drive_pid.compute_heading_command(
                        sensor_state, self.dig_heading_degrees, self.control_loop_interval_s
                    )
                    if done:
                        break
                    interface.publish_drive_command(linear_x=0.0, angular_z=angular_z)
                    time.sleep(self.control_loop_interval_s)
            interface.stop_drive()

            dig_halfmoon.dig_halfmoon()
            self._advance_or_idle()

    def handle_error(self) -> None:
        """Stop movement when a blocking condition is detected. Such as object in the way, sensor mismatch, etc."""
        interface.stop_drive()


def build_argument_parser() -> argparse.ArgumentParser:
    """Temporary for fast debugging // Build command-line arguments for the behaviour manager."""
    parser = argparse.ArgumentParser(
        description="Run a simple state based behaviour manager."
    )
    parser.add_argument(
        "--state",
        choices=[state.value for state in BehaviourState],
        default=BehaviourState.IDLE.value,
        help="Initial behaviour state.",
    )
    parser.add_argument(
        "--duration-s",
        type=float,
        default=DEFAULT_DURATION_S,
        help="How long to run before stopping.",
    )
    parser.add_argument(
        "--period-s",
        type=float,
        default=DEFAULT_PERIOD_S,
        help="Delay between behaviour updates.",
    )
    parser.add_argument(
        "--drive-linear-x",
        type=float,
        default=DEFAULT_DRIVE_LINEAR_X,
        help="Forward drive speed used in the drive state.",
    )
    parser.add_argument(
        "--drive-angular-z",
        type=float,
        default=DEFAULT_DRIVE_ANGULAR_Z,
        help="Turn speed used in the drive state.",
    )
    parser.add_argument(
        "--target-heading-degrees",
        type=float,
        default=None,
        help="Optional heading target for the drive PID controller.",
    )
    parser.add_argument(
        "--target-x",
        type=float,
        default=None,
        help="Optional x target for POI driving.",
    )
    parser.add_argument(
        "--target-y",
        type=float,
        default=None,
        help="Optional y target for POI driving.",
    )
    parser.add_argument(
        "--poi-file",
        type=str,
        default=None,
        help="Path to a JSON file defining the POI route.",
    )
    # Temporary heading enforcement.
    parser.add_argument(
        "--dig-heading-degrees",
        type=float,
        default=0.0,
        help="Heading to rotate to before each dig.",
    )
    return parser


def main() -> int:
    """Run the behaviour manager from the command line."""
    arguments = build_argument_parser().parse_args()
    if arguments.duration_s is not None and arguments.duration_s <= 0.0:
        raise ValueError("--duration-s must be positive")
    if arguments.period_s <= 0.0:
        raise ValueError("--period-s must be positive")
    if (arguments.target_x is None) != (arguments.target_y is None):
        raise ValueError("--target-x and --target-y must be provided together")
    if arguments.target_heading_degrees is not None and arguments.target_x is not None:
        raise ValueError("Use either --target-heading-degrees or --target-x/--target-y")
    if arguments.poi_file and arguments.target_x is not None:
        raise ValueError("Use either --poi-file or --target-x/--target-y")
    if arguments.poi_file and arguments.target_heading_degrees is not None:
        raise ValueError("Use either --poi-file or --target-heading-degrees")

    interface.start_subscribers()

    manager = BehaviourManager(
        state=BehaviourState(arguments.state),
        drive_linear_x=arguments.drive_linear_x,
        drive_angular_z=arguments.drive_angular_z,
        control_loop_interval_s=arguments.period_s,
        target_heading_degrees=arguments.target_heading_degrees,
        target_x=arguments.target_x,
        target_y=arguments.target_y,
        points_of_interest=load_poi_route(arguments.poi_file) if arguments.poi_file else None,
        dig_heading_degrees=arguments.dig_heading_degrees,
    )

    print(f"Behaviour manager state: {manager.state.value}")
    print("Press Ctrl+C to stop.")

    start_time = time.time()

    try:
        while arguments.duration_s is None or time.time() - start_time < arguments.duration_s:
            manager.step()
            time.sleep(arguments.period_s)
    except KeyboardInterrupt:
        print("Stopping behaviour manager.")
    finally:
        interface.stop_drive()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
