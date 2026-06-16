import gz.msgs.pose_pb2 as pose_pb2
import gz.msgs.quaternion_pb2 as quaternion_pb2
import gz.msgs.boolean_pb2 as boolean_pb2
import math

def make_quat(roll, pitch, yaw):
    q = quaternion_pb2.Quaternion()
    cy, sy = math.cos(yaw/2),   math.sin(yaw/2)
    cp, sp = math.cos(pitch/2), math.sin(pitch/2)
    cr, sr = math.cos(roll/2),  math.sin(roll/2)
    q.w = cr*cp*cy + sr*sp*sy
    q.x = sr*cp*cy - cr*sp*sy
    q.y = cr*sp*cy + sr*cp*sy
    q.z = cr*cp*sy - sr*sp*cy
    return q

def make_pose(x, y, z, roll, pitch, yaw):
    p = pose_pb2.Pose()
    p.name = "boundingbox_camera"
    p.position.x = x
    p.position.y = y
    p.position.z = z
    p.orientation.CopyFrom(make_quat(roll, pitch, yaw))
    return p

def make_request(pose, node):
    result = node.request(
        "/world/default/set_pose",
        pose,
        pose_pb2.Pose,
        boolean_pb2.Boolean,
        timeout=500
    )
    return result

N  = make_pose( 0,     -6,    3.5, 0, 0.5999,  1.5708)
NE = make_pose( 4.24,  -4.24, 3.5, 0, 0.5999,  2.2)
E  = make_pose( 8,      0,    3.5, 0, 0.5999,  3.1416)
SE = make_pose( 4.24,   4.24, 3.5, 0, 0.5999, -2.2)
S  = make_pose( 0,      6,    3.5, 0, 0.5999, -1.5708)
SW = make_pose(-4.24,   4.24, 3.5, 0, 0.5999, -0.9)
W  = make_pose(-8,      0,    3.5, 0, 0.5999,  0)
NW = make_pose(-4.24,  -4.24, 3.5, 0, 0.5999,  0.9)

cam_positions = [N, NE, E, SE, S, SW, W, NW]