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
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

class WifiConnector:
    file_path_std_wifi_conf = '/usr/lib/LOCAL_STD_WIFI.conf'

    def __init__(self, ssid: str = None, password: str = None):
        self.ssid = ssid
        self.password = password
        self.file_path_mode = '/home/kipr/wombat-os/configFiles/wifiConnectionMode.txt'  # this file is from kipr themselves
        self.AP_MODE = '0'  # fixed value (by kipr)
        self.CLIENT_MODE = '1'  # fixed value (by kipr)
        self.file_manager = FileR()


    # ======================== PUBLIC METHODS ========================

    @classmethod
    def standard_conf(cls):
        '''
        Start the connection with the router for Botball (will be used for communication) using the preset settings you defined inside the standard wifi config file

        Args:
            None

       Returns:
            the created instance of this WifiConnector class
        '''
        if not os.path.exists(cls.file_path_std_wifi_conf):
            log(f'File {cls.file_path_std_wifi_conf} does not exist! Please create it manually. The structure of the file is in my GitHub (https://github.com/J0K3R-Joel/BotBall_Library.git). Otherwise you can reset the machine and begin with the setup again (but safe all important files beforehand!!)', important=True, in_exception=True)
            raise Exception(f'File {cls.file_path_std_wifi_conf} does not exist! Please create it manually. The structure of the file is in my GitHub (https://github.com/J0K3R-Joel/BotBall_Library.git). Otherwise you can reset the machine and begin with the setup again (but safe all important files beforehand!!)')

        with open(cls.file_path_std_wifi_conf, 'r') as freader:
            text = freader.read().strip().split('\n')
            wifi_name_start_index = text[0].find('=') + 1  # +1 so you skip the "=" and get the character after the "="
            wifi_passw_start_index = text[1].find('=') + 1  # +1 so you skip the "=" and get the character after the "="

            ssid = text[0][wifi_name_start_index:]
            pw = text[1][wifi_passw_start_index:]

        instance = cls(
            ssid=ssid,
            password=pw
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
        text = self.file_manager.reader(self.file_path_mode)
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
        text = self.file_manager.reader(self.file_path_mode)
        mode_index = text.find('MODE ') + 5
        new_text = text[:mode_index] + text[mode_index:].replace(text[mode_index], new_mode)
        self.file_manager.writer(self.file_path_mode, 'w', new_text)


    def change_local_std_wifi(self, ssid: str, password: str, connect: bool = False) -> None:
        '''
        Function to change the SSID and password of the LOCAL_STD_WIFI.conf file

        Args:
            ssid (str): The name of the WIFI you want to connect to
            password (str): The password of the WIFI you want to connect to
            connect (bool, optional): immediately connect to the given WIFI

        Returns:
            None
        '''
        with open(self.file_path_std_wifi_conf, 'r') as freader:
            ssid_line, passw_line = freader.read().split('\n')[0:2]
            ssid_label_index = ssid_line.find('=') + 1  # +1 to include the '='
            passw_label_index = passw_line.find('=') + 1  # +1 to include the '='

            new_ssid = ssid_line[0:ssid_label_index] + str(ssid)
            new_passw = passw_line[0:passw_label_index] + str(password)

            new_text = new_ssid + '\n' + new_passw
            self.file_manager.writer(self.file_path_std_wifi_conf, 'w', new_text)

        if connect:
            self.connect_to_wifi(ssid, password)

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
                ["sudo", "nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"],
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
            bool: If you are connected with the chosen wifi (True), or with any other wifi or just no wifi at all (False)
        '''
        try:
            result = subprocess.run(['sudo', 'nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'],
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

    def connect_to_wifi(self, ssid: str = None, password: str = None) -> None:
        '''
        Lets you connect to the chosen ssid with the chosen password

        Args:
            ssid (str, optional): The new WIFI name you want to connect to (default: None, because it should get connected to the classvariable)
            password (str, optional): The new WIFI password you want to connect to (default: None, because it should get connected to the classvariable)

        Returns:
            None
        '''
        if (self.ssid is None or self.password is None) and (ssid is None and password is None):
            log('You need to tell the constructor the SSID and password of the WIFI you are trying to connect to!', in_exception=True)
            raise ConnectionError('You need to tell the constructor the SSID and password of the WIFI you are trying to connect to!')

        name = ssid if ssid is not None else self.ssid
        passw = password if password is not None else self.password

        print(name, ssid, self.ssid, flush=True)

        try:
            subprocess.run(
                ['sudo', 'nmcli', 'dev', 'wifi', 'connect', name, 'password', passw],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            log(f'Successfully connected with {self.ssid} .')
        except subprocess.CalledProcessError as e:
            log(f'Wifi connection failed: {e.stderr.decode()}', important=True, in_exception=True)

    def get_ip_address(self) -> str:
        '''
        Tells you the current IP-Address of the device

        Args:
            None

       Returns:
            The IPv4 Address of this current device
        '''
        try:
            ip = subprocess.check_output(["hostname", "-I"]).decode().strip().split()[0]
            return ip
        except ConnectionError as e:
            log(f'No IP-Address found: {str(e)}', important=True, in_exception=True)

    def run(self) -> None:
        '''
        Starts the connection with the chosen wifi with the chosen ssid and password

        Args:
            None

       Returns:
            None, but tells you the IP-Address in the end
        '''
        if self.ssid == None or self.password == None:
            log('You need to tell the constructor the SSID and password of the WIFI you are trying to connect to!', in_exception=True)
            raise RuntimeError('You need to tell the constructor the SSID and password of the WIFI you are trying to connect to!')

        if self.get_mode() != self.CLIENT_MODE:
            log("Change to client mode ...")
            self.set_mode(self.CLIENT_MODE)

        if not self.is_connected_to_ssid():
            log(f"Not connected with {self.ssid} . Connecting ...")
            self.connect_to_wifi()

        ip = self.get_ip_address()
        log(f"Connected. IP-Address: {ip}")