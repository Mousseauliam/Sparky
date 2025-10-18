import smbus2
import time

class PCADriver:
    """Driver minimaliste pour le PCA9685 sans bibliothèque externe."""

    # Registres PCA9685
    __MODE1 = 0x00
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06

    def __init__(self, address=0x40, busnum=1, freq=50):
        self.bus = smbus2.SMBus(busnum)
        self.address = address
        self.freq = freq
        self._setup()

    def _setup(self):
        # Sort du mode veille
        self.bus.write_byte_data(self.address, self.__MODE1, 0x00)
        time.sleep(0.005)
        self.set_pwm_freq(self.freq)

    def set_pwm_freq(self, freq_hz):
        """Configure la fréquence du PWM"""
        prescaleval = 25000000.0    # horloge 25 MHz
        prescaleval /= 4096.0
        prescaleval /= float(freq_hz)
        prescaleval -= 1.0
        prescale = int(prescaleval + 0.5)

        oldmode = self.bus.read_byte_data(self.address, self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10  # mode sleep
        self.bus.write_byte_data(self.address, self.__MODE1, newmode)
        self.bus.write_byte_data(self.address, self.__PRESCALE, prescale)
        self.bus.write_byte_data(self.address, self.__MODE1, oldmode)
        time.sleep(0.005)
        self.bus.write_byte_data(self.address, self.__MODE1, oldmode | 0x80)

    def set_pwm(self, channel, on, off):
        """Écrit les registres ON/OFF d’un canal"""
        reg = self.__LED0_ON_L + 4 * channel
        data = [on & 0xFF, on >> 8, off & 0xFF, off >> 8]
        self.bus.write_i2c_block_data(self.address, reg, data)

    def set_pwm_duty(self, channel, duty):
        """Ajuste le rapport cyclique en pourcentage [0-100]"""
        if duty <= 0:
            self.set_pwm(channel, 0, 0)
        elif duty >= 100:
            self.set_pwm(channel, 0, 4095)
        else:
            off = int(4095 * (duty / 100.0))
            self.set_pwm(channel, 0, off)

    def close(self):
        """Ferme la connexion I2C"""
        if hasattr(self, 'bus'):
            self.bus.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
