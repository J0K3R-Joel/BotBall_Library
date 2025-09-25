#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-07-28

try:
    from typing import Optional
    import _kipr as k
    from fileR import FileR  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


class LightSensor:
    def __init__(self, position: str, Port:int, value_white : int =None, value_black : int=None, bias : int=500):  # position is the placement, where it got positioned -> this is for the text average calculation
        self.position = position
        self.port = Port
        self.val_white = value_white
        self.val_black = value_black
        self.bias = bias
        self.BIAS_FOLDER = '/usr/lib/bias_files'
        self.std_white_file_name = 'light_sensor_white_'
        self.std_black_file_name = 'light_sensor_black_'
        self.file_manager = FileR()
        
        if self.val_white is None:
            self.val_white = self._white_load_from_file()
        if self.val_black is None:
            self.val_black = self._black_load_from_file()

    # ======================== Helper =======================
    def _black_load_from_file(self) -> Optional[int]:
        '''
        Loads the last average value of black

        Args:
            None

        Returns:
            int | None: If the file exists, it returns an int, otherwise it returns None
        '''
        file_path = os.path.join(self.BIAS_FOLDER, self.std_black_file_name + self.position + '.txt')
        if os.path.exists(file_path):
            return int(self.file_manager.reader(file_path))
        return None

    def _white_load_from_file(self) -> Optional[int]:
        '''
        Loads the last average value of white

        Args:
            None

        Returns:
            int | None: If the file exists, it returns an int, otherwise it returns None
        '''
        file_path = os.path.join(self.BIAS_FOLDER, self.std_white_file_name + self.position + '.txt')
        if os.path.exists(file_path):
            return int(self.file_manager.reader(file_path))
        return None


    # ======================== Save-Methods =======================

    def save_value_black(self, measured_value: int) -> None:
        '''
        Saves the black value of the light sensor into a file

        Args:
            measured_value (int): The value that should be averaged and written into the file

        Returns:
            None
        '''
        file_name = os.path.join(self.BIAS_FOLDER, f'{self.std_black_file_name + self.position}.txt')
        try:
            if os.path.exists(file_name):
                old_val = int(self.file_manager.reader(file_name))
                measured_value = (old_val + measured_value) // 2
            self.file_manager.writer(file_name, 'w', int(measured_value))
            self.val_black = int(measured_value)
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def save_value_white(self, measured_value: int) -> None:
        '''
        Saves the white value of the light sensor into a file

        Args:
            measured_value (int): The value that should be averaged and written into the file

        Returns:
            None
        '''
        file_name = os.path.join(self.BIAS_FOLDER, f'{self.std_white_file_name + self.position}.txt')
        try:
            if os.path.exists(file_name):
                old_val = int(self.file_manager.reader(file_name))
                measured_value = (old_val + measured_value) // 2
            self.file_manager.writer(file_name, 'w', int(measured_value))
            self.val_white = int(measured_value)
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    # ======================== Getter =======================

    def get_value_black(self) -> int:
        '''
       get the value of the light sensor when it should tell you that it sees black

       Args:
           None

      Returns:
           value where it should recognise the white color (int)
       '''
        if isinstance(self.val_black, int):
            return self.val_black
        file_name = os.path.join(self.BIAS_FOLDER, f'light_sensor_black_{self.position}.txt')
        try:
            val = int(self.file_manager.reader(file_name))
            self.val_black = val
            return val
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def get_value_white(self) -> int:
        '''
         get the value of the light sensor when it should tell you that it sees white

         Args:
             None

        Returns:
             value where it should recognise the black color (int)
        '''
        if isinstance(self.val_white, int):
            return self.val_white
        file_name = os.path.join(self.BIAS_FOLDER, f'light_sensor_white_{self.position}.txt')
        try:
            val = int(self.file_manager.reader(file_name))
            self.val_white = val
            return val
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def get_bias(self) -> int:
        '''
         get the kind of error that is allowed

         Args:
             None

        Returns:
             bias of the on and off value (int)
         '''
        return self.bias


    # ======================== Setter =======================
    def auto_set_values(self) -> None:
        '''
        Automatically reads the files and sets the values

        Args:
            None

        Returns:
            None
        '''
        self.set_value_black(self.get_value_black())
        self.set_value_white(self.get_value_white())


    def set_value_black(self, value:int) -> None:
        '''
        set the value of the light sensor when it should tell you that it sees black

        Args:
            value (int): the new value to see black

       Returns:
            None
        '''
        self.val_black = value

    def set_value_white(self, value:int) -> None:
        '''
        set the value of the light sensor when it should tell you that it sees white

        Args:
            value (int): the new value to see white

       Returns:
            None
        '''
        self.val_white = value


    # ======================== Normal methods =======================

    def current_value(self) -> int:
        '''
        get the current value of the light sensor

        Args:
            None

       Returns:
            current value of the assigned analog port (int)
        '''
        return k.analog(self.port)

    def sees_Black(self) -> bool:
        '''
        tells you, if the sensor sees black (True) or not (False)

        Args:
            None

       Returns:
            if it sees black (True) or if it can not recognise it (Falsa)
        '''
        if not isinstance(self.val_white, int):
            log('You need to set the black value before trying to see if it is white', in_exception=True, important=True)
            raise TypeError('You need to set the white value before trying to see if it is black')
        return self.current_value() >= self.val_white + self.bias

    def sees_White(self) -> bool:
        '''
        tells you, if the sensor sees white (True) or not (False)

        Args:
            None

       Returns:
            if it sees white (True) or if it can not recognise it (Falsa)
        '''
        if not isinstance(self.val_black, int):
            log('You need to set the black value before trying to see if it is white', in_exception=True, important=True)
            raise TypeError('You need to set the black value before trying to see if it is white')
        return self.current_value() <= self.val_black - self.bias
