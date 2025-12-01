#!/usr/bin/python3
import os, sys

sys.path.append("/usr/lib")

from logger import *  # selfmade

try:
    import threading
except Exception as e:
    log(f'Import Exception: {str(e)}', in_exception=True, important=True)


class PausR(threading.Event):
    def __init__(self):
        self.event = threading.Event()

    def get_event(self):
        return self.get_event()




