#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-07-28

try:
    import _kipr as k
    import time
    import threading
    import subprocess
    from commU import WifiConnector  # selfmade
    from RoboComm import RobotCommunicator  # selfmade
    from util import Util  # selfmade
    from distance_sensor import DistanceSensor  # selfmade
    from light_sensor import LightSensor  # selfmade
    from digital import Digital  # selfmade
    from fileR import FileR  # selfmade
    from fake import FakeR  # selfmade
    from driveR import *  # selfmade
    from servo import ServoX  # selfmade
    from camera_manager import CameraManager  # selfmade
    from brightness_detector import CameraBrightnessDetector  # selfmade
    from object_detector import CameraObjectDetector  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


# ======================== VARIABLE DECLARATION =======================
# ===== GLOBAL VARIABLES =====

# ===== PORTS ANALOG =====
PORT_ANALOG_HELLIGKEIT_H = 0
PORT_ANALOG_DISTANZ = 1
PORT_ANALOG_HELLIGKEIT_V = 2

# ===== PORTS DIGITAL =====
PORT_KNOPF_VR = 0
PORT_KNOPF_HR = 1
PORT_KNOPF_VL = 2
PORT_KNOPF_HL = 3

# ===== PORTS MOTORS =====
PORT_MOTOR_R = 0
PORT_MOTOR_L = 1

# ===== PORTS SERVOS =====
PORT_SERVO_ARM = 0
PORT_SERVO_HAND = 1


# ======================== SETUP FUNCTIONS =======================
def Instancer_Setup():
    try:
        # ============ Ports Initializing ===========
        # ================= Digital =================
        globals()['Knopf_VR'] = Digital(PORT_KNOPF_VR)
        globals()['Knopf_VL'] = Digital(PORT_KNOPF_VL)
        globals()['Knopf_HL'] = Digital(PORT_KNOPF_HL)
        globals()['Knopf_HR'] = Digital(PORT_KNOPF_HR)

        # ================= ServoX ==================
        globals()['Servo_Arm'] = ServoX(PORT_SERVO_ARM)
        globals()['Servo_Hand'] = ServoX(PORT_SERVO_HAND)
    
        # ============== DistanceSensor =============
        globals()['Distanz'] = DistanceSensor(PORT_ANALOG_DISTANZ)

        # =============== LightSensor ===============
        globals()['Helligkeit_V'] = LightSensor('front', PORT_ANALOG_HELLIGKEIT_V, bias=150)
        globals()['Helligkeit_H'] = LightSensor('back', PORT_ANALOG_HELLIGKEIT_H, bias=150)


        # ================= DriveR ==================
        globals()['Fahrzeug'] = driveR_two(PORT_MOTOR_R,
                                           PORT_MOTOR_L,
                                           False,
                                           Instance_distance_sensor=Distanz,
                                           Instance_light_sensor_front=Helligkeit_V,
                                           Instance_light_sensor_back=Helligkeit_H,
                                           Instance_button_front_right=Knopf_VR,
                                           Instance_button_front_left=Knopf_VL,
                                           Instance_button_back_right=Knopf_HR,
                                           Instance_button_back_left=Knopf_HL)
        
    except Exception as e:
        log(f'Instancer Exception: {str(e)}', important=True, in_exception=True)


def setup():
    try:
        Instancer_Setup()
    except Exception as e:
        log(f'Setup Exception: {str(e)}', important=True, in_exception=True)

# ======================== CUSTOM METHODS =======================



# ======================== MAIN =======================

def main():
    try:
        setup()
        print(Knopf_VL.is_pressed(), flush=True)
        log('Es funktioniert!')
        Fahrzeug.drive_straight(500)
        time.sleep(1.5)
        Fahrzeug.drive_straight(500, -1400)

    except Exception as e:
        log(f'Main Exception: {str(e)}', important=True, in_exception=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(str(e), important=True, in_exception=True)