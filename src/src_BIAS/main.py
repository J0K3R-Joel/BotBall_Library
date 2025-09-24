#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-09-24

try:
    from driveR import *
    from light_sensor import LightSensor  # selfmade
    from digital import Digital  # selfmade
except Exception as e:
    log(f'Import Exception {str(e)}', important=True, in_exception=True)

# ======================== VARIABLE DECLARATION =======================
# ===== PORTS ANALOG =====
#PORT_LIGHT_SENSOR_FRONT = XX
#PORT_LIGHT_SENSOR_BACK = XX

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
        globals()['LightSensorFront'] = LightSensor(position='front', PORT_LIGHT_SENSOR_FRONT, bias=500)
        globals()['LightSensorBack'] = LightSensor(position='back', PORT_LIGHT_SENSOR_BACK, bias=500)

        # ================= DriveR ==================
        globals()['MechanumWheeler'] = driveR_four(Port_front_right_wheel=PORT_MOTOR_FR,
                                                   Port_front_left_wheel=PORT_MOTOR_FL,
                                                   Port_back_right_wheel=PORT_MOTOR_BR,
                                                   Port_back_left_wheel=PORT_MOTOR_BL,
                                                   controller_standing=XX,                                  # change this
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

    print('Please press the Accept button to set the value for the front AND back BLACK values ...', flush=True)
    while not AcceptButton.is_pressed():
        continue

    black_front_val = LightSensorFront.current_value()
    black_back_val = LightSensorBack.current_value()

    LightSensorFront.save_value_white(white_front_val)  # saving the value into the file
    LightSensorFront.save_value_black(black_front_val)  # saving the value into the file
    LightSensorBack.save_value_white(white_back_val)  # saving the value into the file
    LightSensorBack.save_value_black(black_back_val)  # saving the value into the file

# ======================== MAIN =======================
def main():
    try:
        print('uncomment to start. Do not forget to change the invalid params (like XX)', flush=True)
        #Instancer_Setup()
        #register_light_values()
        #MechanumWheeler.auto_calibration(times=50, on_line=XX)

