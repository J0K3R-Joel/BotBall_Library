#!/usr/bin/python3
import multiprocessing
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
    import threading, multiprocessing
    import subprocess
    from timer import TimeR  # selfmade
    from threadR import KillableThread  # selfmade
    from wheelR import WheelR  # selfmade
    from wifi import WifiConnector  # selfmade
    from RoboComm import RobotCommunicator  # selfmade
    from util import Util  # selfmade
    from distance_sensor import DistanceSensor  # selfmade
    from light_sensor import LightSensor  # selfmade
    from digital import Digital  # selfmade
    from fileR import FileR  # selfmade
    # from fake import FakeR  # selfmade
    from driveR import *  # selfmade
    from servo import ServoX  # selfmade
    # from camera_manager import CameraManager  # selfmade
    # from brightness_detector import CameraBrightnessDetector  # selfmade
    # from object_detector import CameraObjectDetector  # selfmade
    from pausR import PausR  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

# ======================== VARIABLE DECLARATION =======================
# ===== GLOBAL VARIABLES =====
utility = Util()
wifi = None
file_Manager = None
camera_man = None
brightness_cam = None
object_cam = None
pause_event = threading.Event()

# ======================== VARIABLE DECLARATION =======================
# ===== PORTS ANALOG =====
PORT_LIGHT_SENSOR_FRONT = utility.get_port_file_entries('PORT_LIGHT_SENSOR_FRONT', 'Analog')
PORT_LIGHT_SENSOR_BACK = utility.get_port_file_entries('PORT_LIGHT_SENSOR_BACK', 'Analog')
PORT_LIGHT_SENSOR_SIDE = utility.get_port_file_entries('PORT_LIGHT_SENSOR_SIDE', 'Analog')
PORT_LIGHT_SENSOR_START = utility.get_port_file_entries('PORT_LIGHT_SENSOR_START', 'Analog')
# PORT_DISTANCE_SENSOR = utility.get_port_file_entries('PORT_DISTANCE_SENSOR', 'Analog')

# ===== PORTS DIGITAL =====
# PORT_BUTTON_STARTER = 9
PORT_BUTTON_FR = utility.get_port_file_entries('PORT_BUTTON_FR', 'Digital')
PORT_BUTTON_FL = utility.get_port_file_entries('PORT_BUTTON_FL', 'Digital')
PORT_BUTTON_BR = utility.get_port_file_entries('PORT_BUTTON_BR', 'Digital')
PORT_BUTTON_BL = utility.get_port_file_entries('PORT_BUTTON_BL', 'Digital')
PORT_BUTTON_END = utility.get_port_file_entries('PORT_BUTTON_END', 'Digital')

# ===== PORTS MOTORS =====
PORT_MOTOR_FR = utility.get_port_file_entries('PORT_MOTOR_FR', 'Motor')
PORT_MOTOR_FL = utility.get_port_file_entries('PORT_MOTOR_FL', 'Motor')
PORT_MOTOR_BR = utility.get_port_file_entries('PORT_MOTOR_BR', 'Motor')
PORT_MOTOR_BL = utility.get_port_file_entries('PORT_MOTOR_BL', 'Motor')

# ===== PORTS SERVOS =====
PORT_SERVO_STEM = utility.get_port_file_entries('PORT_SERVO_STEM', 'Servo')
PORT_SERVO_ARM = utility.get_port_file_entries('PORT_SERVO_ARM', 'Servo')
PORT_SERVO_CLAW = utility.get_port_file_entries('PORT_SERVO_CLAW', 'Servo')
PORT_SERVO_STABELIZER = utility.get_port_file_entries('PORT_SERVO_STABELIZER', 'Servo')


# ======================== SETUP FUNCTIONS =======================
def Camera_Setup():
    global camera_man, brightness_cam, object_cam
    try:
        camera_man = CameraManager(
            cam_index=X)  # integer number of the USB-port in which you plugged in the USB-camera. eg: 4; 2; 1; ...
        brightness_cam = CameraBrightnessDetector(camera_man)
        object_cam = CameraObjectDetector(camera_man)
    except Exception as e:
        log(f'Camera Exception: {str(e)}', important=True, in_exception=True)


def Comm_Setup():
    try:
        globals()['pause_event'] = PausR()
        globals()['comm'] = RobotCommunicator('192.168.XX.XX', 10000, is_server=True,
                                              pause_event=pause_event)  # one has to be the server, the other one has to be is_server=False (or be left out) -> both need the IP-Adress (IP from the the server) and the same port to communicate
        #  XX here represents the complete IPv4-Address. eg: 192.168.0.10; 10.290.5.100; 172.100.5.134
    except Exception as e:
        log(f'Communication Exception: {str(e)}', important=True, in_exception=True)


def Instancer_Setup():
    try:
        # ============ Ports Initializing ===========
        # ================ DIGITAL ===============
        # globals()['AcceptButton'] = Digital(PORT_BUTTON_STARTER)
        globals()['AcceptButton'] = Digital(PORT_BUTTON_FR)
        globals()['Button_FR'] = Digital(PORT_BUTTON_FR)
        globals()['Button_FL'] = Digital(PORT_BUTTON_FL)
        globals()['Button_BR'] = Digital(PORT_BUTTON_BR)
        globals()['Button_BL'] = Digital(PORT_BUTTON_BL)
        globals()['Button_End'] = Digital(PORT_BUTTON_END)

        # ============= DistanceSensor ===========
        # globals()['DistanceSens'] = DistanceSensor(PORT_DISTANCE_SENSOR)

        # ============== LightSensor =============
        globals()['LightSensorFront'] = LightSensor('front',
                                                    PORT_LIGHT_SENSOR_FRONT)  # the amount of error that you allow from the light sensor. Higher value means it is more forgiving. Integer value is required. eg: 150; 500; 300
        globals()['LightSensorBack'] = LightSensor('back',
                                                   PORT_LIGHT_SENSOR_BACK)  # the amount of error that you allow from the light sensor. Higher value means it is more forgiving. Integer value is required. eg: 150; 500; 300
        globals()['LightSensorSide'] = LightSensor('side',
                                                   PORT_LIGHT_SENSOR_SIDE)  # the amount of error that you allow from the light sensor. Higher value means it is more forgiving. Integer value is required. eg: 150; 500; 300

        # ================== WheelR =================
        globals()['Wheel_FR'] = WheelR(PORT_MOTOR_FR)
        globals()['Wheel_FL'] = WheelR(PORT_MOTOR_FL)
        globals()['Wheel_BR'] = WheelR(PORT_MOTOR_BR)
        globals()['Wheel_BL'] = WheelR(PORT_MOTOR_BL)

        # ================= DriveR ==================
        globals()['MecanumWheeler'] = Mecanum_Wheels_four(Instance_front_right_wheel=Wheel_FR,
                                                          Instance_front_left_wheel=Wheel_FL,
                                                          Instance_back_right_wheel=Wheel_BR,
                                                          Instance_back_left_wheel=Wheel_BL,
                                                          Instance_button_front_right=Button_FR,
                                                          Instance_button_front_left=Button_FL,
                                                          Instance_button_back_right=Button_BR,
                                                          Instance_button_back_left=Button_BL,
                                                          Instance_light_sensor_front=LightSensorFront,
                                                          Instance_light_sensor_back=LightSensorBack,
                                                          Instance_light_sensor_side=LightSensorSide)  # ,
        # Instance_distance_sensor=DistanceSens)

        globals()['Servo_Stem'] = ServoX(PORT_SERVO_STEM)
        globals()['Servo_Arm'] = ServoX(PORT_SERVO_ARM)
        globals()['Servo_Claw'] = ServoX(PORT_SERVO_CLAW, min_value=700, max_value=1600)
        globals()['Servo_Stabelizer'] = ServoX(PORT_SERVO_STABELIZER)



    except Exception as e:
        log(f'Instancer Exception: {str(e)}', important=True, in_exception=True)


def FileR_Setup():
    global file_Manager
    try:
        file_Manager = FileR()
    except Exception as e:
        log(f'FileR Exception: {str(e)}', important=True, in_exception=True)


def setup():
    try:
        # Comm_Setup()
        # Camera_Setup()  # if you want to use the camera
        FileR_Setup()
        Instancer_Setup()
    except Exception as e:
        log(f'Setup Exception: {str(e)}', important=True, in_exception=True)


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


def set_claw_start_pos():
    Servo_Claw.set_pos(700)
    Servo_Stem.set_pos(1650)
    Servo_Arm.set_pos(777)


# ======================== MAIN =======================
# STEM -> 0: zum Boden ; 2047: gerade
# CLAW -> 700: auf ; 1600: zu
# ARM -> 0: zum Boden ; 2047: in die Hoehe

def main(p_event,
         communication):  # leave it as it is, just write in the try / catch block! Do not remove the "p_event" or "communication"! (You can obviously write anything outside and inside the main though) If you delete any of those parameters, there wont be a communication
    try:  # try / catch is always useful in the main! leave it!
        set_claw_start_pos()
        # for i in range(5):
        #register_light_values()

        k.wait_for_light(PORT_LIGHT_SENSOR_START)
        k.shut_down_in(119)
        #while not Button_FR.is_pressed():
        #    continue
        begin_timer = TimeR()
        begin_timer.start_timer_sec()
        Servo_Arm.set_pos(2047)
        MecanumWheeler.drive_side_condition_analog('right', LightSensorFront, '<', LightSensorFront.get_value_black_bias())
        MecanumWheeler.drive_side('left', 650)
        MecanumWheeler.drive_straight(500, -1400)
        Servo_Arm.set_pos(0)
        Servo_Stem.set_pos(0)
        MecanumWheeler.drive_straight(750)
        Servo_Claw.set_pos(1600)
        Servo_Arm.range_to_pos(2047)
        Servo_Stem.set_pos(2047)

        # Starting Area Poms
        MecanumWheeler.turn_degrees('right', 88)
        MecanumWheeler.drive_straight_condition_digital(Button_BR, '!=', 1, speed=-1400)
        MecanumWheeler.align_drive_back()
        MecanumWheeler.drive_straight_condition_analog(LightSensorBack, '<', LightSensorBack.get_value_black_bias())
        MecanumWheeler.drive_straight_condition_analog(LightSensorBack, '>', LightSensorBack.get_value_white_bias())
        MecanumWheeler.drive_straight(200)
        MecanumWheeler.turn_degrees('right', 90)

        # Get to dispenser
        MecanumWheeler.drive_straight_condition_analog(LightSensorFront, '<', LightSensorFront.get_value_black_bias())
        MecanumWheeler.drive_straight_condition_analog(LightSensorBack, '<', LightSensorBack.get_value_black_bias())
        MecanumWheeler.drive_straight_condition_analog(LightSensorBack, '>', LightSensorBack.get_value_white_bias())
        MecanumWheeler.drive_straight_condition_analog(LightSensorBack, '<', LightSensorBack.get_value_black_bias())
        MecanumWheeler.turn_degrees_far('left', True, 80)
        MecanumWheeler.drive_straight(400)
        MecanumWheeler.turn_degrees_far('right', True, 80)
        wall_found = MecanumWheeler.drive_straight_condition_digital(Button_FR, '!=', 1, millis=3000)
        if not wall_found:
            MecanumWheeler.drive_straight(100, -1400)
            MecanumWheeler.turn_degrees('left', 45)
            MecanumWheeler.turn_degrees('right', 90)
            MecanumWheeler.turn_degrees('left', 45)
            MecanumWheeler.drive_side('left', 200)
            wall_found = MecanumWheeler.drive_straight_condition_digital(Button_FR, '!=', 1, millis=2000)

        if wall_found:
            MecanumWheeler.align_drive_front()
            MecanumWheeler.turn_degrees('left', 90)
        else:
            MecanumWheeler.drive_straight(1000, -1400)
            MecanumWheeler.turn_degrees('left', 90)
            MecanumWheeler.drive_straight_condition_digital(Button_FL, '!=', 1)
            MecanumWheeler.align_drive_front()
            MecanumWheeler.drive_side('right', 2000)


        # Drop Gucci Bag
        MecanumWheeler.align_drive_front()
        MecanumWheeler.drive_side('left', 600)
        MecanumWheeler.drive_straight(700, -1400)
        while 30 < begin_timer.stop_timer(False) < 32:  # saving the enemies from possible destruction
            continue
        Servo_Stem.set_pos(0)
        Servo_Arm.set_pos(0)
        Servo_Claw.set_pos(700)
        MecanumWheeler.drive_side('right', 300)
        log(begin_timer.stop_timer(False))

        # Get away from dispenser
        Servo_Arm.set_pos(2047)
        Servo_Stem.set_pos(500)
        Servo_Arm.set_pos(1000)
        multiprocessing.Process(target=Servo_Arm.set_pos, args=(2047,)).start()
        MecanumWheeler.drive_side('left', 500)
        MecanumWheeler.align_drive_front()

        # Get to Cube and Cone (center)
        Servo_Stem.set_pos(2047)
        Servo_Arm.set_pos(2047)
        MecanumWheeler.drive_side_condition_analog('left', LightSensorSide, '<', LightSensorSide.get_value_black_bias())
        MecanumWheeler.align_drive_front()
        MecanumWheeler.drive_side_condition_analog('left', LightSensorBack, '<', LightSensorBack.get_value_black_bias())
        MecanumWheeler.align_drive_front()
        MecanumWheeler.turn_degrees('right', 35)
        MecanumWheeler.drive_side_condition_analog('left', LightSensorSide, '>', LightSensorSide.get_value_white_bias())
        MecanumWheeler.drive_side_condition_analog('left', LightSensorSide, '<', LightSensorSide.get_value_black_bias())
        MecanumWheeler.drive_side_condition_analog('left', LightSensorBack, '<', LightSensorBack.get_value_black_bias())
        MecanumWheeler.align_drive_front()

        # Get to BotGuy
        MecanumWheeler.black_line(300, True)
        MecanumWheeler.align_drive_front(millis=2000)
        MecanumWheeler.drive_side('right', 300)

        # Grab BotGuy
        Servo_Stem.set_pos(0)
        Servo_Arm.set_pos(0)
        MecanumWheeler.drive_straight(1000, -1500)
        MecanumWheeler.drive_straight(500)
        Servo_Stabelizer.set_pos(1500)
        Servo_Stabelizer.set_pos(0)
        Servo_Stabelizer.set_pos(1500)
        Servo_Stabelizer.set_pos(0)
        MecanumWheeler.drive_straight(500, -1400)
        Servo_Claw.set_pos(1600)
        Servo_Arm.set_pos(2047)
        Servo_Stem.range_to_pos(2047)
        log(begin_timer.stop_timer(False))

        # Get to upper warehouse
        MecanumWheeler.drive_straight_condition_digital(Button_BR, '!=', 1, speed=-1400, millis=3000)
        MecanumWheeler.align_drive_back(millis=2000)
        MecanumWheeler.turn_degrees('left', 180)
        MecanumWheeler.align_drive_front(millis=2000)
        MecanumWheeler.drive_side('left', 1000)
        MecanumWheeler.drive_straight(1000)
        MecanumWheeler.drive_side('left', 1000)
        MecanumWheeler.drive_straight(1000)

        # Drop BotGuy
        Servo_Stem.set_pos(1800)
        Servo_Claw.range_to_pos(700)
        Servo_Stem.set_pos(2047)

        # Get to Drum Collector
        MecanumWheeler.turn_degrees('left', 90)
        MecanumWheeler.drive_straight_condition_digital(Button_BL, '!=', 1, speed=-1400)
        MecanumWheeler.align_drive_back()
        MecanumWheeler.drive_straight(650)
        MecanumWheeler.turn_degrees('right', 90)
        MecanumWheeler.drive_straight(500, -1400)
        Servo_Stem.set_pos(800)
        Servo_Arm.set_pos(0)
        MecanumWheeler.drive_straight_condition_analog(LightSensorFront, '<', LightSensorFront.get_value_black_bias())
        MecanumWheeler.drive_straight(500)
        Servo_Claw.set_pos(1600)
        Servo_Stem.set_pos(0)
        MecanumWheeler.drive_straight(200, -1400)

        # Raise Drum Collector
        Servo_Arm.range_to_pos(2047, 2)
        Servo_Stem.range_to_pos(2047)

        # Get to ADDS
        MecanumWheeler.turn_degrees('left', 55)
        MecanumWheeler.drive_straight(4000, -1400)
        MecanumWheeler.drive_straight(500)
        MecanumWheeler.turn_degrees('left', 55)
        MecanumWheeler.drive_straight_condition_digital(Button_FL, '!=', 1)
        for i in range(5):
            Servo_Stabelizer.set_pos(600)
            Servo_Stabelizer.set_pos(2047)
        MecanumWheeler.drive_straight(1000)

        # Drop the Drum Collector
        Servo_Stem.range_to_pos(0)
        Servo_Arm.range_to_pos(1200)
        Servo_Stem.set_pos(2000)
        MecanumWheeler.drive_straight(3000, -1400)
        Servo_Stem.set_pos(500)
        Servo_Arm.set_pos(1200)
        MecanumWheeler.drive_straight(1500)
        MecanumWheeler.drive_straight(3000, -1400)
        MecanumWheeler.drive_diagonal('back', 'left', 500)
        Servo_Arm.set_pos(0)

        # Collect all drums
        for i in range(10):
            MecanumWheeler.drive_side('right', 750)
            MecanumWheeler.turn_degrees('right', 50)

        MecanumWheeler.turn_degrees_far('right', False, 120)
        MecanumWheeler.drive_straight(1500)
        MecanumWheeler.turn_degrees('right', 45)
        multiprocessing.Process(target=Servo_Stem.range_to_pos, args=(0,)).start()
        MecanumWheeler.drive_straight(500)
        Servo_Arm.range_to_pos(1600, 2)

        # Get to lower start box
        MecanumWheeler.drive_straight(1000, -1400)
        MecanumWheeler.turn_degrees('left', 90)
        MecanumWheeler.drive_straight_condition_digital(Button_BR, '!=', 1, speed=-1400)
        MecanumWheeler.align_drive_back()
        Servo_Stem.set_pos(0)
        Servo_Arm.range_to_pos(2047, 1)
        MecanumWheeler.turn_degrees('left', 45)
        for i in range(5):
            MecanumWheeler.turn_degrees('left', 45)
            MecanumWheeler.turn_degrees('right', 45)

        log(begin_timer.stop_timer(False))












    except Exception as e:
        log(f'Main Exception: {str(e)}', important=True, in_exception=True)


if __name__ == "__main__":
    try:
        setup()
        main(None, None)  # if you want communication, replace this line with the "fake_main_setup()" line
        # fake_main_setup()  # if you do not need communication, you can replace this line with the main() function
    except Exception as e:
        log(str(e), important=True, in_exception=True)