#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist

class ManualTeleop(Node):
    def __init__(self):
        super().__init__('manual_teleop')
        self.mode = 'MANUAL'
        self.create_subscription(String, '/mode/state', self.mode_cb, 10)
        self.create_subscription(Twist, '/web/teleop_cmd', self.teleop_cb, 10)
        self.pub = self.create_publisher(Twist, '/cmd_mvt', 10)
        self.get_logger().info('ManualTeleop ready')

    def mode_cb(self, msg: String):
        self.mode = msg.data.upper().strip()

    def teleop_cb(self, msg: Twist):
        if self.mode != 'MANUAL':
            self.get_logger().debug('teleop ignored (not MANUAL)')
            return
        # place for safety checks (limits, watchdog...)
        self.pub.publish(msg)
        self.get_logger().info(f'forward teleop: lin={msg.linear.x:.2f} ang={msg.angular.z:.2f}')

def main(args=None):
    rclpy.init(args=args)
    node = ManualTeleop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
