#!/usr/bin/python3
import os, sys
from typing import Set

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
    from servo import ServoX
    from util import Util  # selfmade
except Exception as e:
    log(f'Import Exception {str(e)}', important=True, in_exception=True)

utility = Util()
# utility.create_port_file_entry('PORT_MOTOR_R', 'Motor', 0)  # XX is an placeholder for the integor of the motor port where the motor is plugged in. eg. 0; 2; 1; 3
# utility.create_port_file_entry('PORT_MOTOR_L', 'Motor', 1)  # XX is an placeholder for the integor of the motor port where the motor is plugged in. eg. 0; 2; 1; 3
# utility.create_port_file_entry('PORT_MOTOR_HAND', 'Motor', 2)
# utility.create_port_file_entry('PORT_MOTOR_HANB', 'Motor', 3)

# utility.create_port_file_entry('PORT_LIGHT_SENSOR_FRONT', 'Analog', 4)  # XX is an placeholder for the integor of the analog port where the sensor is plugged in. eg. 0; 1; 9; 4
# utility.create_port_file_entry('PORT_LIGHT_SENSOR_BACK', 'Analog', 5)  # XX is an placeholder for the integor of the analog port where the sensor is plugged in. eg. 0; 1; 9; 4
# utility.create_port_file_entry('PORT_LIGHT_SENSOR_SIDE', 'Analog', 3)  # XX is an placeholder for the integor of the analog port where the sensor is plugged in. eg. 0; 1; 9; 4
# utility.create_port_file_entry('PORT_DISTANCE_SENSOR', 'Analog', XX)  # XX is an placeholder for the integor of the analog port where the sensor is plugged in. eg. 0; 1; 9; 4
# utility.create_port_file_entry('PORT_LIGHT_SENSOR_START', 'Analog', 2)  # XX is an placeholder for the integor of t

# utility.create_port_file_entry('PORT_BUTTON_BR', 'Digital', 1)  # XX is an placeholder for the integor of the digital port where the button is plugged in. eg. 0; 1; 9; 4
# utility.create_port_file_entry('PORT_BUTTON_BL', 'Digital', 0)  # XX is an placeholder for the integor of the digital port where the button is plugged in. eg. 0; 1; 9; 4
# utility.create_port_file_entry('PORT_BUTTON_FR', 'Digital', 2)  # XX is an placeholder for the integor of the digital port where the button is plugged in. eg. 0; 1; 9; 4
# utility.create_port_file_entry('PORT_BUTTON_FL', 'Digital', 3)  # XX is an placeholder for the integor of the digital port where the button is plugged in. eg. 0; 1; 9; 4

# utility.create_port_file_entry('PORT_SERVO_ARM', 'Servo', 0)  # XX is an placeholder for the integor of the servo port where the servo is plugged in. eg. 0; 2; 1; 3
# utility.create_port_file_entry('PORT_MICRO_SERVO_R', 'Servo', 2)  # XX is an placeholder for the integor of the servo port where the servo is plugged in. eg. 0; 2; 1; 3
# utility.create_port_file_entry('PORT_MICRO_SERVO_L', 'Servo', 1)
# print(utility.get_port_file_entries(category='Servo'), flush=True)


# ======================== VARIABLE DECLARATION =======================
# ===== PORTS ANALOG =====
PORT_LIGHT_SENSOR_FRONT = utility.get_port_file_entries('PORT_LIGHT_SENSOR_FRONT', 'Analog')
PORT_LIGHT_SENSOR_BACK = utility.get_port_file_entries('PORT_LIGHT_SENSOR_BACK', 'Analog')
PORT_LIGHT_SENSOR_SIDE = utility.get_port_file_entries('PORT_LIGHT_SENSOR_SIDE', 'Analog')
PORT_LIGHT_SENSOR_START = utility.get_port_file_entries('PORT_LIGHT_SENSOR_START', 'Analog')

# ===== PORTS DIGITAL =====
PORT_BUTTON_STARTER = 9
PORT_BUTTON_FR = utility.get_port_file_entries('PORT_BUTTON_FR', 'Digital')
PORT_BUTTON_FL = utility.get_port_file_entries('PORT_BUTTON_FL', 'Digital')
PORT_BUTTON_BR = utility.get_port_file_entries('PORT_BUTTON_BR', 'Digital')
PORT_BUTTON_BL = utility.get_port_file_entries('PORT_BUTTON_BL', 'Digital')

# ===== PORTS MOTORS =====
PORT_MOTOR_R = utility.get_port_file_entries('PORT_MOTOR_R', 'Motor')
PORT_MOTOR_L = utility.get_port_file_entries('PORT_MOTOR_L', 'Motor')
PORT_MOTOR_HAND = utility.get_port_file_entries('PORT_MOTOR_HAND', 'Motor')
PORT_MOTOR_HANB = utility.get_port_file_entries('PORT_MOTOR_HANB', 'Motor')

# ===== PORTS Servos =====
PORT_MICRO_SERVO_R = utility.get_port_file_entries('PORT_MICRO_SERVO_R', 'Servo')
PORT_MICRO_SERVO_L = utility.get_port_file_entries('PORT_MICRO_SERVO_L', 'Servo')
PORT_SERVO_ARM = utility.get_port_file_entries('PORT_SERVO_ARM', 'Servo')


# ======================== SETUP FUNCTIONS =======================
def Instancer_Setup():
    try:
        # ============ Ports Initializing ===========
        # ================ DIGITAL ===============
        globals()['AcceptButton'] = Digital(PORT_BUTTON_STARTER)
        globals()['Button_BR'] = Digital(PORT_BUTTON_BR)
        globals()['Button_BL'] = Digital(PORT_BUTTON_BL)
        globals()['Button_FR'] = Digital(PORT_BUTTON_FR)
        globals()['Button_FL'] = Digital(PORT_BUTTON_FL)

        # ============== LightSensor =============
        globals()['LightSensorFront'] = LightSensor('front',
                                                    PORT_LIGHT_SENSOR_FRONT)  # the amount of error that you allow from the light sensor. Higher value means it is more forgiving. Integer value is required. eg: 150; 500; 300
        globals()['LightSensorBack'] = LightSensor('back',
                                                   PORT_LIGHT_SENSOR_BACK)  # the amount of error that you allow from the light sensor. Higher value means it is more forgiving. Integer value is required. eg: 150; 500; 300
        globals()['LightSensorSide'] = LightSensor('side',
                                                   PORT_LIGHT_SENSOR_SIDE)  # the amount of error that you allow from the light sensor. Higher value means it is more forgiving. Integer value is required. eg: 150; 500; 300
        globals()['LightSensorStart'] = LightSensor('start', PORT_LIGHT_SENSOR_START)
        # ================== WheelR =================
        globals()['Wheel_R'] = WheelR(PORT_MOTOR_R)
        globals()['Wheel_L'] = WheelR(PORT_MOTOR_L)
        globals()['Wheel_Hand'] = WheelR(PORT_MOTOR_HAND)
        globals()['Wheel_Hanb'] = WheelR(PORT_MOTOR_HANB)

        # ================= ServoX ==================
        globals()['Micro_R'] = ServoX(PORT_MICRO_SERVO_R)
        globals()['Micro_L'] = ServoX(PORT_MICRO_SERVO_L)
        globals()['Servo_Arm'] = ServoX(PORT_SERVO_ARM)

        # ================= DriveR ==================
        globals()['RubberWheeler'] = Solarbotic_Wheels_two(Instance_right_wheel=Wheel_R,
                                                           Instance_left_wheel=Wheel_L,
                                                           wheels_at_front=True,
                                                           Instance_button_front_right=Button_FR,
                                                           Instance_button_front_left=Button_FL,
                                                           Instance_button_back_right=Button_BR,
                                                           Instance_button_back_left=Button_BL,
                                                           Instance_light_sensor_back=LightSensorBack,
                                                           Instance_light_sensor_front=LightSensorFront,
                                                           Instance_light_sensor_side=LightSensorSide)

        globals()['Motor_Hand'] = Solarbotic_Wheels_two(Instance_right_wheel=Wheel_Hand,
                                                        Instance_left_wheel=Wheel_Hanb,
                                                        wheels_at_front=True,
                                                        Instance_button_front_right=Button_FR,
                                                        Instance_button_front_left=Button_FL,
                                                        Instance_button_back_right=Button_BR,
                                                        Instance_button_back_left=Button_BL,
                                                        Instance_light_sensor_back=LightSensorBack,
                                                        Instance_light_sensor_front=LightSensorFront,
                                                        Instance_light_sensor_side=LightSensorSide)


    except Exception as e:
        log(f'Instancer Exception: {str(e)}', important=True, in_exception=True)


# ======================== CUSTOM METHODS =======================
def register_light_values():
    print(
        'Please press the Accept button to set the value for the front AND back WHITE values and the side BLACK value ...',
        flush=True)
    while not AcceptButton.is_pressed():
        continue

    white_front_val = LightSensorFront.current_value()
    white_back_val = LightSensorBack.current_value()
    black_side_val = LightSensorSide.current_value()

    time.sleep(2)
    print(
        'Please press the Accept button to set the value for the front AND back BLACK values and the side WHITE value ...',
        flush=True)
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


# ======================CUSTOM METHODS=======================
def set_servos_start_pos():
    Servo_Arm.set_pos(560)
    Micro_R.set_pos(1070)
    Micro_L.set_pos(1450)


# ======================== MAIN =======================
def main():
    try:

        Instancer_Setup()
        # register_light_values()

        # 1280 close side micro 980 open R
        # 1700 open main, 970 close L port 1

        k.wait_for_light(PORT_LIGHT_SENSOR_START)
        k.shut_down_in(119)

        time.sleep(15)
        # open claws and lower arm
        Servo_Arm.set_pos(700)  # lower arm to a mid position before opening

        # open micro
        Micro_R.set_pos(200)
        Micro_L.set_pos(1600)
        Servo_Arm.set_pos(1900)

        # drive to collect poms
        RubberWheeler.drive_straight(7000, 1300)
        RubberWheeler.drive_straight(3000)
        Servo_Arm.set_pos(600)
        Servo_Arm.set_pos(1000)
        Servo_Arm.set_pos(600)

        RubberWheeler.turn_degrees('right', 75)
        Servo_Arm.set_pos(800)

        Micro_R.set_pos(830)
        Micro_L.set_pos(1060)

        Motor_Hand.drive_straight(700)
        Motor_Hand.drive_straight(700, -1400)
        Motor_Hand.drive_straight(700)
        Motor_Hand.drive_straight(700, -1400)

        RubberWheeler.drive_straight(1000)
        RubberWheeler.turn_degrees('right', 40)
        RubberWheeler.drive_straight(1500)
        RubberWheeler.turn_degrees('right', 70)

        # drive towars short tubes and align
        RubberWheeler.drive_straight(1500, -1400)
        RubberWheeler.drive_straight(4000)
        RubberWheeler.turn_degrees(40)

        # turn towars long tubes and align

        # drive towards baskets to pull left one out
        # 90deg
        # RubberWheeler.drive_straight(5000, 1000)

        # pull baskets out
        # RubberWheeler.drive_straight(1000,-1000) #until buttons on the back touch pipes

        # Step 1: Register the light values for the front, back and side brightness sensor to know when it should see black / white
        # HINT: If you mess up once, you should rather execute the next function ("register_light_values") 5 times
        # register_light_values()

        # Step 2: Look at how off the IMU is, so that you are able to turn and drive in a line
        # HINT: Place the robot on top of a black line (brightness sensor front and brightness sensor back need to see black!)
        # HINT: DO NOT TOUCH THE ROBOT WHILE THE PROGRAM EXECUTES
        # RubberWheeler.auto_calibration(times=5)

        # Step 3: Test how well it turns
        # HINT: If it does not turn well, then either try "RubberWheeler.calibrate_degrees()" (-> align the robot on a black line again) or calibrate your light sensors again (Step 1) and afterwards Step 2 (or "RubberWheeler.calibrate_degrees()")
        # HINT: If the robot does not turn well, there is no need to execute any other function, except the said ones
        # RubberWheeler.turn_degrees('left', 180)

        # Step 4: Identify how you need to adjust based on the controller position (e.g.: driving forward)
        # HINT: You can place the robot on the floor to have more space
        # HINT: Make sure that the robot will NOT bump into / interfere with anything -> DO NOT TOUCH IT
        # RubberWheeler.threshold_identification()

        # Step 5: Identify how much you need to adjust / counter-steer to drive in a line
        # HINT: You can place the robot on the floor
        # HINT: Make sure that the robot will NOT bump into / interfere with anything -> DO NOT TOUCH IT
        # RubberWheeler.adjuster_identification()

        # Step 6: Calibrate the distance between front and back brightness sensor
        # HINT: The robot needs to face a black line, it will drive forward until the front (and back) brightness sensor(s) detect a black line
        # HINT: Align the robot as good as possible parallel a black line, facing the black line
        # RubberWheeler.calibrate_light_sensor_distance_sec()

        # Step 7: Calibrate the time it takes the robot to drive for some time (default: 5000 milliseconds)
        # RubberWheeler.calibrate_mm_per_sec()

        # Step 8: Calibrate the ET distance sensor corresponding to the wheels
        # RubberWheeler.calibrate_distance(XX)

        # Step 9: Try the distance calibration out
        # RubberWheeler.drive_til_distance(XXX)

    except Exception as e:
        log(f'Main Exception {str(e)}', important=True, in_exception=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log(str(e), important=True, in_exception=True)