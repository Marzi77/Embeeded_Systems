# Bibliotheken importieren
import time
import RPi.GPIO as GPIO

# === Pin-Zuordnung für den Entfernungssensor (Ultraschallsensor) ===
TRIG = 23
ECHO = 24

# === GPIO Setup ===
GPIO.setmode(GPIO.BCM)  # Verwende BCM-Nummerierung
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# === Funktion: Entfernung messen ===
def measure_distance():
    # Trigger auf LOW setzen (Sensor zurücksetzen)
    GPIO.output(TRIG, False)
    time.sleep(0.1)

    # Ultraschall-Impuls senden
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # ECHO-Pin: Warte auf steigende Flanke → Startzeit erfassen
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    
    # ECHO-Pin: Warte auf fallende Flanke → Endzeit erfassen
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # Impulsdauer berechnen
    pulse_sure = pulse_end - pulse_start

    # Entfernung berechnen:
    # Schallgeschwindigkeit ca. 34300 cm/s → Entfernung = (Dauer * Geschwindigkeit) / 2
    mesafe = pulse_sure * 17500  # Vereinfachte Formel (17500 = 34300 / 2)
    mesafe = round(mesafe, 2)

    return mesafe

# === Hauptlogik ===
try:
    # Benutzer gibt die tatsächliche Entfernung (in cm) ein
    gercek_mesafe_cm = float(input("Mesafeyi girin: "))
    olcumler = []

    # 5 Messungen durchführen
    for i in range(5):
        mesafe = measure_distance()
        print(f"Ölçüm {i+1}: {mesafe} cm")
        olcumler.append(mesafe)
        time.sleep(1)  # Zwischen den Messungen 1 Sekunde Pause

    # Durchschnitt berechnen
    ortalama_olcum = sum(olcumler) / len(olcumler)

    # Korrekturfaktor berechnen
    duzeltme_katsayisi = gercek_mesafe_cm / ortalama_olcum

    # Ergebnisse anzeigen
    print(f"\nOrtalama Ölçüm: {ortalama_olcum: .2f} cm")
    print(f"Hesaplanan düzeltme katsayısı: {duzeltme_katsayisi:.4f}")

    # Kalibrierte Messung durchführen und anzeigen
    kalibre_mesafe = measure_distance() * duzeltme_katsayisi
    print(f"Kalibre edilmiş mesafe ölçümü: {kalibre_mesafe:.2f} cm")

# === Bei Abbruch (Ctrl+C) ===
except KeyboardInterrupt:
    print("Hata")  # Fehlerabbruchmeldung

# === GPIO Pins aufräumen ===
finally:
    GPIO.cleanup()
