#  Intelligentes Haustierspielzeug 

Dieses Projekt wurde entwickelt, um den Alltag von Haustierbesitzern zu erleichtern und gleichzeitig die körperliche und geistige Aktivität ihrer Haustiere zu fördern.

Das **„Intelligente Haustierspielzeug“** besteht aus einem interaktiven System, bei dem ein Spielzeug – etwa ein Plüschobjekt oder ein hüpfender Ball – an einem Seil befestigt ist und durch einen **Gleichstrommotor** in Bewegung versetzt wird.  
Die Art des Spielzeugs kann individuell an die Interessen des jeweiligen Haustiers angepasst werden.

---

##  **Funktionsweise**

- Das System misst kontinuierlich die Entfernung zu Hindernissen (z.B. dem Haustier) mithilfe eines **Ultraschallsensors (HC-SR04)**.
- Gleichzeitig wird die Neigung/Rotation des Systems mit einem **Gyrosensor (MPU6050)** erfasst.
- Abhängig von:
  - **der Bewegung / Rotation** (z.B. wenn das Spielzeug angestoßen wird oder sich der Untergrund neigt),
  - **und der Entfernung des Haustiers** (z.B. ob das Haustier in der Nähe ist oder nicht),
  
  passt das System automatisch die **Motordrehzahl** an und bewegt damit das Spielzeug:

     Das Spielzeug wird bei Erkennen eines Haustiers **aktiv** bewegt.  
     Bei starker Annäherung oder Gefahr wird es automatisch **gestoppt**.  
     Es reagiert auf äußere Bewegungen/Rotationen für ein natürlicheres Spielverhalten.

---

##  **Hardware-Anforderungen**

- Raspberry Pi (getestet auf Raspberry Pi 4)
- **MPU6050 Gyrosensor**
- **HC-SR04 Ultraschallsensor**
- **DC-Motor** (an einem Seil befestigt)
- **L293D Motor-Treiber**
- Spielzeug (z.B. Plüsch, Ball, leichte Struktur)
- Stromversorgung für Motor und Raspberry Pi
- Jumper-Kabel

---

##  **Code-Überblick**

- **`get_filtered_x_rotation()`** → Berechnet gefilterten Rotationswinkel (X-Achse).
- **`measure_distance()`** → Misst aktuelle Entfernung zum Haustier / Objekt.
- **`move_motor()`** → Steuert die Motordrehzahl abhängig von Sensorwerten.

 Die Hauptlogik steuert das Spielzeug so, dass es **spielerisch und reaktiv** agiert.

---

##  **Installation & Setup**

1. Bibliotheken installieren:

```bash
pip install RPi.GPIO mpu6050-raspberrypi
