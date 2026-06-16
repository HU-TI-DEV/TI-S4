To implement pathfinding in ROS 2, you aren't just writing one single script; you are configuring a pipeline.

In ROS 2, the standard way to do this is through the Nav2 (Navigation 2) Stack. It uses a behavior tree logic to coordinate between a "Global Planner" (long-distance path) and a "Local Planner" (short-distance obstacle avoidance).

Here is how you implement a custom pathfinding setup for your own robot.

1. The Core Implementation Logic
To get pathfinding working, your robot must provide three things to the Nav2 stack:

Odometry (/odom): Where the robot thinks it is based on wheel turns.

LIDAR/Sensor Data (/scan): Where the obstacles are.

Transforms (tf2): The mathematical relationship between the robot's base, the laser, and the map.

2. Configuration (The nav2_params.yaml)
You don't "hard code" the A* or Dijkstra algorithm; you configure the Controller and Planner servers in a YAML file. This is where the implementation lives.

YAML
planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner" # Implementation of Dijkstra/A*
      tolerance: 0.5
      use_astar: false # Set to true for A*

controller_server:
  ros__parameters:
    controller_plugins: ["FollowPath"]
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner" # Local pathfinding & obstacle avoidance
      max_vel_x: 0.26
      min_vel_x: 0.0
      max_rot_vel: 1.0
3. Implementation via Python Script (API)
If you want to trigger pathfinding programmatically (e.g., "Go to the kitchen") rather than clicking buttons in RViz, you use the BasicNavigator Python API.

Create a file named go_to_goal.py:

```Python
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped
from rclpy.duration import Duration

def main():
    rclpy.init()
    nav = BasicNavigator()

    # 1. Set the robot's starting position (Initial Pose)
    initial_pose = PoseStamped()
    initial_pose.header.frame_id = 'map'
    initial_pose.header.stamp = nav.get_clock().now().to_msg()
    initial_pose.pose.position.x = 0.0
    initial_pose.pose.position.y = 0.0
    initial_pose.pose.orientation.z = 0.0
    initial_pose.pose.orientation.w = 1.0
    nav.setInitialPose(initial_pose)

    # 2. Wait for Nav2 to be fully active
    nav.waitUntilNav2Active()

    # 3. Define a Goal Pose (Where you want to go)
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    goal_pose.header.stamp = nav.get_clock().now().to_msg()
    goal_pose.pose.position.x = 2.5  # 2.5 meters forward
    goal_pose.pose.position.y = 1.0  # 1.0 meter left
    goal_pose.pose.orientation.w = 1.0

    # 4. Execute Pathfinding
    nav.goToPose(goal_pose)

    while not nav.isTaskComplete():
        feedback = nav.getFeedback()
        if feedback:
            print(f'Estimated time of arrival: {Duration.from_msg(feedback.estimated_time_remaining).nanoseconds / 1e9:.2f} s')

    print('Goal reached!')
    rclpy.shutdown()

if __name__ == '__main__':
    main()

```
4. Launching the Implementation
To make this work in Gazebo, you need a Launch File that brings up your robot description (URDF), the Gazebo world, and the Nav2 stack simultaneously.

The Workflow:

URDF: Defines your robot's physical links (wheels, chassis, sensors).

Gazebo Plugin: Inside your URDF, you must include the libgazebo_ros_diff_drive.so (for movement) and libgazebo_ros_ray_sensor.so (for LIDAR) so ROS 2 can talk to the simulation.

Map Server: Loads a .yaml map you created earlier.

AMCL: Handles localization (comparing LIDAR hits to the map).

How to test your code:
Start your Gazebo simulation.

Run your Nav2 stack with your custom nav2_params.yaml.

Run the Python script above:

Bash
python3 go_to_goal.py