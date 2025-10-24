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
    from digital import Digital  # selfmade
    from light_sensor import LightSensor  # selfmade
    from distance_sensor import DistanceSensor  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


class Util:
    def __init__(self,
                 Instance_button_front_right: Digital = None,
                 Instance_light_sensor_start: LightSensor = None,
                 Instance_distance_sensor: DistanceSensor = None):

        self.button_fr = Instance_button_front_right
        self.light_sensor_start = Instance_light_sensor_start
        self.distance_sensor = Instance_distance_sensor

        self.isClose = False
        self.running_allowed = True


    # ======================== SET INSTANCES ========================

    def set_instance_distance_sensor(self, Instance_distance_sensor: DistanceSensor) -> None:
        '''
        create or overwrite the existance of the distance sensor

        Args:
            Instance_distance_sensor (DistanceSensor): the instance of the distance sensor

       Returns:
            None
        '''
        self.distance_sensor = Instance_distance_sensor

    def set_instance_light_sensor_start(self, Instance_light_sensor_start: LightSensor) -> None:
        '''
        create or overwrite the existance of the start light sensor

        Args:
            Instance_light_sensor_start (LightSensor): the instance of the start light sensor

       Returns:
            None
        '''
        self.light_sensor_start = Instance_light_sensor_start

    def set_instance_button_fr(self, Instance_button_front_right: Digital) -> None:
        '''
        create or overwrite the existance of the fr button

        Args:
            Instance_button_front_right (Digital): the instance of the front right button

       Returns:
            None
        '''
        self.button_fr = Instance_button_front_right

    # ======================== CHECK INSTANCES ========================

    def check_instance_distance_sensor(self) -> bool:
        '''
        inspect the existance of the distance sensor

        Args:
            None

       Returns:
            if there is an instance of the distance sensor in existance
        '''
        if not isinstance(self.distance_sensor, DistanceSensor):
            log('Distance sensor is not initialized!', in_exception=True)
            raise TypeError('Distance sensor start is not initialized!')
        return True

    def check_instance_light_sensor_start(self) -> bool:
        '''
        inspect the existance of the start light sensor

        Args:
            None

       Returns:
            if there is an instance of the start light sensor in existance
        '''
        if not isinstance(self.light_sensor_start, LightSensor):
            log('Light sensor start is not initialized!', in_exception=True)
            raise TypeError('Light sensor start is not initialized!')
        return True

    def check_instance_button_fr(self) -> bool:
        '''
        inspect the existance of the fr button

        Args:
            None

       Returns:
            if there is an instance of the button fr in existance
        '''
        if not isinstance(self.button_fr, Digital):
            log('Button front right is not initialized!', in_exception=True)
            raise TypeError('Button front right is not initialized!')
        return True

    # ======================== Normal methods =======================

    def stop_runner(self) -> None:
        '''
        stops every wait function if needed (even though they are in a thread)

        Args:
            None

        Returns:
            None
        '''
        self.running_allowed = False

    def wait_til_moved(self, waiting_millis: int, max_waiting_millis: int = 8000) -> None:
        '''
        wait until the wallaby got touched a little bit

        Args:
            waiting_millis (int): the total time it should wait
            max_waiting_millis (int, optional): the maximum time it is allowed to wait (default: 8000)

        Returns:
            None
        '''
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

    def wait_for_light(self) -> None:  # eher die von kipr verwenden
        '''
        waits for the light to flash once (you should rather use the wait_for_light function of kipr)

        Args:
            None

       Returns:
            None
        '''
        self.check_instance_light_sensor_start()
        while self.light_sensor_start.current_value() > 2000:
            continue

    def wait_for_button(self) -> None:
        '''
        sleep as long as there is no button press

        Args:
            None

       Returns:
            None
        '''
        self.check_instance_button_fr()
        log('waiting for button FR...')
        while not self.button_fr.is_pressed():
            continue