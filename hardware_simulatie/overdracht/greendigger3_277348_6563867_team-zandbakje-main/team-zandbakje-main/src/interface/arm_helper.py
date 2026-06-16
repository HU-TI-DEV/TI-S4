"""Named arm poses and string helpers for arm control scripts.

    Author: Replitard
"""

ARM_POSE_BY_NAME = {
    "neutral": {
        "shoulder_pan_joint": 0.0,
        "shoulder_lift_joint": 0.0,
        "elbow_joint": 0.0,
        "wrist_1_joint": 0.0,
        "wrist_2_joint": 0.0,
        "wrist_3_joint": 0.0,
    },
    "dig": {
        "shoulder_pan_joint": 0.0,
        "shoulder_lift_joint": -0.6,
        "elbow_joint": 1.2,
        "wrist_1_joint": -0.6,
        "wrist_2_joint": 0.0,
        "wrist_3_joint": 0.0,
    },
    "arm_up": {
        "shoulder_pan_joint": 0.0,
        "shoulder_lift_joint": -1.5,
        "elbow_joint": 0.15,
        "wrist_1_joint": 1.4,
        "wrist_2_joint": 0.0,
        "wrist_3_joint": 0.0,
    },
    "arm_down": {
        "shoulder_pan_joint": 0.0,
        "shoulder_lift_joint": 0.3,
        "elbow_joint": 0.8,
        "wrist_1_joint": 0.5,
        "wrist_2_joint": 0.0,
        "wrist_3_joint": 0.0,
    },
    "rotate_left": {
        "shoulder_pan_joint": 1.2,
        "shoulder_lift_joint": -0.8,
        "elbow_joint": 1.3,
        "wrist_1_joint": -0.5,
        "wrist_2_joint": 0.4,
        "wrist_3_joint": 0.0,
    },
    "right_sweep": {
        "shoulder_pan_joint": -1.2,
        "shoulder_lift_joint": -0.8,
        "elbow_joint": 1.3,
        "wrist_1_joint": -0.5,
        "wrist_2_joint": -0.4,
        "wrist_3_joint": 0.0,
    },
    "arm_up_high": {
        "shoulder_pan_joint": 0.0,
        "shoulder_lift_joint": -1.55,
        "elbow_joint": 0.15,
        "wrist_1_joint": 1.4,
        "wrist_2_joint": 0.0,
        "wrist_3_joint": 0.0,
    },
    "arm_out_of_the_way": {
        "shoulder_pan_joint": 0.0,
        "shoulder_lift_joint": -2.4,
        "elbow_joint": 1.45,
        "wrist_1_joint": -0.3,
        "wrist_2_joint": 0.0,
        "wrist_3_joint": 0.0,
    },
}

ARM_POSE_ALIASES = {
    "up": "arm_up",
    "arm up": "arm_up",
    "down": "arm_down",
    "arm down": "arm_down",
    "rotate left": "rotate_left",
    "right sweep": "right_sweep",
    "arm up high": "arm_up_high",
    "arm out of the way": "arm_out_of_the_way",
}

# Makes sure it's not case sensitive, or white space sentisive.
def _normalize_pose_name(pose_name: str) -> str:
    return "_".join(pose_name.strip().lower().replace("-", " ").split())


def list_arm_pose_names() -> tuple[str, ...]:
    """Return canonical named poses."""
    return tuple(sorted(ARM_POSE_BY_NAME.keys()))


def resolve_arm_pose_name(pose_name: str) -> str:
    """Resolve a user pose string into a canonical pose name."""
    normalized_name = _normalize_pose_name(pose_name)
    if normalized_name in ARM_POSE_BY_NAME:
        return normalized_name

    alias_canonical_by_name = {
        _normalize_pose_name(alias_name): canonical_name
        for alias_name, canonical_name in ARM_POSE_ALIASES.items()
    }
    if normalized_name in alias_canonical_by_name:
        return alias_canonical_by_name[normalized_name]

    known_pose_names = ", ".join(list_arm_pose_names())
    raise KeyError(
        f"Unknown arm pose '{pose_name}'. "
        f"Use one of: {known_pose_names}."
    )


def get_arm_pose_targets(pose_name: str) -> dict[str, float]:
    """Return a copy of the joint targets for a named arm pose."""
    canonical_name = resolve_arm_pose_name(pose_name)
    return dict(ARM_POSE_BY_NAME[canonical_name])
