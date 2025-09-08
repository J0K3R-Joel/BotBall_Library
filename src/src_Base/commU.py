#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-07-28

try:
    import subprocess
    import socket
    import time
    from fileR import FileR  # selfmade
    from util import Util  # selfmade
except Exception as e:
    log(f'Import Exception in WifiConnector: {str(e)}', important=True, in_exception=True)

class WifiConnector:
    def __init__(self, ssid: str=None, password: str=None):
        self.ssid = ssid
        self.password = password
        self.file_path = '/home/kipr/wombat-os/configFiles/wifiConnectionMode.txt'
        self.AP_MODE = '0'
        self.CLIENT_MODE = '1'
        self.file_manager = FileR()


    # ======================== PUBLIC METHODS ========================

    @classmethod
    def standard_conf(cls):
        '''
        Start the connection with the router for Botball (will be used for communication)

        Args:
            None

       Returns:
            the created instance of this WifiConnector class
        '''
        instance = cls(
            ssid='S22-Ultra',
            password='wombat123'
        )
        if not instance.is_connected_to_ssid():
            log(f'Wombat not connected to the wifi, trying to reconnect to SSID: {instance.ssid}')
            instance.enable_wifi_scanning()
            instance.run()
            time.sleep(2)
        else:
            log('Wifi successfully setup')
        return instance

    def get_mode(self) -> str:
        '''
        Lets you see in which mode the device is at the moment

        Args:
            None

       Returns:
            If it is in AP (Access Point) or Client mode at this moment
                0 -> AP mode
                1 -> Client mode
                2 -> Event mode (just do not use it, since you can not use wifi in this mode -> no communication)
        '''
        text = self.file_manager.reader(self.file_path)
        return text[text.find('MODE ') + 5]

    def set_mode(self, new_mode: str) -> None:
        '''
        Lets you overwrite in which mode the device should be set

        Args:
            new_mode (str):
                             0 -> AP mode
                             1 -> Client mode
                             2 -> Event mode (just do not use it, since you can not use wifi in this mode -> no communication)

       Returns:
            None
        '''
        text = self.file_manager.reader(self.file_path)
        mode_index = text.find('MODE ') + 5
        new_text = text[:mode_index] + text[mode_index:].replace(text[mode_index], new_mode)
        self.file_manager.writer(self.file_path, 'w', new_text)

    def enable_wifi_scanning(self):
        '''
        lets you be able to see all networks again (in the very beginning you will not see any)

        Args:
            None

       Returns:
            None
        '''
        try:
            log('Wifi scan is getting started ...')

            # Change to client mode to be able to connect with a wifi
            self.set_mode(self.CLIENT_MODE)
            log('Wifi scan should work now. Starting scan ...')

            self.list_available_networks()
        except Exception as e:
            log(f'Error while activating Wifi scan: {str(e)}', important=True, in_exception=True)

    def list_available_networks(self) -> None:
        '''
        Lets you see all available networks that the roboter can see at this moment

        Args:
            None

       Returns:
            None
        '''
        try:
            log('Scanning all available networks ...')
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )

            networks = result.stdout.decode().splitlines()
            networks = [line for line in networks if line]  # filter empty lines

            if not networks:
                log('No networks found!', important=True)
                return

            log('Networks found:')
            for net in networks:
                ssid, signal = net.split(':', 1)
                if ssid:
                    print(f'  SSID: {ssid:<30} Signal: {signal}%', flush=True)

        except subprocess.CalledProcessError as e:
            log(f'Error while scanning: {e.stderr.decode()}', important=True, in_exception=True)
        except Exception as e:
            log(f'Unknown Error: {str(e)}', important=True, in_exception=True)

    def is_connected_to_ssid(self) -> bool:
        '''
        Looks, if you are currently connected to the ssid that you chose when initializing this class

        Args:
            None

       Returns:
            If you are connected with the chosen wifi (True), or with any other wifi or just no wifi at all (False)
        '''
        try:
            result = subprocess.run(['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL)
            for line in result.stdout.decode().splitlines():
                active, current_ssid = line.split(':')
                if active == 'yes' and current_ssid == self.ssid:
                    return True
            return False
        except Exception as e:
            log(f'Error while checking the wifi connection: {str(e)}', important=True, in_exception=True)
            return False

    def connect_to_wifi(self):
        '''
        Lets you connect to the chosen ssid with the chosen password

        Args:
            None

       Returns:
            None
        '''
        if self.ssid == None or self.password == None:
            log('You need to tell the constructor the SSID and password of the WIFI you are trying to connect to!', in_exception=True)
            raise Exception('You need to tell the constructor the SSID and password of the WIFI you are trying to connect to!')
        try:
            subprocess.run(
                ["nmcli", "dev", "wifi", "connect", self.ssid, "password", self.password],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            log(f"Successfully connected with {self.ssid} .")
        except subprocess.CalledProcessError as e:
            log(f'Wifi connection failed: {e.stderr.decode()}', important=True, in_exception=True)

    def get_ip_address(self) -> str:
        '''
        Tells you the current IP-Adress of the device

        Args:
            None

       Returns:
            The IPv4 Adress of this current device
        '''
        try:
            ip = subprocess.check_output(["hostname", "-I"]).decode().strip().split()[0]
            return ip
        except Exception as e:
            log(f'No IP-Adresse found: {str(e)}', important=True, in_exception=True)

    def run(self):
        '''
        Starts the connection with the chosen wifi with the chosen ssid and password

        Args:
            None

       Returns:
            None, but tells you the IP-Adress in the end
        '''
        if self.ssid == None or self.password == None:
            log('You need to tell the constructor the SSID and password of the WIFI you are trying to connect to!', in_exception=True)
            raise Exception(
                'You need to tell the constructor the SSID and password of the WIFI you are trying to connect to!')

        # Step1: Set wallaby to client mode
        if self.get_mode() != self.CLIENT_MODE:
            log("Change to client mode ...")
            self.set_mode(self.CLIENT_MODE)

        # Step2: Connect to wifi
        if not self.is_connected_to_ssid():
            log(f"Not connected with {self.ssid} . Connecting ...")
            self.connect_to_wifi()

        # Step3: show IP-Address
        ip = self.get_ip_address()
        log(f"Connected. IP-Address: {ip}")