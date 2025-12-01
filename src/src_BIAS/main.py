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
    from wheelR import WheelR  # selfmade
    from light_sensor import LightSensor  # selfmade
    from digital import Digital  # selfmade
except Exception as e:
    log(f'Import Exception {str(e)}', important=True, in_exception=True)

# ======================== VARIABLE DECLARATION =======================
# ===== PORTS ANALOG =====
#PORT_LIGHT_SENSOR_FRONT = XX  # XX is an placeholder for the integor of the analog port where the sensor is plugged in. eg. 0; 1; 9; 4
#PORT_LIGHT_SENSOR_BACK = XX  # XX is an placeholder for the integor of the analog port where the sensor is plugged in. eg. 0; 1; 9; 4
#PORT_LIGHT_SENSOR_SIDE = XX  # XX is an placeholder for the integor of the analog port where the sensor is plugged in. eg. 0; 1; 9; 4
#PORT_DISTANCE_SENSOR = XX  # XX is an placeholder for the integor of the analog port where the sensor is plugged in. eg. 0; 1; 9; 4

# ===== PORTS DIGITAL =====
#PORT_BUTTON = XX  # XX is an placeholder for the integor of the digital port where the button is plugged in. eg. 0; 1; 9; 4

# ===== PORTS MOTORS =====
#PORT_MOTOR_R = XX  # XX is an placeholder for the integor of the motor port where the motor is plugged in. eg. 0; 2; 1; 3
#PORT_MOTOR_L = XX  # XX is an placeholder for the integor of the motor port where the motor is plugged in. eg. 0; 2; 1; 3


# ======================== SETUP FUNCTIONS =======================
def Instance_Setup():
    try:
        # ============ Ports Initializing ===========
        globals()['AcceptButton'] = Digital(PORT_BUTTON)

        # ============== DistanceSensor =============
        globals()['DistanceSens'] = DistanceSensor(PORT_DISTANCE_SENSOR)

        # ============== LightSensor =============
        globals()['LightSensorFront'] = LightSensor('front', PORT_LIGHT_SENSOR_FRONT, bias=XX)  # the amount of error that you allow from the light sensor. Higher value means it is more forgiving. Integer value is required. eg: 150; 500; 300
        globals()['LightSensorBack'] = LightSensor('back', PORT_LIGHT_SENSOR_BACK, bias=XX)  # the amount of error that you allow from the light sensor. Higher value means it is more forgiving. Integer value is required. eg: 150; 500; 300
        globals()['LightSensorSide'] = LightSensor('side', PORT_LIGHT_SENSOR_SIDE, bias=XX)  # the amount of error that you allow from the light sensor. Higher value means it is more forgiving. Integer value is required. eg: 150; 500; 300

        # ================== WheelR =================
        globals()['Wheel_R'] = WheelR(PORT_MOTOR_R)
        globals()['Wheel_L'] = WheelR(PORT_MOTOR_L)


        # ================= DriveR ==================
        globals()['RubberWheeler'] = Rubber_Wheels_two(Instance_right_wheel=Wheel_R,
                                                   Instance_left_wheel=Wheel_L,
                                                   controller_standing=XX,                                  # If the controller is standing up-right (True) or if it is laying flat on the surface of the chassis bracket (False)
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
    print('Finished with light sensor calibration. Continuing with next step...', flush=True)

# ======================== MAIN =======================
def main():
    try:
        print('uncomment to start. Do not forget to change the invalid params (like XX)', flush=True)
        #Instance_Setup()
        #register_light_values()
        #RubberWheeler.auto_calibration(times=10)  # make sure that the robot is standing on top of a black line and is aligned in the direction of the black line

    except Exception as e:
        log(f'Main Exception {str(e)}', important=True, in_exception=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log(str(e), important=True, in_exception=True)