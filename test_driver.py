from PCADriver import PCADriver
from time import sleep

print("=== Test Servo Canal 13 ===\n")

# Test connexion I2C
try:
    driver = PCADriver(address=0x40, freq=50)
    print("✅ PCA9685 initialisé à 0x40")
except Exception as e:
    print(f"❌ Erreur d'initialisation: {e}")
    exit(1)

try:
    print("\n--- Balayage 0° → 180° sur canal 13 ---")
    
    # Balayage lent de 0° à 180°
    for angle in range(0, 181, 10):
        # Calcul de la valeur PWM pour l'angle
        # 0° = 102 (2.5% = 0.5ms)
        # 180° = 512 (12.5% = 2.5ms)
        pwm_value = int(102 + (512 - 102) * (angle / 180.0))
        driver.set_pwm(13, 0, pwm_value)
        print(f"Angle: {angle}° | PWM: {pwm_value}")
        sleep(0.5)
    
    print("\n--- Retour 180° → 0° ---")
    
    # Retour de 180° à 0°
    for angle in range(180, -1, -10):
        pwm_value = int(102 + (512 - 102) * (angle / 180.0))
        driver.set_pwm(13, 0, pwm_value)
        print(f"Angle: {angle}° | PWM: {pwm_value}")
        sleep(0.5)
    
    print("\n✅ Test terminé")
    
except KeyboardInterrupt:
    print("\n\n⚠️ Test interrompu")
finally:
    driver.set_pwm(13, 0, 0)  # Éteindre le signal
    driver.close()
    print("Ressources libérées")
