#!/usr/bin/python3
import os, sys

sys.path.append("/usr/lib")

from logger import *  # selfmade

try:
    import threading
    import time
    import atexit

except Exception as e:
    log(f'Import Exception: {str(e)}', in_exception=True, important=True)

class PausR(threading.Event):
    def __init__(self):
        atexit.register(self._cleanup)
        self.file_path = './instance_PausR.lock'  # /temp/
        self._create_lock()
        self.event = threading.Event()

    def _create_lock(self):
        if os.path.exists(self.file_path):
            #log('PausR Instance already exists! Only one instance is allowed globally!', in_)
            raise ValueError('PausR Instance already exists! Only one instance is allowed globally!')

        with open(self.file_path, 'w') as fwriter:
            pass

    def _cleanup(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def get_event(self):
        return self



if __name__ == '__main__':
    p = PausR().get_event()
    print(isinstance(p, PausR))
    print(isinstance(p, threading.Event))







