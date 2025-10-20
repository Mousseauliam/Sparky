from PCADriver import PCADriver
from Servo import Servo
from time import sleep

# Test connexion I2C
try:
    driver1 = PCADriver(address=0x40, freq=50)
    driver2 = PCADriver(address=0x41, freq=50)
except Exception as e:
    print(f"❌ Erreur d'initialisation: {e}")
    exit(1)

servo0 = Servo(driver1, channel=0)
servo1 = Servo(driver1, channel=1)
servo2 = Servo(driver1, channel=2)
servo4 = Servo(driver1, channel=4)
servo5 = Servo(driver1, channel=5)
servo6 = Servo(driver1, channel=6)
servo8 = Servo(driver1, channel=8)
servo9 = Servo(driver1, channel=9)
servo10 = Servo(driver1, channel=10)
servo12 = Servo(driver2, channel=0)
servo13 = Servo(driver2, channel=1)
servo14 = Servo(driver2, channel=2)
servo16 = Servo(driver2, channel=4)
servo17 = Servo(driver2, channel=5)
servo18 = Servo(driver2, channel=6)
servo20 = Servo(driver2, channel=8)
servo21 = Servo(driver2, channel=9)
servo22 = Servo(driver2, channel=10)

servos = [servo0, servo1, servo2, servo4, servo5, servo6, servo8, servo9, servo10, 
          servo12, servo13, servo14, servo16, servo17, servo18, servo20, servo21, servo22]

for servo in servos:
    servo.neutral()
        
sleep(3)

for servo in servos:
    if servo.channel_info()[0] % 4 == 1:
        servo.set_angle(70)
    
servos[10].set_angle(110)

driver1.close()
driver2.close()
sleep(0.5)
print("Ressources libérées")
