#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import sys
import termios
import tty

# Hướng dẫn điều khiển
msg = """
-----------------------------------------
Điều khiển cánh tay qua Action Client:
-----------------------------------------
Cánh tay 1 (Xoay):  q : Tăng  |  a : Giảm
Cánh tay 2 (Trượt): w : Tăng  |  s : Giảm

Phím SPACE để reset về 0
CTRL-C để thoát
-----------------------------------------
"""

class TeleopArmAction(Node):
    def __init__(self):
        super().__init__('teleop_arm_action')
        self.client = ActionClient(self, FollowJointTrajectory, '/arm_controller/follow_joint_trajectory')
        
        # Vị trí hiện tại mong muốn
        self.arm1_pos = 0.0
        self.arm2_pos = 0.0
        
        # Bước nhảy mỗi lần nhấn phím
        self.step_arm1 = 0.1  # rad
        self.step_arm2 = 0.02 # m

    def send_goal(self):
        if not self.client.wait_for_server(timeout_sec=1.0):
            self.get_logger().error('Action Server không phản hồi!')
            return

        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = ['arm1_joint', 'arm2_point']

        point = JointTrajectoryPoint()
        point.positions = [float(self.arm1_pos), float(self.arm2_pos)]
        # Cho robot 0.5 giây để thực hiện mỗi bước nhảy phím
        point.time_from_start = Duration(sec=0, nanosec=500000000) 

        goal_msg.trajectory.points.append(point)
        self.client.send_goal_async(goal_msg)
        self.get_logger().info(f'Gửi lệnh: Arm1={self.arm1_pos:.2f}, Arm2={self.arm2_pos:.2f}')

def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def main():
    settings = termios.tcgetattr(sys.stdin)
    rclpy.init()
    node = TeleopArmAction()

    print(msg)

    try:
        while True:
            key = get_key(settings)
            if key == 'q':
                node.arm1_pos += node.step_arm1
            elif key == 'a':
                node.arm1_pos -= node.step_arm1
            elif key == 'w':
                node.arm2_pos += node.step_arm2
            elif key == 's':
                node.arm2_pos -= node.step_arm2
            elif key == ' ':
                node.arm1_pos = 0.0
                node.arm2_pos = 0.0
            elif key == '\x03': # CTRL-C
                break
            else:
                continue
            
            # Giới hạn góc (theo URDF của bạn)
            node.arm1_pos = max(0.0, min(1.56, node.arm1_pos))
            node.arm2_pos = max(0.0, min(0.38, node.arm2_pos))
            
            node.send_goal()

    except Exception as e:
        print(e)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
