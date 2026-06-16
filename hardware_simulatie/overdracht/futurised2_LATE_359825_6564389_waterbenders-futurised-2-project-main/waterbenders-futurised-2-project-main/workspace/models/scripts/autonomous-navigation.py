from gz.transport import Node
from gz.msgs.twist_pb2 import Twist
from gz.msgs.laserscan_pb2 import LaserScan
import time

# Create a transport node
node = Node()

# Topic to publish velocity commands
cmd_vel_topic = "/model/FLIP/cmd_vel"
lidar_topic = "/lidar"

# Advertise the publisher for the Twist message
pub_twistmsg = node.advertise(cmd_vel_topic, Twist)

def lasermsg_cb(_msg: LaserScan):

    data = Twist()

    # Check whether to turn Flip the robot or not based on the distance to an object
    turn = False
    print(turn)
    for sample in _msg.ranges:
        if sample < 1:
            turn = True
            break

    if turn == True:
        data.linear.x = 0.0 # Forward/backward
        data.angular.z = 0.5 # Rotation
    else:
        data.linear.x = 0.5
        data.angular.z = 0.0

    # Publish the message
    if not pub_twistmsg.publish(data):
        print("Publishing failed")
    print(f"Published: linear.x = {data.linear.x}, angular.z = {data.angular.z}")
    # time.sleep(0.1) # Publish at 10 Hz

    # _msg.count: amount of samples taken (ranges measured) each scan
    # print("Received Lidar sensor data: [{}]".format(_msg.ranges_size()))
 
# Subscribe to a topic by registering a callback
if node.subscribe(LaserScan, lidar_topic, lasermsg_cb):
    print("Subscribing to type {} on topic [{}]".format(
        LaserScan, lidar_topic))
else:
    print("Error subscribing to topic [{}]".format(lidar_topic))

# wait for shutdown
try:
  while True:
    time.sleep(0.001)
except KeyboardInterrupt:
  pass
