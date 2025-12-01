#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-09-24

try:
    import time
    from wheelR import WheelR  # selfmade
    from driveR import *  # selfmade
    from light_sensor import LightSensor  # selfmade
    from digital import Digital  # selfmade
except Exception as e:
    log(f'Import Exception {str(e)}', important=True, in_exception=True)

# ======================== VARIABLE DECLARATION =======================
# ===== PORTS ANALOG =====
PORT_LIGHT_SENSOR_FRONT = 2
PORT_LIGHT_SENSOR_BACK = 0
PORT_DISTANCE_SENSOR = 1

# ===== PORTS DIGITAL =====
PORT_BUTTON = 9

# ===== PORTS MOTORS =====
PORT_MOTOR_R = 0
PORT_MOTOR_L = 1

# ======================== SETUP FUNCTIONS =======================
def Instance_Setup():
    try:
        # ============ Ports Initializing ===========
        globals()['AcceptButton'] = Digital(PORT_BUTTON)

        # ============== DistanceSensor =============
        globals()['DistanceSens'] = DistanceSensor(PORT_DISTANCE_SENSOR)

        # ============== LightSensor =============
        globals()['LightSensorFront'] = LightSensor('front', PORT_LIGHT_SENSOR_FRONT, bias=150)
        globals()['LightSensorBack'] = LightSensor('back', PORT_LIGHT_SENSOR_BACK, bias=150)

        # ================== WheelR =================
        globals()['Wheel_R'] = WheelR(PORT_MOTOR_R)
        globals()['Wheel_L'] = WheelR(PORT_MOTOR_L)

        # ================= DriveR ==================
        globals()['RubberWheeler'] = Rubber_Wheels_two(Instance_right_wheel=Wheel_R,
                                                Instance_left_wheel=Wheel_L,
                                                False,
                                                Instance_distance_sensor=DistanceSens,
                                                Instance_light_sensor_front=LightSensorFront,
                                                Instance_light_sensor_back=LightSensorBack)
    except Exception as e:
        log(f'Instancer Exception: {str(e)}', important=True, in_exception=True)

# ======================== CUSTOM METHODS =======================
def register_light_values():
    print('Please press the Accept button to set the value for the front AND back WHITE values ...', flush=True)
    while not AcceptButton.is_pressed():
        continue

    white_front_val = LightSensorFront.current_value()
    white_back_val = LightSensorBack.current_value()

    time.sleep(2)
    print('Please press the Accept button to set the value for the front AND back BLACK values ...', flush=True)
    while not AcceptButton.is_pressed():
        continue

    black_front_val = LightSensorFront.current_value()
    black_back_val = LightSensorBack.current_value()

    LightSensorFront.save_value_white(white_front_val)  # saving the value into the file
    LightSensorFront.save_value_black(black_front_val)  # saving the value into the file
    LightSensorBack.save_value_white(white_back_val)  # saving the value into the file
    LightSensorBack.save_value_black(black_back_val)  # saving the value into the file

    time.sleep(2)
    print('Please press the Accept button to go on to the next step', flush=True)
    while not AcceptButton.is_pressed():
        continue
    print('Finished with light sensor calibration. Continuing with next step...', flush=True)

# ======================== MAIN =======================
def main():
    try:
        Instance_Setup()
        register_light_values()
        RubberWheeler.auto_calibration(times=10)

    except Exception as e:
        log(f'Main Exception {str(e)}', important=True, in_exception=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log(str(e), important=True, in_exception=True)