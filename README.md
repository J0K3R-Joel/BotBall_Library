# Robot Utility & Communication Toolkit

**Author:** Joel Kalkusch  
**Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)  
**Nationality**: Austrian (Österreich)  
**Date of Creation**: 2025-09-07

---

## Overview

This repository provides a set of utility classes and communication tools designed for robotics projects using the KIPR framework. It covers:

- Sensor interaction (`Digital`, `DistanceSensor`, `LightSensor`)

- Robot driving (`driveR_two`, `driveR_four`)

- Servo / micro-servo usage (`ServoX`)

- Camera detection (`CameraObjectDetector`, `CameraBrightnessDetector`, `CameraManager`)

- Robot communication (`RobotCommunicator`, `WifiConnector`)

- File management and logging (`FileR`, `logger`)

- Simulation utilities (`FakeR`)

- High-level utility functions (`Util`)

These components simplify programming robots by providing structured interfaces, callback systems, and comprehensive handling of sensors and messaging.

---

## Contents

The repository is organized as follows:

- **Classes for Sensor Handling:**
  
  - `Digital` – Digital buttons
  
  - `DistanceSensor` – Analog distance sensor
  
  - `LightSensor` – Light sensor

- **Movement Classes:**
  
  - `driveR_two` – Two-motor drive system
  
  - `driveR_four` – Four-motor drive system
  
  - `ServoX` - Servo / micro-servo controlling

- **Camera Classes:**
  
  - `CameraManager` - Threadsafe camera control
  
  - `CameraObjectDetector` - Object / color / shape detection
  
  - `CameraBrightnessDetector` - Segment-based brightness detection

- **Communication Classes:**
  
  - `RobotCommunicator` – TCP/IP messaging
  
  - `WifiConnector` – WiFi-based communication

- **Utilities & Helpers:**
  
  - `Util` – High-level utility functions for sensors and waiting behaviors
  
  - `FakeR` – Simulation for threaded main execution
  
  - `FileR` – File management
  
  - `logger` – Custom logging functions

- **Documentation:**
  
  - Detailed explanations are included for each class in the `doc/` folder.

---

## Documentation

Detailed explanations of the classes are included in the repository:

- [commU_explainer.md](./doc/commU_explainer.md) – Full explanation and usage guide for the `WifiConnector` class

- [digital_explainer.md](./doc/digital_explainer.md) – Full explanation and usage guide for the `Digital` class

- [distance_sensor_explainer.md](./doc/distance_sensor_explainer.md) – Full explanation and usage guide for the `DistanceSensor` class

- [driveR_explainer.md](./doc/driveR_explainer.md) – Full explanation and usage guide for the `driveR_two` and `driveR_four` classes

- [fake_explainer.md](./doc/fake_explainer.md) – Full explanation and usage guide for the `FakeR` class

- [fileR_explainer.md](./doc/fileR_explainer.md) – Full explanation and usage guide for the `FileR` class

- [light_sensor_explainer.md](./doc/light_sensor_explainer.md) – Full explanation and usage guide for the `LightSensor` class

- [logger_explainer.md](./doc/logger_explainer.md) – Full explanation and usage guide for the `logger` file

- [RoboComm_explainer.md](./doc/RoboComm_explainer.md) – Full explanation and usage guide for the `RobotCommunicator` class

- [util_explainer.md](./doc/util_explainer.md) – Full explanation and usage guide for the `Util` class

- [servo_explainer.md](./doc/servo_explainer.md) - Full explanation and usage guide for the `ServoX` class

- [brightness_detector_explainer.md](./doc/brightness_detector_explainer.md) - Full explanation and usage guide for the `CameraBrightnessDetector` class

- [object_detector_explainer.md](./doc/object_detector_explainer.md) - Full explanation and usage guide for the `CameraObjectDetector` class

- [camera_manager_explainer.md](./doc/camera_manager_explainer.md) - Full explanation and usage guide for the `CameraManager` class

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/J0K3R-Joel/BotBall_Library.git
```

2. Copy the repository to a USB stick.

3. Go in [./src/WIFI_FOR_INSTALLATION/main.py](./src/WIFI_FOR_INSTALLATION/main.py) and change the SSID and PASS inside the `wifi_setup()` to a wifi that grants you internet access, so libraries can get installed 

4. Go in [./LOCAL_STD_WIFI.conf](./LOCAL_STD_WIFI.conf) and type in the SSID and password of your local router. The local router should be a private router you got from home one, so noone can intercept the communication. Internet access is NOT required. 
   **HINT**: every space, every character and everything after the "=" counts as either the SSID or password (depends on the line you are writing in), so be aware of spaces and other characters you fill in.

5. Go to the [KIPR Wombat firmware](https://www.kipr.org/kipr/hardware-software/kipr-wombat-firmware) page

6. Download the latest image.

7. Flash the image onto the robot following the instructions on the KIPR website.

8. Once the robot is flashed and ready, insert the USB stick.

9. Navigate to the path of the USB stick on the robot.

10. Run the configuration script:

```bash
sudo bash config.sh
```

> Notice: sometimes there is an error in the beginning. If so, then press "Ctrl + c" (for canceling the installation) and afterwards just re-execute the configuration script, then you should be good to go

12. The installation is complete.

---

## Usage

Example usage for most classes is provided in the documentation files linked above.

Additionally, an example usage for the `FakeR` class is provided in [./doc/user_server_client_fake_explaner.md](./doc/user_server_client_fake_explaner.md) file, since this will be the best exercise for the beginning, if you do not have experience with this library. This got two new users (one for as a client, the other as the server)

Other classes that got an entire user as test purpose:

- `Camera` -> `CameraManager`, `CameraObjectDetector`, `CameraBrightnessDetector`

- `WIFI` -> `WifiConnector` 

- `COMM` -> `RobotCommunicator` 

---

## Additional Information

- You can call `help({function_name})` or `help({class_name.function_name})` on any function I made to view its signature and docstring.  

- You will find the `ideas.py` file inside the [./src/src_Base/](./src/src_Base/ideas.py) folder. This file is meant to collect ideas on how to handle certain tasks or provide potentially useful snippets. It is not intended for direct execution, but rather as a reference to help with situational problems or concepts that didn’t fit neatly into any class.

- Some classes—especially the `FakeR` class—are quite complex in terms of logic. The `RoboCommunicator` and `FakeR` classes work hand in hand, which makes communication increasingly complicated the more features you add. Since both robots need to communicate seamlessly to get the most value, mastering communication between `RoboCommunicator`, `FakeR`, and the camera classes unlocks almost limitless possibilities. If you have any questions about what to do or how something works, feel free to reach out to me. 

- You can look after setting up the robot in `/usr/lib/bias_folder` to see the bias files. The get updated every time a bias is made

- You can look after setting up the robot in `/usr/lib/logger_log` to see all the logs, that it made. That's why it is prefered to use the `log()` function inside the `logger.py`, since you are able to see the logs, even after something went wrong and it restarted or anything else. Since they get saved in the file, you can look at the errors or informations all the time

- You can look after setting up the robot in `/usr/lib/LOCAL_STD_WIFI.conf` to see and change the default SSID and password of the private network / router. This is like **step 4 in the Installation** segment. 

- Every time you change the weight or size, you should calibrate all bias again. The more often the better, since the bias is getting calibrated with the current and last bias.

- If you are using the camera, please make sure to release it at the end of the code (I provided a function in the `CameraManager` class, which is calles `release`)

- Go to [./doc/user_server_client_fake_explaner.md](./doc/user_server_client_fake_explaner.md) to get an example usage with the `FakeR` class

- If you get into the `driveR.py` file, you will find `gyro_z` and `gyro_y`. While they are getting explained, there is still `gyro_x`, which is not in use yet. This value is for the following: If the controller is (for example) laying down and then it is on the way of standing up, then `gyro_x` changes. You will also find the `accel_x` value. `accel_y` and `accel_z` get explained, but not `accel_x`. This value (`accel_x`) is changing, when the controller is (for example) lying down and then getting moved left or right. 

- You will find in every `main.py` file which is somehow connected with communication `p_event` and `communication` parameters. You will need those parameters everywhere, where you want communication. `p_event` is the short form of "pause_event". With this parameter you are able to pause the main everytime a `high_priority` message gets sent to you. On the other hand the `communication` parameter is for reading and sending messages to the other robot. More on that in [./doc/user_server_client_fake_explaner.md](./doc/user_server_client_fake_explaner.md)

----

## License

This project is open for personal or educational use. For commercial use or redistribution, please contact the author directly. For more information, get to [./LICENSE](./LICENSE)

---

## Closing Words

Since I am the only contributor, tester and author of this library, I am sorry for every problem that might occur.  
In case there are problems that cannot be solved, feel free to contact me.  
I am very thankful and happy that you took your time using or at least considering this library.  
This way, my time did not go to waste. I wish you the greatest luck and most importantly: fun.  

---

> *"If you're willing to do what most won't, you will live like most can't"*  
> 
> - Joel Kalkusch
