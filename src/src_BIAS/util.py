#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-07-28

try:
    import _kipr as k
    import inspect
    import time
    import os
    import threading
    from scipy.interpolate import interp1d
    from fileR import FileR  # selfmade
    from digital import Digital  # selfmade
    from light_sensor import LightSensor  # selfmade
    from distance_sensor import DistanceSensor  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

BASE_FOLDER = '/home/kipr/BotBall-data'
UTIL_FOLDER = BASE_FOLDER + '/util_files'
FILE_PATH = os.path.join(sys.path[0], __file__)
port_file_logable_function_name = None

def Port_File_Logging(func):
    def wrapper(*args, **kwargs):
        global port_file_logable_function_name
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])

        if FILE_PATH != module.__file__:  # another file than this one
            port_file_logable_function_name = func.__name__  # only allow port file functions to log if they are the ones who got called

        result = func(*args, **kwargs)
        return result

    return wrapper


class Util:
    def __init__(self,
                 Instance_button_front_right: Digital = None,
                 Instance_light_sensor_start: LightSensor = None,
                 Instance_distance_sensor: DistanceSensor = None):
        """
        Class for some extra functionality which does not fit into any class

        Args:
            Instance_button_front_right (Digital, optional): The button instance where the button is mounted on the front right of the robot (default: None)
            Instance_light_sensor_start (LightSensor, optional): The light sensor instance which is responsible for starting the program when the light turn on (at the competition during "hands-off") (default: None)
            Instance_distance_sensor (DistanceSensor, optional): The distance sensor instance where the button is mounted on of the robot (default: None)
        """
        self.button_fr = Instance_button_front_right
        self.light_sensor_start = Instance_light_sensor_start
        self.distance_sensor = Instance_distance_sensor

        self.file_manager = FileR(UTIL_FOLDER)
        self.port_file_name = 'port_file.txt'
        self.port_file_seperator = '{SEPERATOR}'
        self.isClose = False
        self.running_allowed = True


    # ======================== GETTER ========================
    @Port_File_Logging
    def get_port_file_entries(self, port_name: str = None, category: str = None, port_number: int = None):
        """
        Receive every data connected to every parameter

        Args:
            port_name (str, optional): If the name is correct, you can get the other two parameters or even combine this parameter with another parameter to get the last parameter by itself (default: None)
            category (str, optional): If there is such a category, you can get the other two parameters or even combine this parameter with another parameter to get the last parameter by itself (default: None)
            port_number (str, optional): If existing, you can get the other two parameters or even combine this parameter with another parameter to get the last parameter by itself (default: None)
            (HINT: if you leave all parameters empty, you will receive every entry!)

        Returns:
            Every combination of strings and integers, which are connected to the parameters

        Raises:
            FileNotFoundError: If there is no entry that got created
        """
        cat_exists = 1 if category else 0
        pname_exists = 1 if port_name else 0
        pnumber_exists = 1 if isinstance(port_number, int) else 0

        counter = cat_exists + pname_exists + pnumber_exists


        if not os.path.exists(self.file_manager.get_base_directory() + self.port_file_name):
            if port_file_logable_function_name == "get_port_file_entries":
                log('No entries created just yet', in_exception=True)
            raise FileNotFoundError('No entries created just yet')

        port_names = dict()
        entries = self.file_manager.reader(self.port_file_name).split('\n')

        for entry in entries:
            if entry:
                cat, pname, pnumber = entry.split(self.port_file_seperator)
                port_names[pname] = int(pnumber), cat

        if counter == 0:  # nothing is given -> everything is wanted
            return port_names  # return everything

        elif cat_exists and pnumber_exists:  # category and port number are given -> name is wanted
            for name, (number, cat) in port_names.items():
                if number == port_number and cat == category:
                    return name
            if port_file_logable_function_name == "get_port_file_entries":
                log(f'Category "{category}" with port number #{port_number}" does not exist', important=True)

        elif cat_exists and pname_exists:  # category and port name are given -> number is wanted
            for name, (number, cat) in port_names.items():
                if port_name == name and cat == category:
                    return number
            if port_file_logable_function_name == "get_port_file_entries":
                log(f'Category "{category}" with port name "{port_name}" does not exist', important=True)

        elif cat_exists:  # category is given -> name and numbers are wanted
            res = dict()
            for name, (number, cat) in port_names.items():
                if cat == category:
                    res[name] = number
            return res

        elif pnumber_exists and pname_exists:  # number and name given -> category is wanted
            for name, (number, cat) in port_names.items():
                if port_name == name and number == port_number:
                    return cat
            if port_file_logable_function_name == "get_port_file_entries":
                log(f'Port number #{port_number} with port name "{port_name}" does not exist', important=True)

        elif pnumber_exists:  # number is given -> category and port name is wanted
            res = dict()
            for name, (number, cat) in port_names.items():
                if port_number == number:
                    res[name] = cat
            return res

        elif pname_exists:  # name is given -> category and number is wanted
            if port_name in list(port_names.keys()):
                return port_names[port_name]
            if port_file_logable_function_name == "get_port_file_entries":
                log(f'Port name "{port_name}" does not exist', important=True)


    @Port_File_Logging
    def get_port_file_categories(self) -> set[str]:
        """
        Receive all categories you created

        Args:
            None

        Returns:
            set[
                str: every category there is
            ]: All categories

        Raises:
            FileNotFoundError: If there is no entry that got created
        """
        if not os.path.exists(self.port_file_name):
            if port_file_logable_function_name == "get_port_file_categories":
                log('No entries created just yet', in_exception=True)
            raise FileNotFoundError('No entries created just yet')

        categories = set()
        entries = self.file_manager.reader(self.port_file_name).split('\n')

        for entry in entries:
            if entry:
                cat, pname, pnumber = entry.split(self.port_file_seperator)
                categories.add(cat)

        return categories


    @Port_File_Logging
    def get_port_file_names(self) -> set[str]:
        """
        Receive all unique names that got created

        Args:
            None

        Returns:
            set[
                str: The names of every saved port
            ]: All names

        Raises:
            FileNotFoundError: If there is no entry that got created
        """
        if not os.path.exists(self.port_file_name):
            if port_file_logable_function_name == "get_port_file_names":
                log('No entries created just yet', in_exception=True)
            raise FileNotFoundError('No entries created just yet')

        names = set()
        entries = self.file_manager.reader(self.port_file_name).split('\n')

        for entry in entries:
            if entry:
                cat, pname, pnumber = entry.split(self.port_file_seperator)
                names.add(pname)

        return names

    # ======================== SETTER ========================
    def set_instance_distance_sensor(self, Instance_distance_sensor: DistanceSensor) -> None:
        """
        create or overwrite the existence of the distance sensor

        Args:
            Instance_distance_sensor (DistanceSensor): the instance of the distance sensor

        Returns:
            None
        """
        self.distance_sensor = Instance_distance_sensor

    def set_instance_light_sensor_start(self, Instance_light_sensor_start: LightSensor) -> None:
        """
        create or overwrite the existence of the start light sensor

        Args:
            Instance_light_sensor_start (LightSensor): the instance of the start light sensor

        Returns:
            None
        """
        self.light_sensor_start = Instance_light_sensor_start

    def set_instance_button_fr(self, Instance_button_front_right: Digital) -> None:
        """
        create or overwrite the existence of the front right button

        Args:
            Instance_button_front_right (Digital): the instance of the front right button

        Returns:
            None
        """
        self.button_fr = Instance_button_front_right


    # ======================== CHECKER ========================
    def check_instance_distance_sensor(self) -> bool:
        """
        inspect the existence of the distance sensor

        Args:
            None

        Returns:
            bool: if there is an instance of the distance sensor in existence

        Raises:
            TypeError: If the distance sensor is not initialized
        """
        if not isinstance(self.distance_sensor, DistanceSensor):
            log('Distance sensor is not initialized!', in_exception=True)
            raise TypeError('Distance sensor is not initialized!')
        return True

    def check_instance_light_sensor_start(self) -> bool:
        """
        inspect the existence of the start light sensor

        Args:
            None

        Returns:
            bool: if there is an instance of the start light sensor in existence

        Raises:
            TypeError: If the light sensor for the start is not initialized
        """
        if not isinstance(self.light_sensor_start, LightSensor):
            log('Light sensor start is not initialized!', in_exception=True)
            raise TypeError('Light sensor start is not initialized!')
        return True

    def check_instance_button_fr(self) -> bool:
        """
        inspect the existence of the front right button

        Args:
            None

        Returns:
            bool: if there is an instance of the button front right in existence

        Raises:
            TypeError: If the button front right is not initialized
        """
        if not isinstance(self.button_fr, Digital):
            log('Button front right is not initialized!', in_exception=True)
            raise TypeError('Button front right is not initialized!')
        return True

    # ======================== PUBLIC METHODS =======================
    def wait_til_moved(self, waiting_millis: int, max_waiting_millis: int = 8000) -> None:
        """
        wait until the wallaby got touched a little bit

        Args:
            waiting_millis (int): the total time it should wait
            max_waiting_millis (int, optional): the maximum time it is allowed to wait (default: 8000)

        Returns:
            None
        """
        startTime = k.seconds()
        touched: bool = False
        while (k.gyro_z() <= 20 and k.gyro_z() >= -20) and k.seconds() - startTime < max_waiting_millis / 1000:
            print(waiting_millis, flush=True)
            k.msleep(1)
            if waiting_millis > 0:
                waiting_millis -= 1
            if k.gyro_z() >= 20 or k.gyro_z() <= -20:  # @TODO -> check, if that is still accurate
                touched = True
        if touched:
            log('touched')
            k.msleep(waiting_millis)
        if k.seconds() - startTime > max_waiting_millis / 1000:
            log('max time reached!')

    def wait_for_light(self) -> None:  # you should frankly use the kipr made function if you use this for starting the robot -> more consistent
        """
        waits for the light to flash once (you should rather use the wait_for_light function of kipr)

        Args:
            None

        Returns:
            None
        """
        self.check_instance_light_sensor_start()
        while self.light_sensor_start.current_value() > 2000:
            continue

    def wait_for_button(self) -> None:
        """
        sleep as long as there is no button press

        Args:
            None

        Returns:
            None
        """
        self.check_instance_button_fr()
        log('waiting for button FR...')
        while not self.button_fr.is_pressed():
            continue


    def toggle_local_test_variable(self) -> str:
        """
        Variable that toggles between "''" and "'1'". Can be useful because for test purpose you might want to change something every second run

        Args:
            None

        Returns:
            str:
                '': Empty string, which can be interpreted as False
                '1': String with some content that can be interpreted as True
        """
        std_msg = ''
        file_name = '/local_test_variable.txt'
        if not os.path.exists(file_name):
            self.file_manager.writer(file_name, 'w', std_msg)
            return std_msg
        else:
            text = self.file_manager.reader(file_name)
            if text != std_msg:
                new_msg = std_msg
            else:
                new_msg = '1'
            self.file_manager.writer(file_name, 'w', new_msg)
            return new_msg


    @Port_File_Logging
    def create_port_file_entry(self, port_name: str, category: str, port_number: int) -> None:
        """
        Create a global file to access everywhere the same port numbers. Also does not get deleted when re-installing the library

        Args:
            port_name (str): A unique name across all created entries. Using this variable alone you can get the access to the stored port information (category and port number) everywhere by using my library
            category (str): Similarities of some ports (e.g.: 'Motor' for all motors)
            port_number (int): The port which the category is plugged into (e.g.: category: 'Motor' ; port (of the motor): 0)

        Returns:
            None, but writes into a file
        """
        if not os.path.exists(self.port_file_name):
            self.file_manager.writer(self.port_file_name, 'w', '')

        if not self.exist_port_file_entry(port_name=port_name) and not self.exist_port_file_entry(category=category, port_number=port_number):
            msg = category + self.port_file_seperator + port_name + self.port_file_seperator + str(port_number) + '\n'
            self.file_manager.writer(self.port_file_name, 'a', msg)
            log_msg = f'Successfully added new entry: {port_name}'
        else:
            entries = self.get_port_file_entries()  # dict
            self.file_manager.cleaner(self.port_file_name)
            for name, (number, cat) in entries.items():
                if name == port_name:
                    number = port_number
                    cat = category

                elif number == port_number and cat == category:
                    name = port_name

                msg = cat + self.port_file_seperator + name + self.port_file_seperator + str(number) + '\n'
                self.file_manager.writer(self.port_file_name, 'a', msg)

            log_msg = f'Successfully overwritten old entry with port name "{port_name}" to category "{category}" and port number #{port_number}'

        if port_file_logable_function_name == "create_port_file_entry":
            log(log_msg)


    @Port_File_Logging
    def remove_port_file_entry(self, port_name: str = None, category: str = None, port_number: int = None) -> None:
        """
        Remove a previously stored port entry from the file

        Args:
            port_name (str, optional): Since the name is unique, you can only use this name to remove the entry (default: None)
            category (str, optional): If you do not remember the name, the category and port number got you covered (you need to at least know these two) (default: None)
            port_number (str, optional): If you do not remember the name, the category and port number got you covered (you need to at least know these two) (default: None)

        Returns:
            None, but tells you if removing the entry was successful or not

        Raises:
            ValueError: If there is too less information about an entry given
        """
        if not port_name and (not category or not isinstance(port_number, int)):
            if port_file_logable_function_name == "remove_port_file_entry":
                log('You need to either know the port name or at least two other parameters!', in_exception=True)
            raise ValueError('You need to either know the port name or at least two other parameters!')

        if port_name:
            existing = self.exist_port_file_entry(port_name=port_name)

        else:  # category and isinstance(port_number, int):  got basically checked
            existing = self.exist_port_file_entry(category=category, port_number=port_number)

        if existing:
            entries = self.get_port_file_entries()  # dict
            self.file_manager.cleaner(self.port_file_name)
            for name, (number, cat) in entries.items():
                if port_name and name == port_name:
                    found = True
                elif (category and isinstance(port_number, int)) and (number == port_number and cat == category):
                    found = True
                else:
                    found = False

                if not found:
                    msg = cat + self.port_file_seperator + name + self.port_file_seperator + str(number) + '\n'
                    self.file_manager.writer(self.port_file_name, 'a', msg)
                else:
                    port_name = name
                    category = cat
                    port_number = number

            if port_name:
                existing = self.exist_port_file_entry(port_name=port_name)

            else:  # category and isinstance(port_number, int):
                existing = self.exist_port_file_entry(category=category, port_number=port_number)

            if not existing:
                if port_file_logable_function_name == "remove_port_file_entry":
                    log(f'Successfully removed entry with port name "{port_name}".')
            elif port_name and not self.exist_port_file_entry(port_name=port_name):
                if port_file_logable_function_name == "remove_port_file_entry":
                    log(f'Failed to remove entry - category: "{category}", port number: #{port_number}', important=True)
            else:
                if port_file_logable_function_name == "remove_port_file_entry":
                    log(f'Failed to remove entry - port name: "{port_name}"', important=True)
        else:
            if port_file_logable_function_name == "remove_port_file_entry":
                if port_name:
                    log_msg = f'Entry with name "{port_name}" does not exist'
                else:
                    log_msg = f'Entry with category "{category}" and port number #{port_number} does not exist'
                log(log_msg, important=True)



    @Port_File_Logging
    def exist_port_file_entry(self, port_name: str = None, category: str = None, port_number: int = None) -> bool:
        """
        Tells you if the entry already exists or not

        Args:
            port_name (str, optional): Since the name is unique, you can only use this name to check for the entry (default: None)
            category (str, optional): If you do not remember the name, the category and port number got you covered (you need to at least know these two) (default: None)
            port_number (str, optional): If you do not remember the name, the category and port number got you covered (you need to at least know these two) (default: None)

        Returns:
            bool: If there was a similar entry found (True -> you can either check for the port name OR the category and port number) or not (False)

        Raises:
            ValueError: If there is too less information about an entry given
        """
        if not port_name and (not category or not isinstance(port_number, int)):
            if port_file_logable_function_name == "exist_port_file_entry":
                log('You need to either know the port name or at least two other parameters!', in_exception=True)
            raise ValueError('You need to either know the port name or at least two other parameters!')

        try:
            if port_name:
                entry = self.get_port_file_entries(port_name=port_name)
                return True if isinstance(entry[0], int) and entry[1] else False

            if category and isinstance(port_number, int):
                entry = self.get_port_file_entries(category=category, port_number=port_number)
                return True if entry else False

            return False

        except Exception as e:
            return False

    def shutdown_wombat(self) -> None:
        """
        Shutting down the controller

        Args:
            None

        Returns:
            None
        """
        subprocess.run(['shutdown', '-h', 'now'])

    def reboot_wombat(self) -> None:
        """
        Rebooting the controller

        Args:
            None

        Returns:
            None

        """
        subprocess.run(['shutdown', '-r', 'now'])
