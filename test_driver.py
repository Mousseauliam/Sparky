from PCADriver import PCADriver
from Servo import Servo
from time import sleep

print("=== Test Servo Canal 13 ===\n")

# Test connexion I2C
try:
    driver = PCADriver(address=0x40, freq=50)
except Exception as e:
    print(f"❌ Erreur d'initialisation: {e}")
    exit(1)

servo0 = Servo(driver, channel=0)
servo1 = Servo(driver, channel=1)
servo2 = Servo(driver, channel=2)
servo4 = Servo(driver, channel=4)
servo5 = Servo(driver, channel=5)
servo6 = Servo(driver, channel=6)
servo8 = Servo(driver, channel=8)
servo9 = Servo(driver, channel=9)
servo10 = Servo(driver, channel=10)

servos = [servo0, servo1, servo2, servo4, servo5, servo6, servo8, servo9, servo10]

for servo in servos:
    servo.neutral()
    if servo.channel_info()%4 == 0:
        print(servo.channel_info())
        
        
driver.close()
sleep(0.5)
print("Ressources libérées")
