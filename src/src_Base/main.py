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
    from wheelR import WheelR  # selfmade
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
wifi = None
comm = None
file_Manager = None
camera_man = None
brightness_cam = None
object_cam = None
pause_event = threading.Event()

# ===== PORTS ANALOG =====


# ===== PORTS DIGITAL =====
PORT_BUTTON = 0


# ===== PORTS MOTORS =====


# ===== PORTS SERVOS =====



# ======================== SETUP FUNCTIONS =======================
def Camera_Setup():
    global camera_man, brightness_cam, object_cam
    try:
        camera_man = CameraManager(cam_index=X)  # integer number of the USB-port in which you plugged in the USB-camera. eg: 4; 2; 1; ...
        brightness_cam = CameraBrightnessDetector(camera_man)
        object_cam = CameraObjectDetector(camera_man)
    except Exception as e:
        log(f'Camera Exception: {str(e)}', important=True, in_exception=True)

def Wifi_Setup():
    global wifi
    try:
        wifi = WifiConnector.standard_conf()
        print('IP Address is:', wifi.get_ip_address(), flush=True)
    except Exception as e:
        log(f'WIFI Exception: {str(e)}', important=True, in_exception=True)


def Comm_Setup(p_event, Communication_instance):
	global comm
	try:
		if Communication_instance == None:
			comm = RobotCommunicator('192.168.XX.XX', 10000, is_server=True) # one has to be the server, the other one has to be is_server=False (or be left out) -> both need the IP-Adress (IP from the the server) and the same port to communicate
			#  XX here represents the complete IPv4-Address. eg: 192.168.0.10; 10.290.5.100; 172.100.5.134
			pause_event.set()
		else:
			Communication_instance.set_pause_event_instance(p_event)
	except Exception as e:
		log(f'Communication Exception: {str(e)}', important=True, in_exception=True)


def Instancer_Setup():
    try:
        # ============ Ports Initializing ===========
        # ================= Digital =================
        globals()['TestButton'] = Digital(PORT_BUTTON)  # This is how you will declare all sensors and motors and servos. globals()['{VAR_NAME)'] creates a global variable that is accessable EVERYWHERE (see main function)!

        # ================= ServoX ==================
    
        # ============== DistanceSensor =============

        # =============== LightSensor ===============

        # ================== Util ===================

        # ================= DriveR ==================
        
    except Exception as e:
        log(f'Instancer Exception: {str(e)}', important=True, in_exception=True)


def FileR_Setup():
    global file_Manager
    try:
        file_Manager = FileR()
    except Exception as e:
        log(f'FileR Exception: {str(e)}', important=True, in_exception=True)


def fake_main_setup():  # see this as the call of the main function -> only execute this in the if __name__ == "__main__": line (if you want communication)
    try:
        Comm_Setup(pause_event, comm)
        f_main = FakeR(thread_instance=pause_event, comm_instance=comm)
        f_main.start()
    except Exception as e:
        log(str(e), important=True, in_exception=True)


def setup(pause_instance, Communication_instance):
    try:
        Wifi_Setup()  # you can delete this line from now on, just as the function!
        # Comm_Setup(pause_instance, Communication_instance)
        # Camera_Setup()  # if you want to use the camera
        FileR_Setup()
        Instancer_Setup()
    except Exception as e:
        log(f'Setup Exception: {str(e)}', important=True, in_exception=True)

# ======================== CUSTOM METHODS =======================

def is_it_pressed():
    log('waiting till its pressed')
    while not TestButton.is_pressed():
        continue

def handle_high_priority():
	try:
		is_it_pressed()
		log('continue with program...')
	except Exception as e:
		log(f'handle exception: {str(e)}', important=True, in_exception=True)

def do_something():
    log('driving straight...')
    time.sleep(1)
    log('turning...')
    time.sleep(1)

def another_main(p_event, communication):  # every new main should have the p_event and communication instances (except you do not need communication from this moment on)
    try:
        communication.send('I am in the new main now!')
        log('breathing...')
        time.sleep(1)
        log('exhaling...')
        time.sleep(1)
    except Exception as e:
        log(f'Another main exception: {str(e)}', in_exception=True, important=True)


# ======================== MAIN =======================

def main(p_event, communication):  # leave it as it is, just write in the try / catch block! Do not remove the "p_event" or "communication"! (You can obviously write anything outside and inside the main though) If you delete any of those parameters, there wont be a communication
    try:  # try / catch is always useful in the main! leave it!
        #communication.on_new_main(another_main, p_event, communication)  # if something does not working accordingly you can all the time send a message so another main will be executed
        setup(p_event, communication)  # if you use the ocmmunication, you need these parameters
        #communication.on_high_priority(handle_high_priority)
        print(TestButton.is_pressed(), flush=True)
        log('actual program running right now...')
        #for _ in range(5):  # simulation of doing anything before sending a high priority message
        #    do_something()
        #communication.send('hallo client!', priority='high')  # keep care that the client is running at this time as well, otherwise the message will get sent into the void
        #for _ in range(5):
        #    do_something()

    except Exception as e:
        log(f'Main Exception: {str(e)}', important=True, in_exception=True)


if __name__ == "__main__":
    try:
        main(None, None)  # if you want communication, replace this line with the "fake_main_setup()" line
        #fake_main_setup()  # if you do not need communication, you can replace this line with the main() function
    except Exception as e:
        log(str(e), important=True, in_exception=True)