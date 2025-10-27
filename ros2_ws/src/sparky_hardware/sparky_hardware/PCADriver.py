import time
import smbus2

class PCADriver:
    """Driver minimaliste pour le PCA9685 sans bibliothèque externe."""

    # Registres PCA9685
    __MODE1 = 0x00
    __MODE2 = 0x01
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06

    # Bits MODE1
    _MODE1_RESTART = 0x80
    _MODE1_AI      = 0x20
    _MODE1_SLEEP   = 0x10
    _MODE1_ALLCALL = 0x01

    # Bits MODE2
    _MODE2_OUTDRV  = 0x04  # totem-pole (nécessaire pour piloter un servo)

    def __init__(self, address=0x40, busnum=1, freq=50):
        self.bus = smbus2.SMBus(busnum)
        self.address = address
        self.freq = freq
        self._setup()

    def _setup(self):
        # Mode ALLCALL + réveil de base
        self.bus.write_byte_data(self.address, self.__MODE1, self._MODE1_ALLCALL)
        time.sleep(0.005)
        # Sorties en totem-pole (sinon open-drain -> signal collé bas sans pull-up)
        self.bus.write_byte_data(self.address, self.__MODE2, self._MODE2_OUTDRV)
        # Fréquence PWM + auto-increment + restart
        self.set_pwm_freq(self.freq)

    def set_pwm_freq(self, freq_hz):
        """Configure la fréquence du PWM"""
        prescaleval = 25000000.0 / 4096.0 / float(freq_hz) - 1.0
        prescale = int(prescaleval + 0.5)

        oldmode = self.bus.read_byte_data(self.address, self.__MODE1)
        # Mettre en veille pour écrire PRESCALE
        newmode = (oldmode & ~self._MODE1_RESTART) | self._MODE1_SLEEP
        self.bus.write_byte_data(self.address, self.__MODE1, newmode)
        self.bus.write_byte_data(self.address, self.__PRESCALE, prescale)
        # Réveiller
        self.bus.write_byte_data(self.address, self.__MODE1, oldmode)
        time.sleep(0.005)
        # Activer Auto-Increment + Restart + ALLCALL
        self.bus.write_byte_data(
            self.address,
            self.__MODE1,
            self._MODE1_RESTART | self._MODE1_AI | self._MODE1_ALLCALL
        )

    def set_pwm(self, channel, on, off):
        """Écrit les registres ON/OFF d’un canal"""
        if not 0 <= channel <= 15:
            raise ValueError("channel doit être entre 0 et 15")
        on = max(0, min(4095, int(on)))
        off = max(0, min(4095, int(off)))
        reg = self.__LED0_ON_L + 4 * channel
        # Masquer les 4 bits de contrôle dans les high-bytes (évite FULL_ON/OFF involontaires)
        data = [
            on & 0xFF,
            (on >> 8) & 0x0F,
            off & 0xFF,
            (off >> 8) & 0x0F
        ]
        self.bus.write_i2c_block_data(self.address, reg, data)

    def set_pwm_duty(self, channel, duty):
        """Définit le rapport cyclique en % [0..100]"""
        duty = max(0.0, min(100.0, float(duty)))
        off = int(duty * 4096 / 100.0)
        if off >= 4096:
            off = 4095
        self.set_pwm(channel, 0, off)

    def close(self):
        try:
            self.bus.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
