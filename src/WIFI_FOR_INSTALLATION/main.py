#!/usr/bin/python3
import os, sys

sys.path.append("/usr/lib")
try:
    from commU import WifiConnector
    import time
    import subprocess
except Exception as e:
    print('Import Exception: ', str(e), flush=True)


def wifi_setup():
    SSID = 'TMOBILE-36869'
    PASS = 'TMADE24762'
    connector = WifiConnector(ssid=SSID, password=PASS)
    if not connector.is_connected_to_ssid():
        print(
            f'Wombat not connected to the wifi, make sure, that you will reconnect with the wifi {SSID}, after some time (give it like a minute)',
            flush=True)
        connector.enable_wifi_scanning()
        connector.run()
        time.sleep(2)
        #subprocess.run(['sudo', 'reboot'])
    else:
        print('Wifi successfully setup', flush=True)


def main():
    wifi_setup()

    print('actual program running now...', flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(str(e))