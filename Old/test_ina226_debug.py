"""
Script de diagnostic pour INA226
Teste tous les registres pour trouver d'où vient le problème
"""
import smbus2
import time

class INA226Debug:
    def __init__(self, address=0x45, bus_number=1):
        self.address = address
        self.bus = smbus2.SMBus(bus_number)
        
    def read_register(self, reg):
        """Lit un registre 16 bits"""
        try:
            data = self.bus.read_i2c_block_data(self.address, reg, 2)
            value = (data[0] << 8) | data[1]
            return value
        except Exception as e:
            return f"Erreur: {e}"
    
    def write_register(self, reg, value):
        """Écrit dans un registre 16 bits"""
        data = [(value >> 8) & 0xFF, value & 0xFF]
        self.bus.write_i2c_block_data(self.address, reg, data)
    
    def test_all(self):
        print(f"🔍 Test INA226 à l'adresse {hex(self.address)}")
        print("=" * 60)
        
        # Test 1: Vérifier l'ID
        print("\n1️⃣  Vérification ID:")
        manufacturer_id = self.read_register(0xFE)
        die_id = self.read_register(0xFF)
        print(f"   Manufacturer ID: {hex(manufacturer_id) if isinstance(manufacturer_id, int) else manufacturer_id}")
        print(f"   Die ID:          {hex(die_id) if isinstance(die_id, int) else die_id}")
        
        if manufacturer_id == 0x5449 and die_id == 0x2260:
            print("   ✅ INA226 détecté correctement!")
        else:
            print("   ⚠️  IDs incorrects - vérifier l'adresse ou les connexions")
        
        # Test 2: Lire la configuration
        print("\n2️⃣  Configuration actuelle:")
        config = self.read_register(0x00)
        print(f"   Config: {hex(config) if isinstance(config, int) else config}")
        
        # Test 3: Reset et reconfiguration
        print("\n3️⃣  Reset et configuration:")
        self.write_register(0x00, 0x8000)  # Reset
        time.sleep(0.1)
        
        # Configuration: mode continu, 1.1ms conversion, avg=1
        self.write_register(0x00, 0x4127)
        time.sleep(0.1)
        
        config_after = self.read_register(0x00)
        print(f"   Config après reset: {hex(config_after) if isinstance(config_after, int) else config_after}")
        
        # Test 4: Lire tous les registres de mesure
        print("\n4️⃣  Lecture de tous les registres:")
        
        registers = {
            0x00: "Configuration",
            0x01: "Shunt Voltage",
            0x02: "Bus Voltage",
            0x03: "Power",
            0x04: "Current",
            0x05: "Calibration"
        }
        
        for reg, name in registers.items():
            raw = self.read_register(reg)
            if isinstance(raw, int):
                print(f"   {name:20s} (0x{reg:02X}): 0x{raw:04X} = {raw:5d} (bin: {bin(raw)})")
            else:
                print(f"   {name:20s} (0x{reg:02X}): {raw}")
        
        # Test 5: Conversion de la tension
        print("\n5️⃣  Conversion tension:")
        bus_voltage_raw = self.read_register(0x02)
        if isinstance(bus_voltage_raw, int):
            voltage = bus_voltage_raw * 0.00125
            print(f"   Raw value: {bus_voltage_raw}")
            print(f"   Tension calculée: {voltage:.6f} V")
            
            # Vérifier si le bit de conversion est OK
            if bus_voltage_raw == 0:
                print("   ⚠️  Valeur = 0, le capteur ne mesure peut-être pas")
                print("   💡 Vérifications:")
                print("      - VCC connecté au capteur ?")
                print("      - Charge connectée entre V+ et V- ?")
        
        # Test 6: Attendre et relire (pour voir si ça bouge)
        print("\n6️⃣  Test de variations (3 lectures):")
        for i in range(3):
            time.sleep(0.5)
            bus_raw = self.read_register(0x02)
            shunt_raw = self.read_register(0x01)
            if isinstance(bus_raw, int) and isinstance(shunt_raw, int):
                bus_v = bus_raw * 0.00125
                # Convertir shunt en signé
                if shunt_raw & 0x8000:
                    shunt_raw_signed = shunt_raw - 0x10000
                else:
                    shunt_raw_signed = shunt_raw
                shunt_mv = shunt_raw_signed * 0.0025
                
                print(f"   Lecture {i+1}: Bus={bus_v:.6f}V, Shunt={shunt_mv:.6f}mV")
        
        print("\n" + "=" * 60)
        print("✅ Test terminé")
        
    def close(self):
        self.bus.close()


if __name__ == '__main__':
    try:
        ina = INA226Debug(address=0x45)
        ina.test_all()
        ina.close()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("\n💡 Vérifications:")
        print("   1. Lance 'sudo i2cdetect -y 1'")
        print("   2. Vérifie l'adresse (actuellement 0x45)")
        print("   3. Vérifie les connexions SDA/SCL/VCC/GND")
