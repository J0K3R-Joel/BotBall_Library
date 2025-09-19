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
    from fake import FakeR  # selfmade
    from driveR import *  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


# ======================== VARIABLE DECLARATION =======================
# ===== GLOBAL VARIABLES =====
wifi = None
comm = None
utility = None
file_Manager = None
pause_event = threading.Event()

# ===== PORTS ANALOG =====


# ===== PORTS DIGITAL =====


# ===== PORTS MOTORS =====
#PORT_MOTOR_FR = XX
#PORT_MOTOR_FL = XX
#PORT_MOTOR_BR = XX
#PORT_MOTOR_BL = XX

# ===== PORTS SERVOS =====



# ======================== SETUP FUNCTIONS =======================
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
			comm = RobotCommunicator('192.168.XX.XX', 10000, is_server=False) # one has to be the server, the other one has to be is_server=False (or be left out) -> both need the IP-Adress (IP from the the server) and the same port to communicate
			pause_event.set()
		else:
			Communication_instance.set_pause_event_instance(p_event)
	except Exception as e:
		log(f'Communication Exception: {str(e)}', important=True, in_exception=True)


def Instancer_Setup():
    try:
        print('you can delete this line from now on and uncomment the global variable', flush=True)
        # ============ Ports Initializing ===========

        # ================== Util ===================

        # ================= DriveR ==================
        #globals()['Noris'] = driveR_four(Port_front_right_wheel=PORT_MOTOR_FR,
        #                                 Port_front_left_wheel=PORT_MOTOR_FL,
        #                                 Port_back_right_wheel=PORT_MOTOR_BR,
        #                                 Port_back_left_wheel=PORT_MOTOR_BL,
		#			                     controller_standing=XX)
        # ============== DistanceSensor =============

        # =============== LightSensor ===============
    except Exception as e:
        log(f'Instancer Exception: {str(e)}', important=True, in_exception=True)


def fake_main_setup():  # see this as the call of the main function -> only execute this in the if __name__ == "__main__": line (if you want communication)
    try:
        Comm_Setup(pause_event, comm)
        f_main = FakeR(thread_instance=pause_event, comm_instance  = comm)
        f_main.start()
    except Exception as e:
        log(str(e), important=True, in_exception=True)


def setup(pause_instance, Communication_instance):
    try:
        Wifi_Setup()
        Comm_Setup(pause_instance, Communication_instance)
        Instancer_Setup()
    except Exception as e:
        log(f'Setup Exception: {str(e)}', important=True, in_exception=True)


# ======================== IMPORTANT FUNCTIONS =======================
def end_main(communication_instance):
    #if isinstance(communication_instance, RobotCommunicator):  # if you do not want communication, you can remove this line, otherwise you can implement this line
    #	communication_instance.disconnect()  # if you do not want communication, you can remove this line, otherwise you can implement this line
    log('PROGRAM FINISHED')

# ======================== CUSTOM METHODS =======================

def drift():
    times = 8
    for i in range(times):
        print('drifts done: ', i, flush=True)
        Noris.drive_straight(300, -2100)

def handle_high_priority():
	try:
		drift()
		log('continue with program...')
	except Exception as e:
		log(f'handle exception: {str(e)}', important=True, in_exception=True)

def another_main():
    try:
        log('breathing...')
        time.sleep(1)
        log('exhaling...')
        time.sleep(1)
    except Exception as e:
        log(f'Another main Exception: {str(e)}', important=True, in_exception=True)
    finally:
        end_main(None)  # very important, you need to tell the main when to end (its important for communication, so if you do not need communication, you can remove this)


# ======================== MAIN =======================

def main(p_event, communication):  # leave it as it is, just write in the try / catch block! Do not remove the "p_event" or "communication"! (You can obviously write anything outside and inside the main though) If you delete any of those parameters, there wont be a communication
    try:  # try / catch is always useful in the main! leave it!
        print('uncomment to start. Also uncomment in the "end_main" function and where you execute this function from. You can now delete this line.\nDo not forget to change the invalid params (like XX)', flush=True)
        #communication.on_new_main(another_main)  # if something does not working accordingly you can all the time send a message so another main will be executed
        #setup(p_event, communication)  # if you use the ocmmunication, you need these parameters
        #communication.on_high_priority(handle_high_priority)
        #Noris.calibrate_gyro_z(1, 1)
        #Noris.get_bias_gyro_z(True)
        #Noris.set_degrees(2.2)  # just a random value
        #print('normal main will be executed...', flush=True)
        #times = 50
        #for _ in range(times):
        #    Noris.drive_straight(5000)
        #    print('driving', flush=True)
        #    Noris.turn_degrees('right', 180)

    except Exception as e:
        log(f'Main Exception: {str(e)}', important=True, in_exception=True)
    finally:
        end_main(communication)  # very important, you need to tell the main when to end (its important for communication, so if you do not need communication, you can remove this)


if __name__ == "__main__":
    try:
        main(None, None)  # if you want communication, replace this line with the "fake_main_setup()" line
        #fake_main_setup()  # if you do not need communication, you can replace this line with the main() function
    except Exception as e:
        log(str(e), important=True, in_exception=True)