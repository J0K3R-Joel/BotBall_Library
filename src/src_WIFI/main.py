#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

try:
    from commU import WifiConnector  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


wifi = None

try:
    wifi = WifiConnector.standard_conf()
except Exception as e:
    log(f'WIFI ERROR: {str(e)}', important=True, in_exception=True)

def main():
    print('IP Address is:', wifi.get_ip_address(), flush=True)
    print('Actual program running now...', flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(str(e), flush=True)
