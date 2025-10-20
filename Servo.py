import math

class Servo:
    """Convertit un angle en PWM pour le PCA9685"""
    def __init__(self, driver, channel, min_us=500, max_us=2500, freq=50):
        self.driver = driver
        self.channel = channel
        self.min_us = min_us
        self.max_us = max_us
        self.period_us = 1_000_000 / freq  # Période du PWM en µs

    def set_angle(self, angle):
        """Définit l’angle du servo en degrés [0-180]"""
        angle = max(0, min(180, angle))
        pulse_us = self.min_us + (self.max_us - self.min_us) * (angle / 180.0)
        duty = (pulse_us / self.period_us) * 100
        self.driver.set_pwm_duty(self.channel, duty)
        
    def neutral(self):
        """Positionne le servo à l’angle neutre (90°)"""
        self.set_angle(90)
        
    def channel_info(self):
        """Retourne les informations du servo"""
        return self.channel, 
