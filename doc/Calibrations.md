# Calibration

This file tells you how to calibrate the wallaby / wombat / controller / ... . Calibration is very important to ensure consistency. The more you calibrate the better. My calibration methods are written into files in `/usr/lib/bias_folder`, so you just need to properly calibrate them once and every function that needs those calibrations will read from the desired file. If you want the most current bias and therefore need to calibrate them while setting up, then the more you calibrate the longer it will take.

---

There is a `BIAS` user that could assist you with calibration. By changing the "unclear values"[^1] to the correct values there are some functions which helps you to calibrate, since some logic specifically for calibration is already done for you. The following functions do not need any further logic besides uncommenting the call and replacing all unclear values with correct values:

##### light_sensor:

front, back and side:

- 
  ```python
  LightSensor.save_value_black()
  ```

- ```python
  LightSensor.save_value_white()
  ```
  

##### driveR

```python
Solarbotic_Wheels_two.auto_calibration()
```
  or 
```python
Mecanum_Wheels_four.auto_calibration()
```

  which includes calibration of:

  - `gyro_z` 
  - `gyro_y` 
  - `accel_y` 
  - `accel_z`
  - `ONEEIGHTY_DEGREES_SECS`  
  - `NINETY_DEGREES_SECS`

---

On the other hand, there are some functions where manual execution is required, since they need a completely different setup. You should only execute those kind of functions alone and not with any other calibration method, since you need to be precise with those methods. As said, execute them alone with no other function, since they can cause a lot of trouble and there is not a lot of margin for error. Those functions include:

##### driveR

###### calibrate_mm_per_sec() - function

**Code:**

```python
Solarbotic_Wheels_two.calibrate_mm_per_sec()
```
  or 
```python
Mecanum_Wheels_four.calibrate_mm_per_sec()
```

**Explanation:**

This needs to be calculated so the `calibrate_distance()` function works properly. It will calculate how fast the robot is moving (in mm/sec). Further explanation in [calibrate_mm_per_sec()](#calibrate_mm_per_sec())



###### calibrate_distance() - function

**Code:**


```python
Solarbotic_Wheels_two.calibrate_distance(XX)
```

or 

```python
Mecanum_Wheels_four.calibrate_distance(XX)
```

**Explanation:**

This function is needed to be able to know all the distances for the distance sensor. Some functions depend on this, so be sure that the values it returns are correct. Further explanation in [calibrate_distance()](#calibrate_distance())

---

[^1]:Ports and values with a placeholder (e.g. "XX"). If the placeholder represents a port, then you only need to tell it the integer number it is plugged in (e.g. 0; 6; 3; ... ) 

---

If you do not need some parts to calibrate, you can just leave them out

## driveR 

#### calibrate_mm_per_sec()

###### Considerations:

- by default it drives for 5 seconds straight, so make sure that there is enough space in front
- mark where the beginning of the calibration is (place the robot so you can see where it started and measure the distance)

###### How to calibrate:

1. Place the robot so you know where it began to drive
2. Run the program
3. Measure the distance (in mm) from the start to the end
4. Write the mm in the console
5. Press `Enter` 

---

#### calibrate_distance()

###### Considerations:

- You need an object which is flat and long on a side (e.g. a box). This is due to slight error while driving back
- You can mount the ET Sensor everywhere, since the distance has to be measured from the ET Sensor to the object which you want to use for calibration 
- Try it out if the values are correct. If they are not, just re-run this function and the values will get overwritten (on the other hand, if the calibrated values match the values in real life, then re-running this function might lead to worse values)
- When calibrating, make sure that the robot is as close as possible to the object as possible, but only until the value of the distance sensor is at the highest and not further. Go until the value reaches the first time the highest value.

###### How to calibrate:

1. Place an flat and long object on the surface
3. Look for the distance where the ET Sensor is having the highest value (get slow and steady to the object, every mm counts!)
4. Make sure the robot is parallel to the object
5. Measure the distance from the front of the ET Sensor to the flat and long object (distance in mm)
6. Tell the function your measurement: 
   - the mm where the distance value is the highest
7. Run the program

---

#### calibrate_degrees()

###### Considerations:

- The front AND back <u>brightness sensor</u> have to be calibrated. This is because this function turns from a black line to a white area and back to the black line and to recognize the line and area, the brightness sensor needs to know what the black and white values are   
- Make sure that the <u>brightness sensors</u> (front and back) are parallel on the front and rear of the robot
- There is a slight difference between the two classes `Solarbotic_Wheels_two` and `Mecanum_Wheels_four`. In the class `Mecanum_Wheels_four` you are able to tell this function if the robot is on a black line or not. If you tell the function, that the robot is not on the line, then (only in `Mecanum_Wheels_four`!) you have to place the robot parallel next to the line, so it can find the line by itself. On the other hand you can tell the function that it got placed on the line (`on_line=True`). The example in the "How to calibrate" section the robot will be placed on the line 

###### How to calibrate

1. Place the robot on a black line. Both front and back brightness sensors need to be on the black line
2. Run the program

---

#### calibrate_accel_y()

###### Considerations:

- While it calibrates, do NOT touch the robot

###### How to calibrate

- Run the program

---

#### calibrate_accel_z()

###### Considerations:

- While it calibrates, do NOT touch the robot

###### How to calibrate

- Run the program

---

#### calibrate_gyro_z()

###### Considerations:

- While it calibrates, do NOT touch the robot

###### How to calibrate

- Run the program

---

#### calibrate_gyro_y()

###### Considerations:

- While it calibrates, do NOT touch the robot

###### How to calibrate

- Run the program

---

#### hardware_calibration()

###### Considerations:

- While it calibrates, do NOT touch the robot
- It will calibrate every hardware component like `gyro_z`, `gyro_y`, `accel_z`, `accel_y`, since they got hardware on the controller
- It is faster than calibrating every hardware calibrate method specifically, since in the background it will use those calibration methods in threads parallel to each other. 

###### How to calibrate

- Run the program

---

#### calibrate()

###### Considerations:

- In the `calibrate` function there are certain functions that will be executed. Make sure that the considerations of every single calibration method are met.

###### How to calibrate

-  Keep track of the "how to calibrate" sections of every single function to execute

---

#### auto_calibration()

###### Considerations

- Make sure that the considerations of every single calibration method are met.

###### How to calibrate

-  Keep track of the "how to calibrate" sections of every single function to execute
- After the running the program, it will automatically make everything that needs to be done. You just need to tell this function on how to begin the first calibration step and how often it should calibrate (10 times should be enough)

---

## LightSensor

#### save_value_black()

###### Considerations

- make sure that the saved value has average lighting of the entire game table for best results
- make sure it is actually on black
- once saved do not change the position of the light / brightness sensor (at least in the z-axis (height))

###### How to calibrate

- Run the program

---

#### save_value_white()

###### Considerations

- make sure that the saved value has average lighting of the entire game table for best results
- make sure it is actually on white
- once saved do not change the position of the light / brightness sensor (at least in the z-axis (height))

###### How to calibrate

- Run the program

---
