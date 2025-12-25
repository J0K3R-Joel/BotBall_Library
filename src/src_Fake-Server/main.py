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
    from wifi import WifiConnector  # selfmade
    from RoboComm import RobotCommunicator  # selfmade
    from digital import Digital  # selfmade
    from fake import FakeR  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


# ======================== VARIABLE DECLARATION =======================
# ===== GLOBAL VARIABLES =====
wifi = None
comm = None
pause_event = threading.Event()

# ===== PORTS ANALOG =====


# ===== PORTS DIGITAL =====
#PORT_BUTTON = XX  # XX is an placeholder for the integor of the digital port where the button is plugged in. eg. 0; 1; 9; 4


# ===== PORTS MOTORS =====


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
			comm = RobotCommunicator('192.168.XX.XX', 10000, is_server=True) # one has to be the server, the other one has to be is_server=False (or be left out) -> both need the IP-Adress (IP from the the server) and the same port to communicate
            #  XX here represents the complete IPv4-Address. eg: 192.168.0.10; 10.290.5.100; 172.100.5.134
			pause_event.set()
		else:
			Communication_instance.set_pause_event_instance(p_event)
	except Exception as e:
		log(f'Communication Exception: {str(e)}', important=True, in_exception=True)


def Instancer_Setup():
    try:
        print('you can delete this line from now on and uncomment the global variable', flush=True)
        # ============ Ports Initializing ===========
        #globals()['TestButton'] = Digital(PORT_BUTTON)  # This is how you will declare all sensors and motors and servos. globals()['{VAR_NAME)'] creates a global variable that is accessable EVERYWHERE (see main function)!

        # ================== Util ===================

        # ================= DriveR ==================
    
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
        Wifi_Setup()  # you can delete this line from now on, just as the function!
        Comm_Setup(pause_instance, Communication_instance)
        Instancer_Setup()
    except Exception as e:
        log(f'Setup Exception: {str(e)}', important=True, in_exception=True)

# ======================== CUSTOM METHODS =======================


# ======================== MAIN =======================

def main(p_event, communication):  # leave it as it is, just write in the try / catch block! Do not remove the "p_event" or "communication"! (You can obviously write anything outside and inside the main though) If you delete any of those parameters, there wont be a communication
    try:  # try / catch is always useful in the main! leave it!
        print('uncomment to start. Also uncomment in the "end_main" function and where you execute this function from. You can now delete this line.\nDo not forget to change the invalid params (like XX)', flush=True)
        #setup(p_event, communication)  # if you use the ocmmunication, you need these parameters
        #i = 0
        #while communication.is_connected():
        #    if TestButton.is_pressed():
        #        i += 1
        #        communication.send('button got pressed', priority='high')
        #        print('sent: ', i)
        #    k.msleep(100)
            

    except Exception as e:
        log(f'Main Exception: {str(e)}', important=True, in_exception=True)

if __name__ == "__main__":
    try:
        main(None, None)  # if you want communication, replace this line with the "fake_main_setup()" line
        #fake_main_setup()  # if you do not need communication, you can replace this line with the main() function
    except Exception as e:
        log(str(e), important=True, in_exception=True)