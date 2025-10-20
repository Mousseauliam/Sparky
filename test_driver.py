from PCADriver import PCADriver
from Servo import Servo
from time import sleep

print("=== Test Servo Canal 13 ===\n")

# Test connexion I2C
try:
    driver = PCADriver(address=0x40, freq=50)
    servo13 = Servo(driver, channel=13, min_us=500, max_us=2500, freq=50)
    print("✅ PCA9685 initialisé à 0x40")
    print("✅ Servo sur canal 13 configuré")
except Exception as e:
    print(f"❌ Erreur d'initialisation: {e}")
    exit(1)

try:
    print("\n--- Balayage 0° → 180° sur canal 13 ---")
    
    # Balayage lent de 0° à 180°
    for angle in range(0, 181, 10):
        servo13.set_angle(angle)
        print(f"Angle: {angle}°")
        sleep(0.5)
    
    print("\n--- Retour 180° → 0° ---")
    
    # Retour de 180° à 0°
    for angle in range(180, -1, -10):
        servo13.set_angle(angle)
        print(f"Angle: {angle}°")
        sleep(0.5)
    
    print("\n✅ Test terminé")
    
except KeyboardInterrupt:
    print("\n\n⚠️ Test interrompu")
finally:
    servo13.set_angle(90)  # Position neutre
    sleep(0.5)
    driver.set_pwm(13, 0, 0)  # Éteindre le signal
    driver.close()
    print("Ressources libérées")
