from PCADriver import PCADriver
from time import sleep

print("=== Diagnostic PCA9685 ===\n")

# Test connexion I2C
try:
    driver = PCADriver(address=0x40, freq=50)
    print("✅ PCA9685 initialisé à 0x40")
except Exception as e:
    print(f"❌ Erreur d'initialisation: {e}")
    exit(1)

try:
    # Test 1: Signal ON complet (100% duty)
    print("\n--- Test 1: Signal ON complet (canal 0) ---")
    driver.set_pwm(0, 0, 4095)  # Toujours ON
    print("Signal ON permanent - vérifier avec multimètre ou LED")
    sleep(10)
    
    # Test 2: Signal OFF complet
    print("\n--- Test 2: Signal OFF complet ---")
    driver.set_pwm(0, 0, 0)  # Toujours OFF
    print("Signal OFF - le servo ne devrait pas être alimenté")
    sleep(3)
    
    # Test 3: PWM 50% (duty cycle moyen)
    print("\n--- Test 3: PWM 50% ---")
    driver.set_pwm(0, 0, 2048)
    print("Signal 50% - le servo devrait vibrer légèrement")
    sleep(3)
    
    # Test 4: Positions servo typiques
    print("\n--- Test 4: Positions servo (valeurs brutes) ---")
    
    # 0° - environ 0.5ms (2.5% de 20ms)
    print("Position 0° (pulse ~0.5ms)")
    driver.set_pwm(0, 0, 102)  # 2.5% de 4096
    sleep(2)
    
    # 90° - environ 1.5ms (7.5% de 20ms)
    print("Position 90° (pulse ~1.5ms)")
    driver.set_pwm(0, 0, 307)  # 7.5% de 4096
    sleep(2)
    
    # 180° - environ 2.5ms (12.5% de 20ms)
    print("Position 180° (pulse ~2.5ms)")
    driver.set_pwm(0, 0, 512)  # 12.5% de 4096
    sleep(2)
    
    print("\n--- Test 5: Balayage lent ---")
    for i in range(102, 513, 20):
        driver.set_pwm(0, 0, i)
        print(f"Valeur PWM: {i}/4095", end='\r')
        sleep(0.3)
    
    print("\n\n✅ Tests terminés")
    
except KeyboardInterrupt:
    print("\n\n⚠️ Test interrompu")
finally:
    driver.set_pwm(0, 0, 0)  # Éteindre le signal
    driver.close()
    print("Ressources libérées")
