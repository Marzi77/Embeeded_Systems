# Bibliotheken importieren
import time
import RPi.GPIO as GPIO
from mpu6050 import mpu6050
import math

# === Konstanten ===
TIMEOUT = 0.05  # Timeout-Zeit für Ultraschallsensor in Sekunden
MAX_FAILED_MEASUREMENTS = 5  # Maximale Anzahl fehlgeschlagener Distanzmessungen bevor das Programm stoppt
ANGLE_STEP = 10  # Schrittweite der Winkeländerung in Grad (für die Geschwindigkeitsanpassung)
ANGLE_TRESHOLD = 1  # Schwellwert für die Winkeländerung

# === Pin-Zuordnung für den Entfernungssensor (Ultraschall) ===
TRIG = 23
ECHO = 24

# === Pin-Zuordnung für den Motor (L293D Treiber) ===
ENA = 22  # PWM-fähiger Pin für Geschwindigkeit
IN1 = 17  # Richtungspin 1
IN2 = 27  # Richtungspin 2

# === GPIO Setup ===
GPIO.setmode(GPIO.BCM)  # Verwende BCM-Nummerierung
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

pwm = None
try:
    # PWM initialisieren (1000 Hz)
    pwm = GPIO.PWM(ENA, 1000)
    pwm.start(0)

    # Gyrosensor initialisieren
    gyro = mpu6050(0x68)

    # === Funktion: Kombinierte Winkelberechnung (Sensorfusion Gyro + Beschleunigungssensor) ===
    def get_filtered_x_rotation(filtered_angle, last_time):
        try:
            accel_data = gyro.get_accel_data()
            gyro_data = gyro.get_gyro_data()
            current_time = time.perf_counter()
            dt = current_time - last_time

            # Winkel basierend auf Beschleunigungssensor berechnen
            x = accel_data['x']
            y = accel_data['y']
            z = accel_data['z']
            accel_angle = math.degrees(math.atan2(y, math.sqrt(x**2 + z**2)))

            # Winkeländerung basierend auf Gyroskopdaten berechnen
            gyro_rate = gyro_data['x']
            gyro_angle_change = gyro_rate * dt

            # Filter (Complementary Filter) anwenden
            alpha = 0.98
            filtered_angle = alpha * (filtered_angle + gyro_angle_change) + (1 - alpha) * accel_angle

            return filtered_angle, current_time
        except Exception as e:
            print(f"Gyro verisi alınamadı: {e}")
            return filtered_angle, last_time

    # === Funktion: Entfernung messen (Ultraschallsensor) ===
    def measure_distance():
        # Ultraschallsignal senden
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        start_time = time.perf_counter()

        # Warte auf Echo-Signal (Start)
        while GPIO.input(ECHO) == 0:
            if time.perf_counter() - start_time > TIMEOUT:
                return -1
        pulse_start = time.perf_counter()

        # Warte auf Echo-Signal (Ende)
        while GPIO.input(ECHO) == 1:
            if time.perf_counter() - pulse_start > TIMEOUT:
                return -1
        pulse_end = time.perf_counter()

        # Entfernung berechnen
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        return round(distance, 2)

    # === Funktion: Motor bewegen ===
    def move_motor(pwm_instance, speed_percent):
        # Geschwindigkeit begrenzen
        speed = max(0, min(100, speed_percent))

        if speed <= 50:
            # Wenn Geschwindigkeit zu niedrig ist, Motor anhalten
            GPIO.output(IN1, False)
            GPIO.output(IN2, False)
        else:
            # Vorwärtsfahrt
            GPIO.output(IN1, True)
            GPIO.output(IN2, False)

        # PWM-Wert anpassen
        pwm_instance.ChangeDutyCycle(speed)

    # === Initialwerte ===
    filtered_angle = 0.0
    last_time = time.perf_counter()
    filtered_angle, last_time = get_filtered_x_rotation(filtered_angle, last_time)
    current_speed = 50  # Startgeschwindigkeit
    reference_speed = filtered_angle
    failed_measurements = 0
    last_angle = 0.0

    # === Hauptprogrammschleife ===
    while True:
        distance = measure_distance()

        # Fehlerhafte Messung behandeln
        if distance == -1:
            failed_measurements += 1
            print(f"Mesafe ölçülemedi ({failed_measurements}/{MAX_FAILED_MEASUREMENTS}).")
            move_motor(pwm, 0)

            if failed_measurements >= MAX_FAILED_MEASUREMENTS:
                print("Çok fazla hatalı ölçüm. Program sonlandırılıyor.")
                break

            time.sleep(0.2)
            continue
        else:
            failed_measurements = 0

        print(f"Mesafe: {distance} cm")

        # Sicherheitsabstand prüfen
        if distance < 20 or distance > 300:
            move_motor(pwm, 0)
            current_speed = 0
            print("Mesafe sınır dışında, motor durduruldu.")
            time.sleep(0.3)
            continue

        # Geschwindigkeit je nach gemessener Entfernung anpassen
        if 20 <= distance < 50:
            max_speed = 70
            accel_step = 4
            decel_step = 8
        elif 50 <= distance < 150:
            max_speed = 85
            accel_step = 8
            decel_step = 10
        else:
            max_speed = 100
            accel_step = 12
            decel_step = 15

        # Gyro-Winkel aktualisieren
        filtered_angle, last_time = get_filtered_x_rotation(filtered_angle, last_time)
        delta_angle = filtered_angle - reference_speed
        last_angle = filtered_angle

        print(f"Açı (X rotasyonu): {filtered_angle:.2f}° | Değişim: {delta_angle:.2f}°")

        # Anpassung der Geschwindigkeit je nach Winkeländerung
        if abs(delta_angle) > 10:
            if delta_angle > 0:
                current_speed += accel_step
            else:
                current_speed -= decel_step
                current_speed = max(50, current_speed)
            delta_angle = 0
            reference_speed = filtered_angle

        # Geschwindigkeit begrenzen
        current_speed = max(0, min(max_speed, current_speed))
        print(f"Aktif Hız: {current_speed}% (Max: {max_speed}%)")

        # Motor bewegen
        move_motor(pwm, current_speed)
        time.sleep(0.1)

# === Beenden bei Tastenkombination (Ctrl+C) ===
except KeyboardInterrupt:
    print("Program durduruldu.")

# === GPIO aufräumen ===
finally:
    if pwm:
        pwm.stop()
    GPIO.cleanup()
