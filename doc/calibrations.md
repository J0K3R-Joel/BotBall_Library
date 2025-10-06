# Calibration

This file tells you how to calibrate the wallaby / wombat / controller / ... . Calibration is very important to ensure consistency. The more you calibrate the better. My calibration methods are written into files in `/usr/lib/bias_folder`, so you just need to properly calibrate them once and every function that needs those calibrations will read from the desired file. If you want the most current bias and therefore need to calibrate them while setting up, then the more you calibrate the longer it will take.

## driveR 

#### calibrate_distance()

###### Considerations:

- You need an object which is flat and long on a side (e.g. a box). This is due to slight error while driving back
- You can mount the ET Sensor everywhere, since the distance has to be measured from the ET Sensor to the object which you want to use for calibration 
- Try it out if the values are correct. If they are not, just re-run this function and the values will get overwritten (on the other hand, if the calibrated values match the values in real life, then re-running this function might lead to worse values)
- Make sure to keep track of the actual lowest value to the object while this function executes the first time (while the robot is standing still, the measured lowest distance does not match the driving lowest distance). Afterwards re-run the function

###### How to calibrate:

0. Everything will take place on a flat surface / game table
1. Place an flat and long object on the surface
2. Go away from the object with the robot and look for the lowest value facing the object parallel (**HINT**: the more you make it parallel, the more you will notice that the value changes from maybe ~800 to ~200 while maintaining the same distance to the object. This value becomes a little bit more consistent while driving, so make sure that while trying your first lowest value to keep track of the "actual" lowest value. Your first run of this function will so to say just be a test run. The actual lowest value will probably be around ~600. You can just make a low number up, so the robot will drive endlessly so you can be more focused on the "actual" lowest value.)
3. Look for the distance where the ET Sensor is having the highest value (go slow and steady, every mm counts!)
4. Make sure the robot is parallel to the object
5. Measure the distance from the front of the ET Sensor to the flat and long object (distance in mm)
6. Tell the function your two measurements: 
   1. the mm where the distance is the highest
   2. actual lowest value of the ET Sensor 

#### calibrate_degrees()

###### Considerations:

- 
