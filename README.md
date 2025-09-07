# Robot Utility & Communication Toolkit

**Author:** Joel Kalkusch  
**Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)  
**Date of Creation:** 2025-09-07

---

## Overview

This repository provides a set of utility classes and communication tools designed for robotics projects using the KIPR framework. It covers:

- Sensor interaction (`Digital`, `DistanceSensor`, `LightSensor`)

- Robot driving (`driveR_two`, `driveR_four`)

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

- **Driving Classes:**
  
  - `driveR_two` – Two-motor drive system
  
  - `driveR_four` – Four-motor drive system

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

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/robot-utility.git
```

2. Copy the repository to a USB stick.

3. Go to the [KIPR Wombat firmware](https://www.kipr.org/kipr/hardware-software/kipr-wombat-firmware) page

4. Download the latest image.

5. Flash the image onto the robot following the instructions on the KIPR website.

6. Once the robot is flashed and ready, insert the USB stick.

7. Navigate to the path of the USB stick on the robot.

8. Run the configuration script:

```bash
sudo bash config.sh
```

9. The installation is complete.

---

## Usage

Example usage for most classes is provided in the documentation files linked above.

---

## License

This project is open for personal or educational use. For commercial use or redistribution, please contact the author directly.
