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
    import math
    import _kipr as k
    from fileR import FileR  # selfmade
    from analog import Analog  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


class LightSensor(Analog):
    def __init__(self, position: str, port: int, value_white: int = None, value_black: int = None, bias: int = None):
        '''
        Class for the analog light and brightness sensor. Both work similar, so they get the same class.

        Args:
            position (str): where it is located. This is for the file creation, so you can use the same values across different users and files. Keep the name the same for the same position of the sensor
            port (int): the integer value from where it is plugged in (the hardware) e.g.: 1; 3; 4; 2.
            value_white (int, optional): the value at which the sensor should detect that it is seeing white (exclusive bias) (default: calibrated value)
            value_black (int, optional): the value at which the sensor should detect that it is seeing black (exclusive bias) (default: calibrated value)
            bias (int, optional): the amount of error that you allow from the light sensor. Higher value means it is more forgiving. Integer value is required. e.g.: 150; 500; 300
        '''

        super().__init__(port)
        self.position = position
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
        if self.bias is None:
            self.bias = self._calibrate_bias()

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
            return self.file_manager.reader(file_path, 'int')
        return None  # You can not raise an Exception here, since if you did not calibrate in the beginning, then you will always receive an exception

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
            return int(self.file_manager.reader(file_path, 'int'))
        return None  # You can not raise an Exception here, since if you did not calibrate in the beginning, then you will always receive an exception

    def _calibrate_bias(self) -> Optional[int]:
        '''
        automatic calibration of the bias for the light sensor. It will calculate a value from 150 - 500. The bias calculates itself between the light and black value. The higher the difference between those values, the higher the bias.

        Args:
            None

        Returns:
            int: actual calibrated bias
        '''
        if self.val_white is None or self.val_black is None:
            return None  # You can not raise an Exception here, since if you did not calibrate in the beginning, then you will always receive an exception

        diff = self.get_value_black() - self.get_value_white()
        if diff < 0:
            log('Black value needs to be higher than the white value. Since this is not the case, this means that you did something wrong in setting the light values!', in_exception=True)
            raise ValueError('Black value needs to be higher than the white value. Since this is not the case, this means that you did something wrong in setting the light values!')
        elif diff < 400:
            log('The difference between the value of the black- and white light sensor is too small. Please consider either dropping the sensors lower (more near to the floor) or replacing your sensors!', in_exception=True)
            raise ValueError('The difference between the value of the black- and white light sensor is too small. Please consider either dropping the sensors lower (more near to the floor) or replacing your sensors!')

        return int(155.5 * math.log(diff) - 782)  # value between ~150 and ~500

    # ======================== Save-Methods =======================

    def save_value_black(self, measured_value: int = None) -> None:
        '''
        Saves the black value of the light sensor into a file

        Args:
            measured_value (int): The value that should be averaged and written into the file

        Returns:
            None
        '''
        if measured_value is None:
            measured_value = self.current_value()

        file_name = os.path.join(self.BIAS_FOLDER, f'{self.std_black_file_name + self.position}.txt')
        try:
            if os.path.exists(file_name):
                old_val = int(self.file_manager.reader(file_name))
                measured_value = (old_val + measured_value) // 2
            self.file_manager.writer(file_name, 'w', int(measured_value))
            self.val_black = int(measured_value)
        except Exception as e:
            log(str(e), in_exception=True)

    def save_value_white(self, measured_value: int = None) -> None:
        '''
        Saves the white value of the light sensor into a file

        Args:
            measured_value (int, optional): The value that should be averaged and written into the file

        Returns:
            None
        '''
        if measured_value is None:
            measured_value = self.current_value()

        file_name = os.path.join(self.BIAS_FOLDER, f'{self.std_white_file_name + self.position}.txt')
        try:
            if os.path.exists(file_name):
                old_val = int(self.file_manager.reader(file_name))
                measured_value = (old_val + measured_value) // 2
            self.file_manager.writer(file_name, 'w', int(measured_value))
            self.val_white = int(measured_value)
        except Exception as e:
            log(str(e), in_exception=True)

    # ======================== Getter =======================

    def get_value_black(self) -> int:
        '''
         get the value of the light sensor when it should tell you that it sees black

         Args:
             None

        Returns:
             int: value for the sensor to see black (exclusive bias)
        '''
        if isinstance(self.val_black, int):
            return self.val_black
        file_name = os.path.join(self.BIAS_FOLDER, f'light_sensor_black_{self.position}.txt')
        try:
            val = int(self.file_manager.reader(file_name))
            self.val_black = val
            return val
        except Exception as e:
            log(str(e), in_exception=True)

    def get_value_white(self) -> int:
        '''
         get the value of the light sensor when it should tell you that it sees white

         Args:
             None

        Returns:
             int: value for the sensor to see white (exclusive bias)
        '''
        if isinstance(self.val_white, int):
            return self.val_white
        file_name = os.path.join(self.BIAS_FOLDER, f'light_sensor_white_{self.position}.txt')
        try:
            val = int(self.file_manager.reader(file_name))
            self.val_white = val
            return val
        except Exception as e:
            log(str(e), in_exception=True)

    def get_value_black_bias(self) -> int:
        '''
       get the value of the light sensor when it should tell you that it sees black with the bias subtracted to it

       Args:
           None

       Returns:
           int: value for the sensor to see black (inclusive bias)
       '''
        if isinstance(self.val_black, int):
            return self.val_black - self.bias
        file_name = os.path.join(self.BIAS_FOLDER, f'light_sensor_black_{self.position}.txt')
        try:
            val = int(self.file_manager.reader(file_name))
            self.val_black = val
            return val - self.bias
        except Exception as e:
            log(str(e), in_exception=True)

    def get_value_white_bias(self) -> int:
        '''
         get the value of the light sensor when it should tell you that it sees white with the bias added to it

         Args:
             None

        Returns:
             int: value for the sensor to see white (inclusive bias)
        '''
        if isinstance(self.val_white, int):
            return self.val_white + self.bias
        file_name = os.path.join(self.BIAS_FOLDER, f'light_sensor_white_{self.position}.txt')
        try:
            val = int(self.file_manager.reader(file_name))
            self.val_white = val
            return val + self.bias
        except Exception as e:
            log(str(e), in_exception=True)


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
    def sees_black(self) -> bool:
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

    def sees_white(self) -> bool:
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
