#!/usr/bin/env python3
"""
Serveur web simple pour contrôler Sparky
Sert les fichiers statiques (HTML, CSS, JS) et gère l'API REST
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import os

class SparkyWebServer(Node):
    def __init__(self):
        super().__init__('sparky_web_server')
        
        # Publisher pour les commandes
        self.cmd_pub = self.create_publisher(Float64MultiArray, 'joint_commands', 10)
        
        # Subscriber pour l'état
        self.state_sub = self.create_subscription(
            JointState,
            'joint_states',
            self.state_callback,
            10
        )
        
        self.current_angles = [90.0] * 18
        self.get_logger().info('🌐 Serveur web Sparky initialisé')
    
    def state_callback(self, msg):
        """Reçoit l'état des joints"""
        self.current_angles = list(msg.position)
    
    def send_command(self, servo_id, angle, speed=100.0):
        """
        Envoie une commande pour un servo spécifique avec vitesse
        
        ✅ MODIFIÉ: N'envoie QUE l'angle du servo sélectionné pour éviter
        de saturer le bus I2C en bougeant tous les servos en même temps
        """
        if not (0 <= servo_id < 18):
            return False
        
        if not (0 <= angle <= 180):
            return False
        
        # ✅ Créer un tableau avec SEULEMENT le servo à bouger
        # Les autres gardent leur position actuelle (pas de mouvement)
        angles = self.current_angles.copy()
        angles[servo_id] = float(angle)
        
        # Publier la commande avec 19 éléments (18 angles + vitesse)
        msg = Float64MultiArray()
        msg.data = angles + [float(speed)]
        self.cmd_pub.publish(msg)
        
        self.get_logger().info(f'📤 Servo {servo_id} → {angle}° @ {speed}°/sec')
        return True

# Instance globale
web_node = None

class SparkyHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Désactive les logs HTTP"""
        pass
    
    def do_GET(self):
        """Sert les fichiers statiques"""
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        
        if self.path == '/':
            file_path = os.path.join(static_dir, 'index.html')
            content_type = 'text/html'
        elif self.path == '/style.css':
            file_path = os.path.join(static_dir, 'style.css')
            content_type = 'text/css'
        elif self.path == '/script.js':
            file_path = os.path.join(static_dir, 'script.js')
            content_type = 'application/javascript'
        elif self.path == '/api/state':
            # API pour récupérer l'état
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            state = {'angles': web_node.current_angles}
            self.wfile.write(json.dumps(state).encode())
            return
        else:
            self.send_response(404)
            self.end_headers()
            return
        
        # Servir le fichier
        try:
            with open(file_path, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Reçoit les commandes"""
        if self.path == '/api/command':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            servo_id = data.get('servo')
            angle = data.get('angle')
            speed = data.get('speed', 100.0)
            
            success = web_node.send_command(servo_id, angle, speed)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'ok' if success else 'error',
                'servo': servo_id,
                'angle': angle,
                'speed': speed
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def main():
    global web_node
    
    # Créer le dossier static s'il n'existe pas
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    rclpy.init()
    web_node = SparkyWebServer()
    
    # Lancer le serveur HTTP
    server = HTTPServer(('0.0.0.0', 8080), SparkyHTTPHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    web_node.get_logger().info('🌐 Serveur web démarré sur http://sparky.local:8080')
    web_node.get_logger().info('📱 Ouvre cette adresse dans ton navigateur')
    
    try:
        rclpy.spin(web_node)
    except KeyboardInterrupt:
        web_node.get_logger().info('⚠️ Arrêt du serveur')
    finally:
        server.shutdown()
        web_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
