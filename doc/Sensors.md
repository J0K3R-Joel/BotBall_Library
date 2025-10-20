# Robot Sensor System Documentation

## 1. Sensor Overview

- Analog
  
  - Distance (ET)
  
  - Light
  
  - Brightness (Tophat)
  
  - Linear Slide

- Digital
  
  - Touch
  
  - Lever

- Motor

- Servo

## 2. How to see / get the values



### 2.1 Code

##### 2.1.1 Analog

You can receive the value of every analog sensor with the `analog()` function from the kipr library. In python the code will look something like this:

```python
k.analog(PORT)
```

Where:

- PORT is the corresponding port on the controller where the sensor is plugged in
- k is the name of the library (`import _kipr as k`)

##### 2.1.2 Digital

You can receive the value of every digital sensor with the `digital()` function from the kipr library. In python the code will look something like this:

```python
k.digital(PORT)
```

Where:

- PORT is the corresponding port on the controller where the sensor is plugged in
- k is the name of the library (`import _kipr as k`)

##### 2.1.3 Motor

You can receive the value of the current motor position with the `gmpc()` or `get_motor_position_counter()` (which is the long form of "gpmc") function from the kipr library. In python the code will look something like this:

```python
k.gpmc(PORT)
# or
k.get_motor_position_counter(PORT)
```

Where:

- PORT is the corresponding port on the controller where the sensor is plugged in
- k is the name of the library (`import _kipr as k`)

##### 2.1.4 Servo

You can receive the value of the current servo position with the `get_servo_position()` function from the kipr library. In python the code will look something like this:

```python
k.get_servo_position(PORT)
```

Where:

- PORT is the corresponding port on the controller where the sensor is plugged in
- k is the name of the library (`import _kipr as k`)

---

### 2.2 Controller / Hardware

For further information head into the [./controller_guide.md](./controller_guide.md) file.

1. Click on the `Motors and Sensors` button (on the controller)
2. Here you can find the buttons `Motors`, `Servos` and `Sensor List`
   1. `Motors`: Here you can see the "Position" in the top right corner
   2. `Servos`: Here you can see the value of the position underneath the gauge or in the bottom left corner
   3. `Sensor List`: Here you can see every analog and digital sensor value, even some inbuilt sensors such as "Magnetometer", "Gyro" and "Accelerometer" can be viewed here 

---

## 3. Details

### 3.1 Analog

##### 3.1.1 Distance Sensor (ET)

![](./img/distance_sensor.png)

The distance sensor returns a value between `200` - `2900`. The value it returns depends on some factors (at least from what I noticed):

- distance

- temperature

- light

This sensor is unfortunatelly very unreliable, so keep care when using it! It works great on distances between `100` - `800`mm. Everything above 800mm will not be recognised and everything below 100mm is very inconsistent and is very hard to balance.  

##### 3.1.2 Light Sensor

![](./img/light_sensor.png)

The light sensor returns a value from `1000` - `3100`. The value it returns depends on one factor:

- brightness of light

This sensor is reliable. It is works best for light emitting sources, like a lamp. This is great for the start of the game. Theoretically it could be used as a brightness sensor, but with less bias between the top and low threshold. 

##### 3.1.3 Brightness Sensor (Tophat)

![](./img/large_tophat.png) ![](./img/small_tophat.png)

The Tophat sensors (small and large) return a value from `200` - `3700`. The value they return depends on one factor:

- Greyscale of the ground where the sensor faces

There is not really a difference between the small and large Tophat sensors. From what I noticed the only difference is the area which gets scanned. 

##### 3.1.4 Linear Slide

![](./img/slide.png)

The linear slide returns a value from `0`  - `2047`. The value it returns depends on one factor:

- The position of the slider (the further away from the cable the higher the value)

Unfortunatelly you can not set the value, you can only receive the value it is at the moment

---

### 3.2 Digital

##### 3.2.1 Touch

![](./img/button_small.png)![](./img/button_large.png)

The small and large Buttons return the values `0` or `1`. The value it returns depends on one factor:

- If it is pressed, it returns `1`, otherwise it returns `0` 

You should keep care a bit on the large Touch sensor, since if it is pressed from the side, it is counted as pressed.

##### 3.2.2 Lever

![](./img/lever.png)

The Lever returns the values `0` or `1`. The value depends on one factor:

- If it is pressed, it returns `1`, otherwise it returns `0`

The last years you were able to bend the metal, which made. You also need to be careful to not crush the metal piece, since it is not very durable

---

### 3.3 Motor

![](./img/motor.png)

The motor is very diverse. It can move 360 degrees in a loop. You can use them for something simple just as driving and for something advanced like an arm. You can receive and set the value in ticks / velocity / ... . They are not really depending on a factor, but something you need to keep care about is the following:

- If you are using it for an arm you will encounter the problem that sometimes it will not move (even if the arm is not too heavy for lifting). This is due to how the initial source code is written. It is highly inefficient with a lot of time of waiting time. If you control the motor in this time of "maintenance" it simply will not move. You can try to fix this issue yourself   

---

### 3.4 Servos

##### 3.4.1 Servo

![](./img/servo.png)

The servo is great for using it as an arm or claw. It can move 180 degrees. It is not really dependant on anything. It is very consistent and I did not encounter any problems with those. You can receive and set the value of a servo very accurately.

##### 3.4.2 Micro Servo

![](./img/micro_servo.png)

The micro servo is not that consistent. It is very important to consider the following:

- Even though you are able to set the value very high, you should not do this, since otherwise it will break. Since it is still a servo, it can move 180 degrees.

You are able to receive and set the value, just as the normal servo, since it uses the same functions. **HINT**: If you are using my library, you can just set the min and max value and from there on you are not able to exceed the numbers.
