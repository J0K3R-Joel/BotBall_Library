#!/usr/bin/python3
import os, sys
from typing import Tuple, Any

sys.path.append("/usr/lib")

from logger import *

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-07-28

try:
    import _kipr as k
    from typing import *
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


class Digital:
    def __init__(self, Port : int):
        self.port = Port
        self.last_state = 0  # initialized while the button is not pressed
        self.pressed_at = 0  # to know when the button was first pressed
        self.state_timer = 0  # initialized while the button is not pressed
        self.got_pressed = False


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
        res = k.digital(self.port) == 1

        if res:
            self.got_pressed = True

        return res

    def state_changed(self, recognise_press: bool = False) -> bool:
        '''
        tells you, if the state of the button got changed since the last call

        Args:
            recognise_press (bool, optional): If the class should count a button hit (True) or not (False). This is only for the time_end function.

       Returns:
            If the state got changed (True) or not (False)
        '''
        curr_state = self.current_value()

        if recognise_press and curr_state:
            self.got_pressed = True

        if curr_state != self.last_state:
            self.last_state = curr_state
            return True

        return False

    def seperator(self, until_pressed: bool, millis_func_dict: dict = None) -> int:
        num = 1 if until_pressed else 0
        times_sorted = sorted(millis_func_dict.keys(), key=int, reverse=True)
        start_time = k.millis()

        while not self.is_pressed() == num:
            continue

        total_time = int(k.millis() - start_time)

        if millis_func_dict is None:
            return total_time

        #for time in times_sorted:
         #   if total_time > int(time):
                # callable überprüfen, wenn ja dict an der stelle mit der funktion ausführen. Wenn nicht callable, dann exception


    def time_begin(self) -> None:
        '''
        remembers the state it is currently in and the time where the function got called

        Args:
            None

       Returns:
            None
        '''
        self.state_timer = self.current_value()
        self.got_pressed = False
        self.pressed_at = k.seconds()

    def time_end(self, end_timer: bool = True, raiser_last_pressed: str = '') -> tuple[bool, bool, int]:
        '''
        tells you how the time since the last time when the beginner function was called. The state has to be changed since the last beginner function was called

        Args:
            end_timer (bool, optional): If the timer should reset to 0 (default: True) or continue counting (False)
            raiser_last_pressed (str, optional): If you want an exception, warning or just do not care that the last time it got pressed the state did not chance (default: '' -> do not care)

       Returns:
            tuple:
                bool: did the state change since the last call (True) or is it the same (False)
                bool: did the state changed since the last time_begin call (True) or is it the same (False)
                int: the time between this function is called and the last time the begin function was called
        '''
        if self.pressed_at == 0:
            log(f'If you want to know how long the button was (not) pressed, please initialize the beginning of the time to count!', in_exception=True)
            raise RuntimeError('If you want to know how long the button was (not) pressed, please initialize the beginning of the time to count!')


        current_v = self.current_value()
        state_changed = self.state_timer == current_v
        warn_lst = ['warning', 'info']
        exc_lst = ['error', 'exception', 'interrupt']
        res = k.seconds() - self.pressed_at
        total_changed = self.got_pressed

        self.pressed_at = 0 if end_timer else self.pressed_at

        if not state_changed and raiser_last_pressed:
            if raiser_last_pressed.lower() in warn_lst:
                log(f'The button is in the same state as it was when the beginner function got called! Time counting still continues though...', in_exception=True)

            elif raiser_last_pressed.lower() in exc_lst:
                log(f'The button is in the same state as it was when the beginner function got called! Time counting still continues though...',in_exception=True)
                raise RuntimeError('The button is in the same state as it was when the beginner function got called! Time counting still continues though...')

            else:
                log(f'raiser_last_pressed can only contain either anything of {warn_lst} or anything of {exc_lst}.', in_exception=True)
                raise ValueError(f'raiser_last_pressed can only contain either anything of {warn_lst} or anything of {exc_lst}.')

        return state_changed, total_changed, res
