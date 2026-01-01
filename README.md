# Robot Utility & Communication Toolkit

**Author:** Joel Kalkusch  
**Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)  
**Nationality**: Austrian (Österreich)  
**Date of Creation**: 2025-09-07

---

## Getting Started

If this is your first time using the project, please read the [Introduction](./doc/Introduction.md). 
It will walk you through the basics of setting up and understanding the core concepts of BotBall.

---

## Overview

This repository provides a set of utility classes and communication tools designed for robotics projects using the KIPR framework. It covers:

- Sensor interaction (`Digital`, `DistanceSensor`, `LightSensor`)

- Robot driving (`base_driver`, `Solarbotic_Wheels_two`, `Mechanum_Wheels_four`, `MOTOR_SCHEDULER`, `WheelR`)

- Servo / micro-servo usage (`ServoX`, `SERVO_SCHEDULER`)

- Camera detection (`CameraObjectDetector`, `CameraBrightnessDetector`, `CameraManager`)

- Robot communication (`RobotCommunicator`, `WifiConnector`)

- File management and logging (`FileR`, `logger`)

- Simulation utilities (`FakeR`, `PausR`)

- High-level utility functions (`Util`)

- Stopping activity that runs on new main execution(`stop_manager`)

These components simplify programming robots by providing structured interfaces, callback systems, and comprehensive handling of sensors and messaging.

---

## Contents

The repository is organized as follows:

- **Classes for Sensor Handling:**
  
  - `Digital` – Digital buttons
  
  - `Analog` - Analog sensors 
  
  - `DistanceSensor` – Analog distance sensor

  - `LightSensor` – Analog light sensor
- **Movement Classes:**
  - `WheelR` - functionality for wheels
  - `Solarbotic_Wheels_two` – Two-motor drive system using rubber / solarbotic wheels
  - `Mecanum_Wheels_four` – Four-motor drive system
  - `MOTOR_SCHEDULER` - Schedules which motor function should be executed
  - `ServoX` - Servo / micro-servo controlling
  - `SERVO_SCHEDULER` -  Schedules which servo function should be executed

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
  - `stop_manager` - Stops certain activity
  - `PausR` - optional execution of a function when using communication 
- **Documentation:**
  - Detailed explanations are included for each class in the [./doc/explainer](./doc/explainer)` folder.

---

## Documentation - Codes

Detailed explanations of the classes are included in the repository:

- [wifi.md](./doc/explainer/wifi.md) – Full explanation and usage guide for the `WifiConnector` class

- [digital.md](./doc/explainer/digital.md) – Full explanation and usage guide for the `Digital` class

- [distance_sensor.md](./doc/explainer/distance_sensor.md) – Full explanation and usage guide for the `DistanceSensor` class

- [driveR.md](./doc/explainer/driveR.md) – Full explanation and usage guide for the `Solarbotic_Wheels_two` and `Mecanum_Wheels_four` classes

- [fake.md](./doc/explainer/fake.md) – Full explanation and usage guide for the `FakeR` class

- [fileR.md](./doc/explainer/fileR.md) – Full explanation and usage guide for the `FileR` class

- [light_sensor.md](./doc/explainer/light_sensor.md) – Full explanation and usage guide for the `LightSensor` class

- [logger.md](./doc/explainer/logger.md) – Full explanation and usage guide for the `logger` file

- [RoboComm.md](./doc/explainer/RoboComm.md) – Full explanation and usage guide for the `RobotCommunicator` class

- [util.md](./doc/explainer/util.md) – Full explanation and usage guide for the `Util` class

- [servo.md](./doc/explainer/servo.md) - Full explanation and usage guide for the `ServoX` class

- [brightness_detector.md](./doc/explainer/brightness_detector.md) - Full explanation and usage guide for the `CameraBrightnessDetector` class

- [object_detector.md](./doc/explainer/object_detector.md) - Full explanation and usage guide for the `CameraObjectDetector` class

- [camera_manager.md](./doc/explainer/camera_manager.md) - Full explanation and usage guide for the `CameraManager` class

- [stop_manager.md](./doc/explainer/stop_manager.md) - Full explanation and usage guide for the `stop_manager` functions

- [pausR.md](./doc/explainer/pausR.md) - Full explanation and usage guide for the `PausR` class

- [motor_scheduler.md](./doc/explainer/motor_scheduler.md) - Full explanation and usage guide for the `MotorScheduler` class

- [servo_scheduler.md](./doc/explainer/servo_scheduler.md) - Full explanation and usage guide for the `ServoScheduler` class

---

## Installation

1. Clone the repository onto an USB-stick:

```bash
git clone https://github.com/J0K3R-Joel/BotBall_Library.git
```

2. Copy the repository to an USB-stick.

3. Go in [./src/WIFI_FOR_INSTALLATION/main.py](./src/WIFI_FOR_INSTALLATION/main.py) and change the SSID and PASS inside the `wifi_setup()` to a wifi that grants you internet access, so libraries can get installed 

4. Go in [./LOCAL_STD_WIFI.conf](./LOCAL_STD_WIFI.conf) and type in the SSID and password of your local router. The local router should be a private router you got from home, so no one can intercept the communication. Internet access is NOT required. 
   **HINT**: every space, every character and everything after the "=" counts as either the SSID or password (depends on the line you are writing in), so be aware of spaces and other characters you fill in.

5. Go to the [KIPR Wombat firmware](https://www.kipr.org/kipr/hardware-software/kipr-wombat-firmware) page

6. Download the latest "KIPR Wombat OS Image" (scroll down!).

7. Flash the image onto the robot following the instructions on the KIPR website. Use a software like [Raspberry Pi Imager](https://www.raspberrypi.com/software) for flashing the image file onto the micro SD card of the controller (You need to unscrew the "shell" of the controller to get to the micro SD card)

8. Once the robot is flashed and ready, insert the USB stick.

9. Navigate to the path of the USB stick on the robot.

10. Run the configuration script:

```bash
sudo bash config.sh
```

11. The installation is complete. You can check the log file in "**/usr/lib/logger_log/log_file.txt**". This will get edited all the time.

---

## Usage

Example usage for most classes is provided in the documentation files linked above.

Additionally, an example usage for the `FakeR` class (most complex class) is provided in [./doc/explainer/user_server_client_fake.md](./doc/explainer/user_server_client_fake.md) file, since this will be the best exercise (for some more experienced use), if you do not have experience with this library. This got two new users (one for as a client, the other as the server)

Other classes that got an entire user as test purpose:

- `Camera` -> `CameraManager`, `CameraObjectDetector`, `CameraBrightnessDetector`

- `WIFI` -> `WifiConnector` 

- `BIAS` -> everything that needs some way of calibration or stuff that calibration needs

- `COMM` -> `RobotCommunicator` 

- `Fake-Client` & `Fake-Server` -> `FakeR`, `stop_manager`, `RobotCommunicator`,...

---

## Additional Information

- Go to [./doc/explainer/user_server_client_fake.md](./doc/explainer/user_server_client_fake.md) to get an example usage with the `FakeR` class
- Check out [./doc/Sensors.md](./doc/Sensors.md) for every sensor description
- Check out [./doc/Considerations.md](./doc/Considerations.md) for every (more) detailed information and good-to-knows
- Check out [./doc/Common_Issues.md](./doc/Common_Issues.md) for the solutions of common issues that might occur
- If you are using my library, then you need to calibrate the robot. Check out [./doc/Calibrations.md](./doc/Calibrations.md) for further information
- `driveR` is very dependent on the right placement of the sensors, which you can find in [./Standard_Construction.md](./Standard_Construction.md). Make sure everything is positioned correctly
- I will talk very often about "rubber wheels", what I mean by that are the "Solarbotic" wheels (including the caster ball).
- Many classes have a `R` in the end of the name, this is solely for fun / so it sounds a little bit better. It does not really have any meaning whatsoever 
- Read my documentations, this will help you out a lot. I tried to document everything, use it. Other Teams do NOT have this!

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
