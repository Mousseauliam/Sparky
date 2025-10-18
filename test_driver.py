from time import sleep
from PCADriver import PCADriver
from Servo import Servo

# Initialisation de la première carte PCA9685 (0x40)
driver = PCADriver(address=0x40, freq=50)

try:
    print("Test PWM direct sur canal 0...")
    # Position neutre (90°)
    driver.set_pwm_duty(0, 7.5)  # ~1.5ms
    print("Position neutre (90°) - pause 2s")
    sleep(2)
    
    # Position min (0°)
    driver.set_pwm_duty(0, 2.5)  # ~0.5ms
    print("Position min (0°) - pause 2s")
    sleep(2)
    
    # Position max (180°)
    driver.set_pwm_duty(0, 12.5)  # ~2.5ms
    print("Position max (180°) - pause 2s")
    sleep(2)
    
finally:
    driver.close()
