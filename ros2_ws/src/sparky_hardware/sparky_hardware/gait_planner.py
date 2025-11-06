#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray

class GaitPlanner(Node):
    def __init__(self):
        super().__init__('gait_planner')
        self.declare_parameter('cycle_time', 0.6)
        self.declare_parameter('duty_cycle', 0.5)
        self.declare_parameter('step_length', 0.05)   # m
        self.declare_parameter('step_height', 0.03)   # m
        self.cycle_time = self.get_parameter('cycle_time').value
        self.duty = self.get_parameter('duty_cycle').value
        self.step_length = self.get_parameter('step_length').value
        self.step_height = self.get_parameter('step_height').value

        self.cmd_lin = 0.0
        self.cmd_ang = 0.0

        # tripod groups: 0,3,4 and 1,2,5 (phase 0 / 0.5)
        self.phase_offset = [0.0, 0.5, 0.5, 0.0, 0.0, 0.5]

        self.sub = self.create_subscription(Twist, '/cmd_mvt', self.cb_cmd, 10)
        self.pub = self.create_publisher(Float64MultiArray, '/foot_positions', 10)
        self.t0 = self.get_clock().now().nanoseconds / 1e9
        self.create_timer(1.0/50.0, self.update)

        # default stance offsets (x,y,z) par jambe (adapter selon ta géométrie)
        self.stance = [
            (0.10,  0.08, -0.12),  # leg0
            (0.10,  0.00, -0.12),
            (0.10, -0.08, -0.12),
            (-0.10,  0.08, -0.12),
            (-0.10,  0.00, -0.12),
            (-0.10, -0.08, -0.12),
        ]

    def cb_cmd(self, msg: Twist):
        self.cmd_lin = max(-1.0, min(1.0, msg.linear.x))
        self.cmd_ang = max(-1.0, min(1.0, msg.angular.z))

    def leg_phase(self, leg, t):
        return ((t / self.cycle_time) + self.phase_offset[leg]) % 1.0

    def step_profile(self, phase):
        # retourne (s_forward in [-0.5..0.5], height in [0..1])
        if phase < self.duty:
            s = phase / self.duty
            return (-0.5 + s, 0.0)
        else:
            s = (phase - self.duty) / (1.0 - self.duty)
            return (0.5 - s, math.sin(math.pi * s))
    
    def update(self):
        t = self.get_clock().now().nanoseconds / 1e9 - self.t0
        data = []
        for leg in range(6):
            phase = self.leg_phase(leg, t)
            sf, h = self.step_profile(phase)
            # apply cmd_lin/cmd_ang
            forward = self.cmd_lin * self.step_length * sf
            yaw_offset = (self.cmd_ang * 0.05) * (1 if (leg % 2 == 0) else -1)
            sx, sy, sz = self.stance[leg]
            x = sx + forward
            y = sy + yaw_offset
            z = sz - h * self.step_height
            data.extend([x, y, z])
        msg = Float64MultiArray()
        msg.data = data
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = GaitPlanner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
