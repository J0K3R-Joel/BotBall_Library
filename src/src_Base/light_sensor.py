#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import log  # selfmade

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

    # ======================== Getter =======================

    def get_value_black(self) -> int:
        '''
       get the value of the light sensor when it should tell you that it sees black

       Args:
           None

      Returns:
           value where it should recognise the white color (int)
       '''
        return self.val_white

    def get_value_white(self) -> int:
        '''
         get the value of the light sensor when it should tell you that it sees white

         Args:
             None

        Returns:
             value where it should recognise the black color (int)
         '''
        return self.val_black

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
        return self.current_value() >= self.val_white - self.bias

    def sees_White(self) -> bool:
        '''
        tells you, if the sensor sees white (True) or not (False)

        Args:
            None

       Returns:
            if it sees white (True) or if it can not recognise it (Falsa)
        '''
        return self.current_value() <= self.val_black + self.bias
