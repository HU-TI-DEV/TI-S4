"""
Interface Usage Info:
1. Add the topic constant and message import at the top of this file.
2. Add a new entry under `state` with simple Python values (no Gazebo types).
3. Add a callback that updates that entry and refreshes `last_update_time`.
4. Subscribe in `start_subscribers()` using node.subscribe(MessageType, TOPIC, callback).

    Author: Replitard
    Contributors: GrijzePanda, Ocarian
"""

import time
import subprocess
from dataclasses import dataclass
from gz.transport import Node

from gz.msgs.contacts_pb2 import Contacts
from gz.msgs.double_pb2 import Double
from gz.msgs.image_pb2 import Image
from gz.msgs.imu_pb2 import IMU
from gz.msgs.laserscan_pb2 import LaserScan
from gz.msgs.twist_pb2 import Twist
from gz.msgs.pose_v_pb2 import Pose_V
from gz.msgs.model_pb2 import Model

# One can add helpers here for ease of use. Not required, since it's only meant to streamline commands / make troubleshooting easier.
import arm_helper

# --------------------------------------------------------------------------

CMD_VEL_TOPIC = "/model/digger/cmd_vel"
IMU_TOPIC = "/digger/imu"
LIDAR_TOPIC = "/digger/lidar"
CAMERA_TOPIC = "/digger/camera"
CHASSIS_CONTACT_TOPIC = "/digger/chassis_contact"
POSE_TOPIC = "/world/starting_environment/dynamic_pose/info"
ARM_STATE_TOPIC = "/arm/joint_state"
BUCKET_CONTACT_TOPIC = "/world/starting_environment/model/digger/model/digger/model/mounted_arm/link/ee_link/sensor/rod_contact/contact"

ARM_TOPIC_BY_JOINT = {
    "shoulder_pan_joint": "/arm/joint/shoulder_pan_joint/cmd_pos",
    "shoulder_lift_joint": "/arm/joint/shoulder_lift_joint/cmd_pos",
    "elbow_joint": "/arm/joint/elbow_joint/cmd_pos",
    "wrist_1_joint": "/arm/joint/wrist_1_joint/cmd_pos",
    "wrist_2_joint": "/arm/joint/wrist_2_joint/cmd_pos",
    "wrist_3_joint": "/arm/joint/wrist_3_joint/cmd_pos",
}
ARM_LIMITS_BY_JOINT = {
    "shoulder_pan_joint": (-6.2832, 6.2832),
    "shoulder_lift_joint": (-6.2832, 6.2832),
    "elbow_joint": (-3.1416, 3.1416),
    "wrist_1_joint": (-6.2832, 6.2832),
    "wrist_2_joint": (-6.2832, 6.2832),
    "wrist_3_joint": (-6.2832, 6.2832),
}
ARM_JOINT_ORDER = tuple(ARM_TOPIC_BY_JOINT.keys())


@dataclass(frozen=True)
class ArmJointConfig:
    """Control metadata for one arm joint."""

    name: str
    topic: str
    lower: float | None
    upper: float | None


# One shared Gazebo node keeps all transport traffic in this file.
node = Node()
last_contact_print_time = 0.0
subscriptions_started = False

# The logic layer can read this dictionary without needing Gazebo message types.
state = {
    "imu": {
        "orientation_x": None,
        "orientation_y": None,
        "orientation_z": None,
        "orientation_w": None,
        "angular_velocity_x": None,
        "angular_velocity_y": None,
        "angular_velocity_z": None,
        "linear_acceleration_x": None,
        "linear_acceleration_y": None,
        "linear_acceleration_z": None,
    },
    "lidar": {
        "first_range": None,
        "range_count": 0,
    },
    "camera": {
        "width": None,
        "height": None,
        "pixel_format_type": None,
    },
    "contact": {
        "chassis_touching": False,
    },
    "pose": {
        "current_x": None,
        "current_y": None,
    },
    "arm": {
    "shoulder_pan_joint": None,
    "shoulder_lift_joint": None,
    "elbow_joint": None,
    "wrist_1_joint": None,
    "wrist_2_joint": None,
    "wrist_3_joint": None,
    },
    "bucket_contact": {
        "touching": False,
        "x": None,
        "y": None,
    },
    "last_update_time": 0.0,
}
# Keep sensor state flat and primitive so logic / tests can read this easily.


# Publishers are created once and reused for each command.
drive_publisher = node.advertise(CMD_VEL_TOPIC, Twist)
arm_publishers = {
    joint_name: node.advertise(topic_name, Double)
    for joint_name, topic_name in ARM_TOPIC_BY_JOINT.items()
}

def imu_cb(message: IMU) -> None:
    """Store the latest IMU values."""
    state["imu"]["orientation_x"] = message.orientation.x
    state["imu"]["orientation_y"] = message.orientation.y
    state["imu"]["orientation_z"] = message.orientation.z
    state["imu"]["orientation_w"] = message.orientation.w
    state["imu"]["angular_velocity_x"] = message.angular_velocity.x
    state["imu"]["angular_velocity_y"] = message.angular_velocity.y
    state["imu"]["angular_velocity_z"] = message.angular_velocity.z
    state["imu"]["linear_acceleration_x"] = message.linear_acceleration.x
    state["imu"]["linear_acceleration_y"] = message.linear_acceleration.y
    state["imu"]["linear_acceleration_z"] = message.linear_acceleration.z
    state["last_update_time"] = time.time()


def lidar_cb(message: LaserScan) -> None:
    """Store a simple lidar summary."""
    state["lidar"]["range_count"] = len(message.ranges)
    # The first range is enough for early testing. Full scan processing can be
    # added later in the logic layer or expanded here if needed.
    if message.ranges:
        state["lidar"]["first_range"] = message.ranges[0]
    else:
        state["lidar"]["first_range"] = None
    state["last_update_time"] = time.time()

def camera_cb(message: Image) -> None:
    """Store camera metadata."""
    state["camera"]["width"] = message.width
    state["camera"]["height"] = message.height
    state["camera"]["pixel_format_type"] = message.pixel_format_type
    state["last_update_time"] = time.time()


def chassis_contact_cb(message: Contacts) -> None:
    """Store chassis contact state."""
    global last_contact_print_time

    state["contact"]["chassis_touching"] = len(message.contact) > 0
    state["last_update_time"] = time.time()

    # Limit repeated prints so contact spam does not flood the terminal.
    if state["contact"]["chassis_touching"]:
        now = time.time()
        if now - last_contact_print_time >= 1.0:
            print("[CONTACT] Chassis touching something", flush=True)
            last_contact_print_time = now


def pose_cb(message: Pose_V) -> None:
    """Store digger coordinates."""
    for pose in message.pose:
        if pose.name == "digger":
            state["pose"]["current_x"] = pose.position.x
            state["pose"]["current_y"] = pose.position.y
            state["last_update_time"] = time.time()
            return
        

def arm_state_cb(message: Model) -> None:
    """Store the latest arm joint positions."""
    for joint in message.joint:
        if joint.name in state["arm"]:
            state["arm"][joint.name] = joint.axis1.position
    state["last_update_time"] = time.time()


def bucket_contact_cb(message: Contacts) -> None:
    """Store first bucket contact point."""
    state["bucket_contact"]["touching"] = False
    state["bucket_contact"]["x"] = None
    state["bucket_contact"]["y"] = None

    for contact in message.contact:
        for pos in contact.position:
            state["bucket_contact"]["touching"] = True
            state["bucket_contact"]["x"] = pos.x
            state["bucket_contact"]["y"] = pos.y
            state["last_update_time"] = time.time()
            return
    
# --------------------------------------------------------------------------

def start_subscribers() -> None:
    """Subscribe to the Gazebo topics used by the project."""
    global subscriptions_started

    # Prevent duplicate subscriptions if another script calls this twice.
    if subscriptions_started:
        return

    node.subscribe(IMU, IMU_TOPIC, imu_cb)
    node.subscribe(LaserScan, LIDAR_TOPIC, lidar_cb)
    node.subscribe(Image, CAMERA_TOPIC, camera_cb)
    node.subscribe(Contacts, CHASSIS_CONTACT_TOPIC, chassis_contact_cb)
    node.subscribe(Pose_V, POSE_TOPIC, pose_cb)
    node.subscribe(Model, ARM_STATE_TOPIC, arm_state_cb)
    node.subscribe(Contacts, BUCKET_CONTACT_TOPIC,  bucket_contact_cb)
    subscriptions_started = True


def publish_drive_command(linear_x: float = 0.0, angular_z: float = 0.0) -> None:
    """Publish one drive command to Gazebo."""
    message = Twist()
    message.linear.x = linear_x
    message.angular.z = angular_z
    drive_publisher.publish(message)


def stop_drive() -> None:
    """Publish a zero drive command."""
    publish_drive_command()


def publish_arm_command(
    shoulder_pan_joint: float | None = None,
    shoulder_lift_joint: float | None = None,
    elbow_joint: float | None = None,
    wrist_1_joint: float | None = None,
    wrist_2_joint: float | None = None,
    wrist_3_joint: float | None = None,
) -> None:
    """Publish arm targets for the joints that have a value."""
    # None means "leave this joint alone" so callers can update one joint
    # without having to resend every other arm target.
    target_by_joint = {
        "shoulder_pan_joint": shoulder_pan_joint,
        "shoulder_lift_joint": shoulder_lift_joint,
        "elbow_joint": elbow_joint,
        "wrist_1_joint": wrist_1_joint,
        "wrist_2_joint": wrist_2_joint,
        "wrist_3_joint": wrist_3_joint,
    }

    for joint_name, target in target_by_joint.items():
        if target is None:
            continue

        message = Double()
        message.data = target
        arm_publishers[joint_name].publish(message)


def publish_arm_targets(target_by_joint: dict[str, float | None]) -> None:
    """Publish arm targets from a joint-name keyed dictionary."""
    unknown_joint_names = sorted(
        joint_name
        for joint_name in target_by_joint
        if joint_name not in ARM_TOPIC_BY_JOINT
    )
    if unknown_joint_names:
        raise KeyError(
            "Unknown arm joint names in target_by_joint: "
            + ", ".join(unknown_joint_names)
        )

    publish_arm_command(
        shoulder_pan_joint=target_by_joint.get("shoulder_pan_joint"),
        shoulder_lift_joint=target_by_joint.get("shoulder_lift_joint"),
        elbow_joint=target_by_joint.get("elbow_joint"),
        wrist_1_joint=target_by_joint.get("wrist_1_joint"),
        wrist_2_joint=target_by_joint.get("wrist_2_joint"),
        wrist_3_joint=target_by_joint.get("wrist_3_joint"),
    )


def get_arm_pose_names() -> tuple[str, ...]:
    """Return canonical named arm poses supported by the interface."""
    return arm_helper.list_arm_pose_names()


def get_arm_pose_targets(pose_name: str) -> dict[str, float]:
    """Resolve a pose string into validated joint targets."""
    target_by_joint = arm_helper.get_arm_pose_targets(pose_name)
    validate_arm_targets(target_by_joint)
    return target_by_joint


def publish_arm_pose(pose_name: str) -> None:
    """Publish one named arm pose."""
    publish_arm_targets(get_arm_pose_targets(pose_name))


def get_arm_joint_order() -> tuple[str, ...]:
    """Return the arm joint order used by interface commands."""
    return ARM_JOINT_ORDER


def get_arm_joint_configs() -> dict[str, ArmJointConfig]:
    """Return arm control metadata used by the interface layer."""
    return {
        joint_name: ArmJointConfig(
            name=joint_name,
            topic=ARM_TOPIC_BY_JOINT[joint_name],
            lower=ARM_LIMITS_BY_JOINT[joint_name][0],
            upper=ARM_LIMITS_BY_JOINT[joint_name][1],
        )
        for joint_name in ARM_JOINT_ORDER
    }


def validate_arm_targets(target_by_joint: dict[str, float]) -> None:
    """Validate arm targets against known joints and configured limits."""
    missing_joint_names = sorted(
        joint_name
        for joint_name in ARM_JOINT_ORDER
        if joint_name not in target_by_joint
    )
    if missing_joint_names:
        raise ValueError(
            "Missing arm joint targets for: " + ", ".join(missing_joint_names)
        )

    unknown_joint_names = sorted(
        joint_name
        for joint_name in target_by_joint
        if joint_name not in ARM_TOPIC_BY_JOINT
    )
    if unknown_joint_names:
        raise KeyError("Unknown arm joint names: " + ", ".join(unknown_joint_names))

    for joint_name in ARM_JOINT_ORDER:
        target_value = target_by_joint[joint_name]
        lower_limit, upper_limit = ARM_LIMITS_BY_JOINT[joint_name]

        if lower_limit is not None and target_value < lower_limit:
            raise ValueError(
                f"{joint_name}={target_value:.4f} is below the lower limit "
                f"{lower_limit:.4f}"
            )
        if upper_limit is not None and target_value > upper_limit:
            raise ValueError(
                f"{joint_name}={target_value:.4f} is above the upper limit "
                f"{upper_limit:.4f}"
            )


def despawn(model_name: str) -> None:
    """Despawn a model, used for terrain refreshing."""

    subprocess.run(
        [
            "gz",
            "service",
            "-s",
            f"/world/starting_environment/remove",
            "--reqtype",
            "gz.msgs.Entity",
            "--reptype",
            "gz.msgs.Boolean",
            "--timeout",
            "3000",
            "--req",
            f'name: "{model_name}" type: MODEL',
        ],
        check=True,
    )


def spawn(model_name: str, sdf_filename: str = "terrain.sdf",) -> None:
    """Spawn a model, used for terrain refreshing."""

    subprocess.run(
        [
            "gz",
            "service",
            "-s",
            "/world/starting_environment/create",
            "--reqtype",
            "gz.msgs.EntityFactory",
            "--reptype",
            "gz.msgs.Boolean",
            "--timeout",
            "3000",
            "--req",
            f'sdf_filename: "{sdf_filename}" name: "{model_name}"',
        ]
    )


def get_state() -> dict:
    """Return the latest stored sensor values."""
    # Return copies so outside code does not accidentally overwrite interface
    # state directly.
    return {
        "imu": dict(state["imu"]),
        "lidar": dict(state["lidar"]),
        "camera": dict(state["camera"]),
        "contact": dict(state["contact"]),
        "pose": dict(state["pose"]),
        "arm": dict(state["arm"]),
        "bucket_contact": dict(state["bucket_contact"]),
        "last_update_time": state["last_update_time"],
    }


def print_state_summary() -> None:
    """Print a short summary of the latest stored values."""
    print(
        "[STATE] "
        f"imu_x={state['imu']['angular_velocity_x']} "
        f"lidar_first={state['lidar']['first_range']} "
        f"cam={state['camera']['width']}x{state['camera']['height']} "
        f"chassis_contact={state['contact']['chassis_touching']} "
        f"pose={state['pose']['current_x']},{state['pose']['current_y']} "
        f"shoulder={state['arm']['shoulder_lift_joint']} "
        f"elbow={state['arm']['elbow_joint']} "
        f"wrist={state['arm']['wrist_1_joint']}"
        f"bucket_contact={state['bucket_contact']['touching']},{state['bucket_contact']['x']},{state['bucket_contact']['y']} ",
        flush=True,
    )


def main() -> None:
    """Small manual test entry point for the interface layer."""
    start_subscribers()
    print("Listening to Gazebo topics...")

    while True:
        time.sleep(1.0)
        print_state_summary()


if __name__ == "__main__":
    main()