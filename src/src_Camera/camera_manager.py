#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-09-15

try:
    import cv2
    import threading
    import time
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

class CameraManager:
    def __init__(self, cam_index=1, warmup_frames=30, warmup_delay=0.05):
        self.lock = threading.Lock()
        self.cap = cv2.VideoCapture(cam_index)
        self._warmed_up = False
        self.warmup_frames = warmup_frames
        self.warmup_delay = warmup_delay

    def _warmup(self) -> None:
        '''
        when initializing the camera, it takes some time so you get a clear image and not an image where everything is kind of black, since it just got started

        Args:
            None

        Returns:
            None
        '''
        if not self._warmed_up:
            for _ in range(self.warmup_frames):
                self.cap.read()
                time.sleep(self.warmup_delay)
            self._warmed_up = True

    def get_frame(self, retries:int=5, delay:float=0.05):
        '''
        create one frame. If there is an error, then retry again

        Args:
            retries (int, optional): how often it should retry after nothing could be read (default: 5)
            delay (float, optional): the time in seconds between two (re)tries (default: 0.05)

        Returns:
            The image taken
        '''
        with self.lock:
            self._warmup()

            for _ in range(retries):
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    return frame
                time.sleep(delay)
            log("No valid frame found", important=True, in_exception=True)
            raise RuntimeError("No valid frame found")

    def release(self):
        '''
        deletes the instance of this class. After releasing, you need to initialize again

        Args:
            None

        Returns:
            None
        '''
        with self.lock:
            if self.cap.isOpened():
                self.cap.release()
            cv2.destroyAllWindows()
            self._warmed_up = False
