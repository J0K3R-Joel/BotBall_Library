# Klassen - Erklärung



| Dateiname          | Klassenname    | Bezeichner                             | Funktionen                                           | Erklärung                                    |
| ------------------ | -------------- | -------------------------------------- | ---------------------------------------------------- | -------------------------------------------- |
| analog.py          | Analog         | Helligkeit_V, Helligkeit_H, Distanz    | `current_value()`                                    | Allgemeine Klasse für alle analogen Sensoren |
| digital.py         | Digital        | Knopf_VR, Knopf_VL, Knopf_HR, Knopf_HL | `is_pressed()`, `current_value()`                    | Klasse für alle digitalen Sensoren           |
| distance_sensor.py | DistanceSensor | Distanz                                | `current_value()`                                    | Klasse für den Distanz Sensor                |
| driveR.py          | driveR_two     | Fahrzeug                               | `drive_straight()`, `turn_degrees()`, `turn_wheel()` | Klasse zum Fahren                            |
| light_sensor.py    | LightSensor    | Helligkeit_V, Helligkeit_H             | `current_value()`, `get_value_*()`, `sees_*()`       | Klasse für den Licht- und Helligkeitssensor  |
| servo.py           | ServoX         | Servo_Arm, Servo_Hand                  | `set_pos()`, `range_to_pos()`, `range_from_to_pos()` | Klasse für die Servo                         |

---

```python
current_value() -> int
```

Gibt den aktuellen Wert zurück (als Ganzzahl)

---

```python
is_pressed() -> bool
```

Sagt, ob der Knopf gedrückt ist (`True`) oder nicht (`False`)

---

```python
drive_straight(millis: int, speed: int = None) -> None
```

Bringt den Roboter dazu, geradeaus zu fahren

---

```python
turn_degrees(direction: str, degree: int) -> None
```

Bringt den Roboter dazu, sich in einem bestimmten Winkel in eine bestimmte Richtung zu drehen

---

```python
turn_wheel(direction: str, speed: int, millis: int) -> None
```

Bringt den Roboter dazu, sich in eine Richtung für eine bestimmte Zeit zu drehen, aber nur mit einem Rad

---

```python
get_value_black() -> int
get_value_white() -> int
```

Sagt, ab welchem ganzzahligen Wert der Roboter Schwarz oder Weiß sieht

---

```python
sees_Black() -> bool
sees_White() -> bool
```

Sagt, ob der Roboter gerade Schwarz oder Weiß sieht

---

```python
set_pos(value: int) -> None
```

Setzt die Position vom Servo zum vorgegebenen Wert

---

```python
range_to_pos(value: int, multi: int = 2) -> None
```

Geht langsam vom aktuellen Servo Wert zu dem vorgegebenen Wert (zum flüssigen Auf- oder Zumachen)

---

```python
range_from_to_pos(interval: list, multi: int = 2) -> None
```

Geht langsam vom ersten angegebenen Wert zum zweiten angegebenen Wert (zum flüssigen Auf- oder Zumachen)

---





