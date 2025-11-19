# Klassen - Erklärung



| Dateiname          | Klassenname    | Bezeichner                             | Funktionen                                           | Erklärung                                    |
| ------------------ | -------------- | -------------------------------------- | ---------------------------------------------------- | -------------------------------------------- |
| analog.py          | Analog         | Helligkeit_V, Helligkeit_H, Distanz    | `current_value()`                                    | Allgemeine Klasse für alle analogen Sensoren |
| digital.py         | Digital        | Knopf_VR, Knopf_VL, Knopf_HR, Knopf_HL | `is_pressed()`, `current_value()`                    | Klasse für alle digitalen Sensoren           |
| distance_sensor.py | DistanceSensor | Distanz                                | `current_value()`                                    | Klasse für den Distanz Sensor                |
| driveR.py          | driveR_two     | Fahrzeug                               | `drive_straight()`, `turn_degrees()`, `turn_wheel()` | Klasse zum Fahren                            |
| light_sensor.py    | LightSensor    | Helligkeit_V, Helligkeit_H             | `current_value()`, `get_value_*()`, `sees_*()`       | Klasse für den Licht- und Helligkeitssensor  |
| servo.py           | ServoX         | Servo_Arm, Servo_Hand                  | `set_pos()`, `range_to_pos()`                        | Klasse für die Servo                         |

