#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

try:
	import threading
	from RoboComm import RobotCommunicator  # selfmade
	import time
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


pause_event = threading.Event()
comm = None

# ======================== SETUP FUNCTIONS =======================

def Comm_Setup(p_event, Communication_instance):
	global comm
	try:
		if Communication_instance == None:
			comm = RobotCommunicator('192.168.0.10', 10000, is_server=True) # one has to be the server, the other one has to be is_server=False (or be left out) -> both need the IP-Adress (IP from the the server) and the same port to communicate
			pause_event.set()
		else:
			Communication_instance.set_pause_event_instance(p_event)
	except Exception as e:
		log(f'Communication Exception: {str(e)}', important=True, in_exception=True)

def fake_main_setup():  # see this as the call of the main function -> only execute this in the if __name__ == "__main__": line (if you want communication)
    try:
        Comm_Setup(pause_event, comm)
        f_main = FakeR(thread_instance=pause_event, comm_instance  = comm)
        f_main.start()
    except Exception as e:
        log(str(e), important=True, in_exception=True)

def setup(pause_instance, Communication_instance):
    try:
        Comm_Setup(pause_instance, Communication_instance)
    except Exception as e:
        log(f'Setup Exception: {str(e)}', important=True, in_exception=True)


# ======================== IMPORTANT FUNCTIONS =======================
def end_main(communication_instance):
    #communication_instance.disconnect()  # if you do not want communication, you can remove this line
    log('PROGRAM FINISHED')

# ======================== CUSTOM METHODS =======================

def do_something():
    log('driving straight...')
    time.sleep(1)
    log('turning...')
    time.sleep(1)

def another_main():
	log('breathing...')
	time.sleep(1)
	log('exhaling...')
	time.sleep(1)

def handle_high_priority(msg):
    log(f'HIGH PRIORITY MESSAGE RECEIVED: {msg}')
    time.sleep(10)
    log("continue with program...")

def drive_straight_text():
	try:
		log('driving straight..')
		time.sleep(2)
	except Exception as e:
		print(str(e))

def turn_degrees_text():
    log('turning...')
    time.sleep(2)


# ======================== MAIN =======================

def main(p_event, communication):
	try:
		#communication.on_new_main(another_main)  # if something does not working accordingly you can all the time send a message so another main will be executed (from the other machine!)
		#setup(p_event, communication) # uncomment this line to enable communication
		log("Starting program ...")
		# communication.on_high_priority(handle_high_priority)
		#tries = range(10)
		#for i in tries:
		#	drive_straight_text()
		#	turn_degrees_text()
		#communication.send('hallo client!', priority='high')  # keep care that the client is running at this time as well, otherwise the message will get sent into the void
	except Exception as e:
		log(str(e), important=True, in_exception=True)
	finally:
		end_main(communication)  # very important, you need to tell the main when to end (its important for communication, so if you do not need communication, you can remove this)


if __name__ == "__main__":
    try:
		main(None, None) # if you want communication, replace this line with the "fake_main_setup()" line
        #fake_main_setup()  # if you do not need communication, you can replace this line with the main() function
    except Exception as e:
        log(str(e), important=True, in_exception=True)
