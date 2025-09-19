#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-07-28

try:
    import _kipr as k
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


class Digital:
    def __init__(self, Port : int):
        self.port = Port
        self.last_state = 0  # initialized while the button is not pressed
        self.pressed_at = 0  # to know when the button was first pressed
        self.state_timer = 0  # initialized while the button is not pressed


    # ======================== PUBLIC METHODS ========================

    def current_value(self) -> int:
        '''
        get the current value of the digital Port

        Args:
            None

       Returns:
            Current digital output (int)
        '''
        return k.digital(self.port)

    def is_pressed(self) -> bool:
        '''
        tells you, if the button is pressed (True) or not (False)

        Args:
            None

       Returns:
            If the digital Port is set to 1 at the moment (bool)
        '''
        return k.digital(self.port) == 1

    def state_changed(self) -> bool:
        '''
        tells you, if the state of the button got changed since the last call

        Args:
            None

       Returns:
            If the state got changed (True) or not (False)
        '''
        curr_state = self.current_value()

        if curr_state != self.last_state:
            self.last_state = curr_state
            return True

        return False

    def time_begin(self) -> None:
        '''
        remembers the state it is currently in and the time where the function got called

        Args:
            None

       Returns:
            None
        '''
        self.state_timer = self.current_value()
        self.pressed_at = k.seconds()

    def time_end(self) -> int:
        '''
        tells you how the time since the last time when the beginner function was called. The state has to be changed since the last beginner function was called

        Args:
            None

       Returns:
            the time between this function is called and the last time the beginnemr function was called
        '''
        if self.pressed_at == 0:
            log(f'If you want to know how long the button was (not) pressed, please initialize the beginning of the time to count!', in_exception=True)
            raise Exception('If you want to know how long the button was (not) pressed, please initialize the beginning of the time to count!')

        if self.state_timer == self.current_value():
            log(f'The button is in the same state as it was when the beginner function got called! Time counting still continues though...', in_exception=True)
            raise Exception('The button is in the same state as it was when the beginner function got called! Time counting still continues though...')


        return k.seconds() - self.pressed_at






