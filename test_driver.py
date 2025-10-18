from time import sleep
from PCADriver import PCADriver
from Servo import Servo

# Initialisation de la première carte PCA9685 (0x40)
driver = PCADriver(address=0x40, freq=50)

try:
    # Création de quelques servos (par exemple sur les 3 premiers canaux)
    servo1 = Servo(driver, channel=0)
    servo2 = Servo(driver, channel=15)
    
    print("Test de mouvement des servos... (Ctrl+C pour arrêter)")
    while True:
        for angle in range(0, 181, 10):
            servo1.set_angle(angle)
            servo2.set_angle(180 - angle)
            sleep(0.05)
        for angle in range(180, -1, -10):
            servo1.set_angle(angle)
            servo2.set_angle(180 - angle)
            sleep(0.05)
except KeyboardInterrupt:
    print("\nArrêt du test...")
finally:
    driver.close()
    print("Ressources libérées")
