#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray
from .PCADriver import PCADriver
from .Servo import Servo
from time import sleep

class SparkyHardwareNode(Node):
    def __init__(self):
        super().__init__('sparky_hardware')
        
        self.get_logger().info('🚀 Initialisation de Sparky Hardware Node...')
        
        # Test connexion I2C
        try:
            self.driver1 = PCADriver(address=0x40, freq=50)
            self.driver2 = PCADriver(address=0x41, freq=50)
            self.get_logger().info('✅ Drivers PCA9685 initialisés (0x40 et 0x41)')
        except Exception as e:
            self.get_logger().error(f"❌ Erreur d'initialisation: {e}")
            raise
        
        # Créer les 18 servos
        self.servo0 = Servo(self.driver1, channel=0)
        self.servo1 = Servo(self.driver1, channel=1)
        self.servo2 = Servo(self.driver1, channel=2)
        self.servo4 = Servo(self.driver1, channel=4)
        self.servo5 = Servo(self.driver1, channel=5)
        self.servo6 = Servo(self.driver1, channel=6)
        self.servo8 = Servo(self.driver1, channel=8)
        self.servo9 = Servo(self.driver1, channel=9)
        self.servo10 = Servo(self.driver1, channel=10)
        self.servo12 = Servo(self.driver2, channel=0)
        self.servo13 = Servo(self.driver2, channel=1)
        self.servo14 = Servo(self.driver2, channel=2)
        self.servo16 = Servo(self.driver2, channel=4)
        self.servo17 = Servo(self.driver2, channel=5)
        self.servo18 = Servo(self.driver2, channel=6)
        self.servo20 = Servo(self.driver2, channel=8)
        self.servo21 = Servo(self.driver2, channel=9)
        self.servo22 = Servo(self.driver2, channel=10)
        
        self.servos = [
            self.servo0, self.servo1, self.servo2, self.servo4, 
            self.servo5, self.servo6, self.servo8, self.servo9, self.servo10,
            self.servo12, self.servo13, self.servo14, self.servo16, 
            self.servo17, self.servo18, self.servo20, self.servo21, self.servo22
        ]
        
        self.get_logger().info(f'✅ {len(self.servos)} servos créés')
        
        # Position neutre au démarrage
        self.get_logger().info('📍 Mise en position neutre...')
        for servo in self.servos:
            servo.neutral()
        
        self.get_logger().info('⏳ Attente 3 secondes...')
        sleep(3)
        
        # Test: servos canaux 0,4,8 à 70°
        self.get_logger().info('🔧 Test: servos canaux 0,4,8 à 70°')
        for servo in self.servos:
            if servo.channel_info()[0] % 4 == 0:
                servo.set_angle(100)
        
        # Subscriber pour recevoir des commandes d'angles
        self.cmd_sub = self.create_subscription(
            Float64MultiArray,
            'joint_commands',
            self.joint_cmd_callback,
            10
        )
        
        # Publisher pour l'état des joints
        self.state_pub = self.create_publisher(JointState, 'joint_states', 10)
        self.create_timer(0.02, self.publish_states)  # 50Hz
        
        # État actuel des servos
        self.current_angles = [90.0] * len(self.servos)
        # Mettre à jour avec les angles du test
        for i, servo in enumerate(self.servos):
            if servo.channel_info()[0] % 4 == 0:
                self.current_angles[i] = 70.0
        
        self.get_logger().info('🤖 Sparky Hardware Node prêt!')
        self.get_logger().info('📥 En attente de commandes sur /joint_commands')
    
    def joint_cmd_callback(self, msg):
        """Reçoit un tableau d'angles pour chaque servo"""
        for i, angle in enumerate(msg.data):
            if i < len(self.servos):
                self.servos[i].set_angle(angle)
                self.current_angles[i] = angle
        
        self.get_logger().info(f'Angles reçus: {list(msg.data)[:6]}...')
    
    def publish_states(self):
        """Publie l'état actuel des joints à 50Hz"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = [f'joint_{i}' for i in range(len(self.servos))]
        msg.position = self.current_angles
        self.state_pub.publish(msg)
    
    def destroy_node(self):
        """Nettoyage à la fermeture"""
        self.get_logger().info('🛑 Fermeture de Sparky Hardware Node...')
        self.driver1.close()
        self.driver2.close()
        sleep(0.5)
        self.get_logger().info("✅ Ressources libérées")
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = SparkyHardwareNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('⚠️ Interruption clavier')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
