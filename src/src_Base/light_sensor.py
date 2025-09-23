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
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


class LightSensor:
    def __init__(self, Port:int, value_white : int =None, value_black : int=None, bias : int=500):
        self.port = Port
        self.val_white = value_white
        self.val_black = value_black
        self.bias = bias
        self.BIAS_FOLDER = '/usr/lib/bias_files'

    # ======================== Getter =======================

    def get_value_black(self, calibrated: bool = False) -> int:
        '''
       get the value of the light sensor when it should tell you that it sees black

       Args:
           None

      Returns:
           value where it should recognise the white color (int)
       '''
        avg = 0
        file_name = os.path.join(self.BIAS_FOLDER, 'light_sensor_black.txt')
        try:
            temp_black = file_Manager.reader(file_name)
            if calibrated:
                avg = (float(temp_black) + self.val_black) // 2
                file_Manager.writer(file_name, 'w', avg)
            else:
                avg = float(temp_black)
            return avg
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def get_value_white(self, calibrated: bool = False) -> int:
        '''
         get the value of the light sensor when it should tell you that it sees white

         Args:
             None

        Returns:
             value where it should recognise the black color (int)
        '''
        avg = 0
        file_name = os.path.join(self.BIAS_FOLDER, 'light_sensor_white.txt')
        try:
            temp_white = file_Manager.reader(file_name)
            if calibrated:
                avg = (float(temp_white) + self.val_white) // 2
                file_Manager.writer(file_name, 'w', avg)
            else:
                avg = float(temp_white)
            return avg
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
        self.val_white = value

    def set_value_white(self, value:int) -> None:
        '''
        set the value of the light sensor when it should tell you that it sees white

        Args:
            value (int): the new value to see white

       Returns:
            None
        '''
        self.val_black = value


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
