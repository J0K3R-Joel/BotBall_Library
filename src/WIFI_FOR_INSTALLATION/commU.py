#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

try:
    import subprocess
    import socket
    import time
    from fileR import FileR
except Exception as e:
    print('Import Exception: ', str(e), flush=True)


class WifiConnector:
    def __init__(self, ssid: str=None, password: str=None):
        self.ssid = ssid
        self.password = password
        self.file_path = '/home/kipr/wombat-os/configFiles/wifiConnectionMode.txt'
        self.AP_MODE = '0'
        self.CLIENT_MODE = '1'
        self.file_manager = FileR()


    @classmethod
    def standard_conf(cls):
        instance = cls(
            ssid='JOELK',
            password='5AHIT-BOTBALL-LinzerTechnikum1.'
        )
        if not instance.is_connected_to_ssid():
            print(
                f'Wombat not connected to the wifi, trying to reconnect to SSID: {instance.ssid}',
                flush=True)
            instance.enable_wifi_scanning()
            instance.run()
            time.sleep(2)
        else:
            print('Wifi successfully setup', flush=True)
        return instance

    def get_mode(self) -> str:
        text = self.file_manager.reader(self.file_path)
        return text[text.find('MODE ') + 5]

    def set_mode(self, new_mode: str):
        text = self.file_manager.reader(self.file_path)
        mode_index = text.find('MODE ') + 5
        new_text = text[:mode_index] + text[mode_index:].replace(text[mode_index], new_mode)
        self.file_manager.writer(self.file_path, 'w', new_text)

    def enable_wifi_scanning(self):
        try:
            print(f"Wifi scan is getting started ...", flush=True)

            # 1. Change to client mode
            self.set_mode(self.CLIENT_MODE)
            # time.sleep(1)

            # 2. restart all services, just to be sure that you are not longer in the AP mode
            # subprocess.run(["systemctl", "stop", "hostapd"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # subprocess.run(["systemctl", "stop", "dnsmasq"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # subprocess.run(["nmcli", "radio", "wifi", "off"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # time.sleep(1)
            # subprocess.run(["nmcli", "radio", "wifi", "on"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # time.sleep(2)

            # 3. allow scanning
            #subprocess.run(["nmcli", "dev", "set", "wlan0", "managed", "yes"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            print(f"Wifi scan should work now. Starting scan ...", flush=True)
            self.list_available_networks()
        except Exception as e:
            print('========= Error while activating Wifi scan: ', str(e), ' =========', flush=True)

    def list_available_networks(self) -> None:
        try:
            print(f"Scanning all available networks ...", flush=True)
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )

            networks = result.stdout.decode().splitlines()
            networks = [line for line in networks if line]  # filter empty lines

            if not networks:
                print('========= No networks found! =========', flush=True)
                return

            print(f"Found networks:", flush=True)
            for net in networks:
                ssid, signal = net.split(":", 1)
                if ssid:
                    print(f"  SSID: {ssid:<30} Signal: {signal}%", flush=True)
        except subprocess.CalledProcessError as e:
            print(f'========= Error while scanning: ', e.stderr.decode(), '=========', flush=True)
        except Exception as e:
            print(f"=========Unknown Error: {str(e)}=========", flush=True)

    def is_connected_to_ssid(self) -> bool:
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
            print('========= Error while checking the wifi connection: ', str(e), ' =========', flush=True)
            return False

    def connect_to_wifi(self):
        if self.ssid == None or self.password == None:
            print('You need to tell the constructor the SSID and password of the WIFI you are trying to connect to!', flush=True)
            raise Exception('You need to tell the constructor the SSID and password of the WIFI you are trying to connect to!')
        try:
            subprocess.run(
                ["nmcli", "dev", "wifi", "connect", self.ssid, "password", self.password],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"Successfully connected with {self.ssid} .", flush=True)
        except subprocess.CalledProcessError as e:
            print('========= Wifi connection failed: ', e.stderr.decode(), ' =========', flush=True)

    def get_ip_address(self) -> str:
        try:
            ip = subprocess.check_output(["hostname", "-I"]).decode().strip().split()[0]
            return ip
        except Exception as e:
            return "=========No IP-Address found========="

    def run(self):
        if self.ssid == None or self.password == None:
            print('You need to tell the constructor the SSID and password of the WIFI you are trying to connect to!',
                  flush=True)
            raise Exception(
                'You need to tell the constructor the SSID and password of the WIFI you are trying to connect to!')

        # Step1: Set wallaby to client mode
        if self.get_mode() != self.CLIENT_MODE:
            print("Change to client mode ...", flush=True)
            self.set_mode(self.CLIENT_MODE)

        # Step2: Connect to wifi
        if not self.is_connected_to_ssid():
            print(f"Not connected with {self.ssid} . Connecting ...", flush=True)
            self.connect_to_wifi()

        # Step3: show IP-Address
        ip = self.get_ip_address()
        print(f"Connected. IP-Address: {ip}", flush=True)