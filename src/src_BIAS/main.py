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
    from driveR import *  # selfmade
    from light_sensor import LightSensor  # selfmade
    from digital import Digital  # selfmade
except Exception as e:
    log(f'Import Exception {str(e)}', important=True, in_exception=True)

# ======================== VARIABLE DECLARATION =======================
# ===== PORTS ANALOG =====
#PORT_LIGHT_SENSOR_FRONT = XX
#PORT_LIGHT_SENSOR_BACK = XX
#PORT_LIGHT_SENSOR_SIDE = XX
#PORT_DISTANCE_SENSOR = XX

# ===== PORTS DIGITAL =====
#PORT_BUTTON = XX

# ===== PORTS MOTORS =====
#PORT_MOTOR_FR = XX
#PORT_MOTOR_FL = XX
#PORT_MOTOR_BR = XX
#PORT_MOTOR_BL = XX

# ======================== SETUP FUNCTIONS =======================
def Instance_Setup():
    try:
        # ============ Ports Initializing ===========
        globals()['AcceptButton'] = Digital(PORT_BUTTON)

        # ============== DistanceSensor =============
        globals()['DistanceSens'] = DistanceSensor(PORT_DISTANCE_SENSOR)

        # ============== LightSensor =============
        globals()['LightSensorFront'] = LightSensor('front', PORT_LIGHT_SENSOR_FRONT, bias=XX)
        globals()['LightSensorBack'] = LightSensor('back', PORT_LIGHT_SENSOR_BACK, bias=XX)
        globals()['LightSensorSide'] = LightSensor('side', PORT_LIGHT_SENSOR_SIDE, bias=XX)

        # ================= DriveR ==================
        globals()['MechanumWheeler'] = driveR_four(Port_front_right_wheel=PORT_MOTOR_FR,
                                                   Port_front_left_wheel=PORT_MOTOR_FL,
                                                   Port_back_right_wheel=PORT_MOTOR_BR,
                                                   Port_back_left_wheel=PORT_MOTOR_BL,
                                                   controller_standing=XX,                                  # change this
                                                   Instance_light_sensor_front=LightSensorFront,
                                                   Instance_light_sensor_back=LightSensorBack,
                                                   Instance_light_sensor_side=LightSensorSide,
                                                   Instance_distance_sensor=DistanceSens)
    except Exception as e:
        log(f'Instancer Exception: {str(e)}', important=True, in_exception=True)

# ======================== CUSTOM METHODS =======================
def register_light_values():
    print('Please press the Accept button to set the value for the front AND back WHITE values and the side BLACK value ...', flush=True)
    while not AcceptButton.is_pressed():
        continue

    white_front_val = LightSensorFront.current_value()
    white_back_val = LightSensorBack.current_value()
    black_side_val = LightSensorSide.current_value()

    time.sleep(2)
    print('Please press the Accept button to set the value for the front AND back BLACK values and the side WHITE value ...', flush=True)
    while not AcceptButton.is_pressed():
        continue

    black_front_val = LightSensorFront.current_value()
    black_back_val = LightSensorBack.current_value()
    white_side_val = LightSensorSide.current_value()

    black_back_val = LightSensorBack.current_value()
    LightSensorFront.save_value_white(white_front_val)  # saving the value into the file
    LightSensorFront.save_value_black(black_front_val)  # saving the value into the file
    LightSensorBack.save_value_white(white_back_val)  # saving the value into the file
    LightSensorBack.save_value_black(black_back_val)  # saving the value into the file
    LightSensorSide.save_value_white(white_side_val)  # saving the value into the file
    LightSensorSide.save_value_black(black_side_val)  # saving the value into the file

    time.sleep(2)
    print('Please press the Accept button to go on to the next step', flush=True)
    while not AcceptButton.is_pressed():
        continue

# ======================== MAIN =======================
def main():
    try:
        print('uncomment to start. Do not forget to change the invalid params (like XX)', flush=True)
        #Instance_Setup()
        #register_light_values()
        #MechanumWheeler.auto_calibration(times=10, on_line=XX)

    except Exception as e:
        log(f'Main Exception {str(e)}', important=True, in_exception=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log(str(e), important=True, in_exception=True)