# Good-To-Knows

This file will tell you things to consider and important stuff. This is very important since my entire library is dependent on some things. On the other hand this file includes great information about other stuff as well

### Considerations

- You can call `help({function_name})` or `help({class_name.function_name})` on any function I made to view its signature and doc-string

- You will find the `ideas.py` file inside the [../src/src_Base/](../src/src_Base/ideas.py) folder. This file is meant to collect ideas on how to handle certain tasks or provide potentially useful snippets. It is not intended for direct execution, but rather as a reference to help with situational problems or concepts that didn’t fit neatly into any class

- Some classes—especially the `FakeR` class—are quite complex in terms of logic. The `RoboCommunicator` and `FakeR` classes work hand in hand, which makes communication increasingly complicated the more features you add. Since both robots need to communicate seamlessly to get the most value, mastering communication between `RoboCommunicator`, `FakeR`, and the camera classes unlocks almost limitless possibilities. If you have any questions about what to do or how something works, feel free to reach out to me

- You can look after setting up the robot in `/usr/lib/bias_folder` to see the bias files. They get updated every time a bias is made

- You can look after setting up the robot in `/usr/lib/logger_log` to see all the logs, that it made. That's why it is preferred to use the `log()` function inside the `logger.py`, since you are able to see the logs, even after something went wrong and it restarted or anything else. Since they get saved in the file, you can look at the errors or informations all the time

- You can look after setting up the robot in `/usr/lib/LOCAL_STD_WIFI.conf` to see and change the default SSID and password of the private network / router. This is like [step 4 in the Installation](../README.md#Installation) segment

- Every time you change the weight or size, you should calibrate all bias again. The more often the better, since the bias is getting calibrated with the current and last bias

- If you are using the camera, please make sure to release it at the end of the code (I provided a function in the `CameraManager` class, which is called `release`)

- If you get into the `driveR.py` file, you will find `gyro_z` and `gyro_y`. While they are getting explained, there is still `gyro_x`, which is not in use yet. This value is for the following: If the controller is (for example) laying down and then it is on the way of standing up, then `gyro_x` changes. You will also find the `accel_x` value. `accel_y` and `accel_z` get explained, but not `accel_x`. This value (`accel_x`) is changing, when the controller is (for example) lying down and then getting moved left or right

- You will find in every `main.py` file which is somehow connected with communication `p_event` and `communication` parameters. You will need those parameters everywhere, where you want communication. `p_event` is the short form of "pause_event". With this parameter you are able to pause the main every time a `high` priority message gets sent to you. On the other hand the `communication` parameter is for reading and sending messages to the other robot. More on that in [./explainer/user_server_client_fake.md](./explainer/user_server_client_fake.md). **HINT:** Name those parameters / variables **everywhere the same**! 

- You need to make sure that if the values of the motor position gets positive, then the motors have to make the robot move forward. All `driveR` functions are expecting, that this works and that this is the case

- In [./threadsafe_classes.md](./threadsafe_classes.md) every class that supports multi threading / threading is written down

- In [./calibrations.md](./calibrations.md) you will find how to calibrate (and why you should consider calibration) the robot

- The buttons mounted on the robot need to be the furthest point in the front and rear.

- The tophats should be as low as possible, but they should not scratch the ground. If they are positioned too high, then the values are more inaccurate (since the sensor can not detect the difference between white and black as precise). If they are too low, they will scratch the ground and may get damaged. Also consider the shadow the robot casts onto the tophats.

- If there is a new update in my GitHub repository and you want to pull it, then there are two ways:

  1. repeat every step in the [README installation](../README.md#Installation) guide

  2. only copy the new files from the pulled directory which are relevant for you and paste it into the corresponding folder. The old file gets overwritten this way.

  No matter which path you choose, you need to make sure that nothing important gets overwritte -> you can not get the changes back. Save every important file, especially when you use the first step, since it overwrites every file.

- If you have no experience on the controller, then consider the [./controller_guide.md](./controller_guide.md) file

- If you use my library and with it the `light_sensor` class, then you will encounter the `bias` variable. This variable is for widening the range of where the light sensor can see black / white. Higher value means it is more forgiving and a lower value means it is less forgiving in detecting the brightness.

- When coding in the KISS IDE, then make sure that you safe / compile the code before switching files inside the KISS IDE, otherwise your new code will be overwritten by the latest saved code and you have to start all over again since the last safe 
