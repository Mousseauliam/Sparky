#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class LegIK(Node):
    def __init__(self):
        super().__init__('leg_ik')
        # longueurs (m) -> adapter à ta mécanique
        self.L_coxa = 0.035
        self.L_femur = 0.065
        self.L_tibia = 0.095

        self.sub = self.create_subscription(Float64MultiArray, '/foot_positions', self.cb_foot, 10)
        self.pub = self.create_publisher(Float64MultiArray, '/joint_commands', 10)
        self.get_logger().info('leg_ik ready')

    def cb_foot(self, msg: Float64MultiArray):
        data = msg.data
        if len(data) != 18:
            self.get_logger().warn(f'expected 18 values, got {len(data)}')
            return
        angles = []
        for leg in range(6):
            x = data[3*leg + 0]
            y = data[3*leg + 1]
            z = data[3*leg + 2]
            a0, a1, a2 = self.solve_leg(x, y, z)
            # convertir radians -> degrés si tu veux / hardware attend degrés
            angles.extend([math.degrees(a0), math.degrees(a1), math.degrees(a2)])
        out = Float64MultiArray()
        out.data = angles
        self.pub.publish(out)

    def solve_leg(self, x, y, z):
        # coxa rotation
        a0 = math.atan2(y, x)
        # plan distance from coxa pivot to foot projection (in plane after coxa)
        r = math.hypot(x, y) - self.L_coxa
        s = -z  # assume z negative down; adjust sign per ta convention
        D = math.hypot(r, s)
        # clamp to reachable range
        a = self.L_femur
        b = self.L_tibia
        # law of cosines
        cos_q2 = (a*a + b*b - D*D) / (2*a*b)
        cos_q2 = max(-1.0, min(1.0, cos_q2))
        q2 = math.acos(cos_q2)  # knee angle (internal)
        # angle between femur and line to foot
        cos_phi = (a*a + D*D - b*b) / (2*a*D)
        cos_phi = max(-1.0, min(1.0, cos_phi))
        phi = math.acos(cos_phi)
        psi = math.atan2(s, r)
        a1 = psi + phi  # femur
        a2 = -(math.pi - q2)  # tibia (depends sign convention)
        return a0, a1, a2

def main(args=None):
    rclpy.init(args=args)
    node = LegIK()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
