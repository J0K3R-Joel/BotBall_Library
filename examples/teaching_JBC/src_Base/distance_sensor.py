#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-07-28

try:
    import time
    from analog import Analog  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


class DistanceSensor(Analog):
    def __init__(self, Port):
        super().__init__(Port)
