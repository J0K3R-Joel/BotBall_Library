# Classes for usage

This file tells you, which files and therefor which classes are for the regular user and which for the advanced ones. 

## Basic User

Non-advanced users should only use the following files:

- `analog.py` - Analog
- `brightness_detector.py` - CameraBrightnessDetector
- `camera_manager.py` - CameraManager
- `wifi.py` - WifiConnector
- `digital.py` - Digital
- `distance_sensor.py` - DistanceSensor
- `driveR.py` - Rubber_Wheels_two, Mecanum_Wheels_four, base_driver
- `fileR.py` - FileR
- `light_sensor.py` - LightSensor
- `logger.py`
- `object_detector.py` - CameraObjectDetector
- `RoboComm.py` - RobotCommunicator
- `servo.py` - ServoX
- `util.py` - Util
- `wheelR.py` - WheelR
- (`ideas.py` -> not really for execution, but to get some ideas / add some ideas)
- (`main.py` -> obviously, since you need to write in here)

## Advanced User

Only the advanced user should use the following files and should be allowed to edit them. They work in the background without anyone having to do anything / anyone noticing anything from them:  

- `motor_scheduler.py` - MotorScheduler / MOTOR_SCHEDULER
- `servo_scheduler.py` - ServoScheduler / SERVO_SCHEDULER
- `stop_manager.py` - stop_manager
- `fake.py` - FakeR
- `pausR.py` - PausR