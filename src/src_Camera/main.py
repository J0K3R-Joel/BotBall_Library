#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-09-17

try:
    from camera_manager import CameraManager  # selfmade
    from brightness_detector import CameraBrightnessDetector  # selfmade
    from object_detector import CameraObjectDetector  # selfmade
except Exception as e:
    log(f"Import Exception: {str(e)}", important=True, in_exception=True)

camera_man = None

def main():
    print('uncomment to start camera detection', flush=True)
    #try:
        #global camera_man
        #camera_man = CameraManager(cam_index=X)  # integer number of the USB-port in which you plugged in the USB-camera. eg: 4; 2; 1; ...
        #brightness_man = CameraBrightnessDetector(camera_man, tiles_x=2, tiles_y=5)
        #object_man = CameraObjectDetector(camera_man)
    
        #print(brightness_man.find_black(), flush=True)
        #if brightness_man.is_white_top():
        #    print('something white is on the top half', flush=True)
        #else:
        #    print('nothing white found on the top half', flush=True)

        #if object_man.find_by_color('red'):
        #    print('ooh, something red was found!', flush=True)

        #object_man.wait_for_object("red_pom", max_secs=10)
    #except Exception as e:
     #   log(f'Main Exception: {str(e)}', important=True, in_exception=True)
    #finally:
        #camera_man.release()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f'Main execution exception: {str(e)}', important=True, in_exception=True)