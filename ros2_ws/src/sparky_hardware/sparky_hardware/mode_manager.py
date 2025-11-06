#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class ModeManager(Node):
    def __init__(self):
        super().__init__('mode_manager')
        self._mode = 'MANUAL'
        self.pub = self.create_publisher(String, '/mode/state', 10)
        self.create_subscription(String, '/mode/set', self.set_mode_cb, 10)
        self.get_logger().info(f'ModeManager ready (initial mode: {self._mode})')
        self.publish_mode()

    def set_mode_cb(self, msg: String):
        mode = msg.data.upper().strip()
        if mode == self._mode:
            self.get_logger().info(f'mode already {mode}')
            return
        if mode not in ('MANUAL', 'AUTO', 'FOLLOW', 'STOP'):
            self.get_logger().warn(f'unknown mode "{mode}"')
            return
        self._mode = mode
        self.get_logger().info(f'mode -> {mode}')
        self.publish_mode()

    def publish_mode(self):
        m = String()
        m.data = self._mode
        self.pub.publish(m)

def main(args=None):
    rclpy.init(args=args)
    node = ModeManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
