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
    from timer import TimeR  # selfmade
    from threadR import KillableThread  # selfmade
    from wheelR import WheelR  # selfmade
    from light_sensor import LightSensor  # selfmade
    from digital import Digital  # selfmade
    from util import Util  # selfmade
except Exception as e:
    log(f'Import Exception {str(e)}', important=True, in_exception=True)


utility = Util()
#utility.create_port_file_entry('PORT_MOTOR_R', 'Motor', XX)  # XX is an placeholder for the integor of the motor port where the motor is plugged in. eg. 0; 2; 1; 3
#utility.create_port_file_entry('PORT_MOTOR_L', 'Motor', XX)  # XX is an placeholder for the integor of the motor port where the motor is plugged in. eg. 0; 2; 1; 3
#utility.create_port_file_entry('PORT_LIGHT_SENSOR_FRONT', 'Analog', XX)  # XX is an placeholder for the integor of the analog port where the sensor is plugged in. eg. 0; 1; 9; 4
#utility.create_port_file_entry('PORT_LIGHT_SENSOR_BACK', 'Analog', XX)  # XX is an placeholder for the integor of the analog port where the sensor is plugged in. eg. 0; 1; 9; 4
#utility.create_port_file_entry('PORT_LIGHT_SENSOR_SIDE', 'Analog', XX)  # XX is an placeholder for the integor of the analog port where the sensor is plugged in. eg. 0; 1; 9; 4
#utility.create_port_file_entry('PORT_DISTANCE_SENSOR', 'Analog', XX)  # XX is an placeholder for the integor of the analog port where the sensor is plugged in. eg. 0; 1; 9; 4
#utility.create_port_file_entry('PORT_BUTTON_BR', 'Digital', XX)  # XX is an placeholder for the integor of the digital port where the button is plugged in. eg. 0; 1; 9; 4
#utility.create_port_file_entry('PORT_BUTTON_BL', 'Digital', XX)  # XX is an placeholder for the integor of the digital port where the button is plugged in. eg. 0; 1; 9; 4
#utility.create_port_file_entry('PORT_BUTTON_FR', 'Digital', XX)  # XX is an placeholder for the integor of the digital port where the button is plugged in. eg. 0; 1; 9; 4
#utility.create_port_file_entry('PORT_BUTTON_FL', 'Digital', XX)  # XX is an placeholder for the integor of the digital port where the button is plugged in. eg. 0; 1; 9; 4
#utility.create_port_file_entry('PORT_SERVO_ARM', 'Servo', XX)  # XX is an placeholder for the integor of the servo port where the servo is plugged in. eg. 0; 2; 1; 3
#utility.create_port_file_entry('PORT_SERVO_HAND', 'Servo', XX)  # XX is an placeholder for the integor of the servo port where the servo is plugged in. eg. 0; 2; 1; 3
#print(utility.get_port_file_entries(category='Servo'), flush=True)


# ======================== VARIABLE DECLARATION =======================
# ===== PORTS ANALOG =====
#PORT_LIGHT_SENSOR_FRONT = utility.get_port_file_entries('PORT_LIGHT_SENSOR_FRONT', 'Analog')
#PORT_LIGHT_SENSOR_BACK = utility.get_port_file_entries('PORT_LIGHT_SENSOR_BACK', 'Analog')
#PORT_LIGHT_SENSOR_SIDE = utility.get_port_file_entries('PORT_LIGHT_SENSOR_SIDE', 'Analog')
#PORT_DISTANCE_SENSOR = utility.get_port_file_entries('PORT_DISTANCE_SENSOR', 'Analog')

# ===== PORTS DIGITAL =====
#PORT_BUTTON_STARTER = XX
#PORT_BUTTON_FR = utility.get_port_file_entries('PORT_BUTTON_FR', 'Digital')
#PORT_BUTTON_FL = utility.get_port_file_entries('PORT_BUTTON_FL', 'Digital')
#PORT_BUTTON_BR = utility.get_port_file_entries('PORT_BUTTON_BR', 'Digital')
#PORT_BUTTON_BL = utility.get_port_file_entries('PORT_BUTTON_BL', 'Digital')

# ===== PORTS MOTORS =====
#PORT_MOTOR_R = utility.get_port_file_entries('PORT_MOTOR_R', 'Motor')
#PORT_MOTOR_L = utility.get_port_file_entries('PORT_MOTOR_L', 'Motor')


# ======================== SETUP FUNCTIONS =======================
def Instancer_Setup():
    try:
        # ============ Ports Initializing ===========
        # ================ DIGITAL ===============
        globals()['AcceptButton'] = Digital(PORT_BUTTON_STARTER)
        globals()['Button_FR'] = Digital(PORT_BUTTON_FR)
        globals()['Button_FL'] = Digital(PORT_BUTTON_FL)
        globals()['Button_BR'] = Digital(PORT_BUTTON_BR)
        globals()['Button_BL'] = Digital(PORT_BUTTON_BL)

        # ============= DistanceSensor ===========
        globals()['DistanceSens'] = DistanceSensor(PORT_DISTANCE_SENSOR)

        # ============== LightSensor =============
        globals()['LightSensorFront'] = LightSensor('front', PORT_LIGHT_SENSOR_FRONT)  # the amount of error that you allow from the light sensor. Higher value means it is more forgiving. Integer value is required. eg: 150; 500; 300
        globals()['LightSensorBack'] = LightSensor('back', PORT_LIGHT_SENSOR_BACK)  # the amount of error that you allow from the light sensor. Higher value means it is more forgiving. Integer value is required. eg: 150; 500; 300
        globals()['LightSensorSide'] = LightSensor('side', PORT_LIGHT_SENSOR_SIDE)  # the amount of error that you allow from the light sensor. Higher value means it is more forgiving. Integer value is required. eg: 150; 500; 300

        # ================== WheelR =================
        globals()['Wheel_R'] = WheelR(PORT_MOTOR_R)
        globals()['Wheel_L'] = WheelR(PORT_MOTOR_L)


        # ================= DriveR ==================
        globals()['RubberWheeler'] = Solarbotic_Wheels_two(Instance_right_wheel=Wheel_R,
                                                   Instance_left_wheel=Wheel_L,
                                                   wheels_at_front=XX,                                      # If the wheels from the solarbotic wheels robot are located in the front (True) or back (False) half
                                                   Instance_button_front_right=Button_FR,
                                                   Instance_button_front_left=Button_FL,
                                                   Instance_button_back_right=Button_BR,
                                                   Instance_button_back_left=Button_BL,
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
    time.sleep(2)
    print('Finished with light sensor calibration. Continuing with next step...', flush=True)

# ======================== MAIN =======================
def main():
    try:
        print('uncomment to start. Do not forget to change the invalid params (like XX)', flush=True)

        # Step 0: Create the global instances
        #Instancer_Setup()  # you will need this all the time, so do not comment this line out!

        # Step 1: Basic calibrations (turning, driving straight and brightness sensors)
        #register_light_values()
        #RubberWheeler.auto_calibration(times=10)  # make sure that the robot is standing on top of a black line and is aligned in the direction of the black line

        # Step 2: Identify the orientation of the controller -> Create some space for the robot, this function will need it
        #RubberWheeler.hardware_orientation_identification()  # make sure that the robot will NOT bump into / interfere with anything -> DO NOT TOUCH IT

        # Step 3: Test how well it turns
        #RubberWheeler.turn_degrees('left', 180)

        # Step 4: Calibrate the rest (one after the other!!!)
        #RubberWheeler.calibrate_light_sensor_distance_sec()
        #RubberWheeler.calibrate_mm_per_sec()
        #RubberWheeler.calibrate_distance(XX)

        # Step 5: Try the distance calibration out
        #RubberWheeler.drive_til_distance(XXX)

    except Exception as e:
        log(f'Main Exception {str(e)}', important=True, in_exception=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log(str(e), important=True, in_exception=True)