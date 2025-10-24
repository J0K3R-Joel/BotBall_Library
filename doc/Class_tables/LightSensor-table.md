# LightSensor



<center> <h2> Get </h2>  </center>



### current_value

#### Methode

```python
current_value() -> int
```

#### Parameter-Erklärung

Diese Methode hat **keine Parameter**.

#### Rückgabe

- `int`:
   Der aktuelle Messwert des Lichtsensors am zugewiesenen Port.
   Dieser Wert gibt die momentane Helligkeit der Umgebung oder der Fläche unter dem Sensor an.

#### Allgemeine Erklärung

Die Methode liefert den **aktuellen Wert des Lichtsensors** zurück.
 Sie ist nützlich, um **Helligkeitsmessungen in Echtzeit** durchzuführen, z. B. für **Linienverfolgung**, Farberkennung oder Anpassung der Sensorempfindlichkeit.
 Der zurückgegebene Wert kann direkt für **Schwellwertvergleiche**, **Bias-Berechnungen** oder andere **regelbasierte Steuerungen** verwendet werden.

---

### get_value_black

#### Methode

```python
get_value_black() -> int
```

#### Parameter-Erklärung

Diese Methode hat **keine Parameter**.

#### Rückgabe

- `int`:
   Der gespeicherte Helligkeitswert, der den **Schwarzwert des Lichtsensors** repräsentiert.
   Dieser Wert wird als Referenz verwendet, um zu erkennen, wann der Sensor eine schwarze Fläche erfasst.

#### Allgemeine Erklärung

Diese Methode gibt den zuvor gespeicherten **Schwarzwert** des Lichtsensors zurück.
 Der Wert wird insbesondere für **Linienverfolgungs- oder Farberkennungsfunktionen** genutzt, damit der Roboter zuverlässig zwischen dunklen (schwarzen) und hellen (weißen) Flächen unterscheiden kann.

---

### get_value_white

#### Methode

```python
get_value_white() -> int
```

#### Parameter-Erklärung

Diese Methode hat **keine Parameter**.

#### Rückgabe

- `int`:
   Der gespeicherte Helligkeitswert, der den **Weißwert des Lichtsensors** repräsentiert.
   Dieser Wert dient als Referenz, um zu erkennen, wann der Sensor eine weiße Fläche erfasst.

#### Allgemeine Erklärung

Diese Methode gibt den zuvor gespeicherten **Weißwert** des Lichtsensors zurück.
 Der Wert wird insbesondere für **Linienverfolgungs- oder Farberkennungsfunktionen** genutzt, damit der Roboter zuverlässig zwischen hellen (weißen) und dunklen (schwarzen) Flächen unterscheiden kann.

---

### get_bias

#### Methode

```python
get_bias() -> int
```

#### Parameter-Erklärung

Diese Methode hat **keine Parameter**.

#### Rückgabe

- `int`:
   Der gespeicherte **Toleranzwert** (Bias), der angibt, wie viel Abweichung zwischen den Sollwerten (z. B. Weiß- und Schwarzwert) akzeptiert wird.
   Dieser Wert wird genutzt, um kleine Messungenauigkeiten oder Schwankungen im Lichtsensor auszugleichen.

#### Allgemeine Erklärung

Die Methode gibt den **Bias** zurück, also den erlaubten Fehlerbereich bei der Erkennung von hellen und dunklen Flächen.
 Dieser Wert ist besonders wichtig für **Linienverfolgungs- oder Schwellwert-Funktionen**, damit der Roboter nicht zu empfindlich auf kleine Unterschiede reagiert und stabil zwischen „an“ (weiß) und „aus“ (schwarz) unterscheiden kann.

---



<center> <h2> Prüfen </h2>  </center>



### sees_black

#### Methode

```python
sees_black() -> bool
```

#### Parameter-Erklärung

Diese Methode hat **keine Parameter**.

#### Rückgabe

- `bool`:
  - `True`: Der Lichtsensor erkennt eine **schwarze Fläche**.
  - `False`: Der Lichtsensor erkennt **keine schwarze Fläche** oder der Messwert liegt außerhalb des definierten Schwarzwertbereichs.

#### Allgemeine Erklärung

Diese Methode prüft, ob der Lichtsensor aktuell **Schwarz** sieht.
 Sie vergleicht den gemessenen Wert mit dem gespeicherten **Schwarzwert** und dem **Bias** und liefert eine einfache **True/False-Antwort**.
 Dies ist besonders nützlich für **Linienverfolgungs- oder Farbdetektionsfunktionen**, bei denen der Roboter schnell erkennen muss, ob er sich auf einer schwarzen Linie befindet.

---

### sees_white

#### Methode

```python
sees_white() -> bool
```

#### Parameter-Erklärung

Diese Methode hat **keine Parameter**.

#### Rückgabe

- `bool`:
  - `True`: Der Lichtsensor erkennt eine **weiße Fläche**.
  - `False`: Der Lichtsensor erkennt **keine weiße Fläche** oder der Messwert liegt außerhalb des definierten Weißwertbereichs.

#### Allgemeine Erklärung

Diese Methode prüft, ob der Lichtsensor aktuell **Weiß** sieht.
 Sie vergleicht den gemessenen Wert mit dem gespeicherten **Weißwert** und dem **Bias** und liefert eine einfache **True/False-Antwort**.
 Dies ist besonders nützlich für **Linienverfolgungs- oder Farbdetektionsfunktionen**, bei denen der Roboter schnell erkennen muss, ob er sich auf einem hellen Untergrund befindet.