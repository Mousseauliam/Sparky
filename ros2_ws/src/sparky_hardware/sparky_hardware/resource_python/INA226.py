"""
Classe simple pour lire la tension avec l'INA226
"""
import smbus2

class INA226:
    def __init__(self, address=0x45, bus_number=1):
        """
        Initialise le capteur INA226
        
        Args:
            address: Adresse I2C (défaut: 0x40)
            bus_number: Numéro du bus I2C (défaut: 1)
        """
        self.address = address
        self.bus = smbus2.SMBus(bus_number)
    
    def get_voltage(self):
        """
        Lit la tension du bus
        
        Returns:
            float: Tension en Volts
        """
        # Registre Bus Voltage = 0x02
        data = self.bus.read_i2c_block_data(self.address, 0x02, 2)
        raw_value = (data[0] << 8) | data[1]
        # LSB = 1.25mV
        voltage = raw_value * 0.00125
        return voltage
    
    def close(self):
        """Ferme la connexion I2C"""
        self.bus.close()


# Test
if __name__ == '__main__':
    ina = INA226()
    print(f"Tension: {ina.get_voltage():.8f} V")
    ina.close()
