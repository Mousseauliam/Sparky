from time import sleep

class Servo:
    def __init__(self, driver, channel, min_pulse=150, max_pulse=600, default_angle=90):
        """
        Initialise un servo
        
        Args:
            driver: Instance de PCADriver
            channel: Numéro du canal (0-15)
            min_pulse: Largeur d'impulsion min (correspond à 0°)
            max_pulse: Largeur d'impulsion max (correspond à 180°)
            default_angle: Angle par défaut au démarrage
        """
        self.driver = driver
        self.channel = channel
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.current_angle = float(default_angle)
        
        # Définir l'angle initial (sans interpolation au démarrage)
        self._set_angle_immediate(default_angle)
    
    def _angle_to_pulse(self, angle):
        """Convertit un angle (0-180°) en largeur d'impulsion"""
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
        
        pulse = int(self.min_pulse + (angle / 180.0) * (self.max_pulse - self.min_pulse))
        return pulse
    
    def _set_angle_immediate(self, angle):
        """Définit l'angle immédiatement (sans interpolation)"""
        try:
            pulse = self._angle_to_pulse(angle)
            self.driver.set_pwm(self.channel, 0, pulse)
            self.current_angle = float(angle)
            sleep(0.001)  # ✅ Petit délai de 1ms pour laisser l'I2C respirer
        except OSError as e:
            print(f"⚠️ Erreur I2C servo {self.channel}: {e}")
    
    def set_angle(self, angle, speed=None):
        """
        Définit l'angle du servo avec contrôle de vitesse optionnel
        
        Args:
            angle: Angle cible (0-180°)
            speed: Vitesse en degrés/seconde (None = instantané, ex: 50 = lent, 200 = rapide)
        """
        if speed is None:
            # Mouvement instantané
            self._set_angle_immediate(angle)
        else:
            # Mouvement progressif
            self.move_smooth(angle, speed)
    
    def move_smooth(self, target_angle, speed=50):
        """
        Déplace le servo progressivement vers l'angle cible
        
        Args:
            target_angle: Angle de destination (0-180°)
            speed: Vitesse en degrés/seconde (50 = lent, 200 = rapide)
        """
        # Calculer la différence d'angle
        diff = target_angle - self.current_angle
        
        if abs(diff) < 1:
            # Déjà à la bonne position
            return
        
        # Calculer le nombre d'étapes (1 degré par étape)
        steps = int(abs(diff))
        step_angle = 1.0 if diff > 0 else -1.0
        delay = 1.0 / speed  # Délai entre chaque degré
        
        # ✅ Ajouter un délai minimum pour protéger l'I2C
        delay = max(delay, 0.002)  # Minimum 2ms entre chaque commande
        
        # Interpolation linéaire
        try:
            for i in range(steps):
                self.current_angle += step_angle
                pulse = self._angle_to_pulse(self.current_angle)
                self.driver.set_pwm(self.channel, 0, pulse)
                sleep(delay)
            
            # S'assurer qu'on atteint exactement l'angle cible
            self.current_angle = float(target_angle)
            pulse = self._angle_to_pulse(target_angle)
            self.driver.set_pwm(self.channel, 0, pulse)
            
        except OSError as e:
            print(f"⚠️ Erreur I2C pendant interpolation servo {self.channel}: {e}")
    
    def neutral(self, speed=None):
        """Place le servo en position neutre (90°)"""
        self._set_angle_immediate(90.0, speed)
    
    def get_angle(self):
        """Retourne l'angle actuel du servo en float"""
        return float(self.current_angle)
    
    def channel_info(self):
        """Retourne les infos du canal"""
        return (self.channel, self.driver.address)
