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


    def wait_til_distance_reached(self, mm_to_object: int, sideways: bool = False) -> bool:
        # distance in mm
        '''
        do nothing except wait until it detects an object that is in the specified mm range (the object has to come closer, since this function only waits until somethings gets closer)
        HINT: The higher the value of the mm_to_object, the less consistent

        Args:
            mm_to_object (int): the distance (in mm) between the distance sensor and the object in front of the sensor (95 - 800mm)
            sideways (bool, optional): If True, indicates that the robot is moving sideways instead of forward. This changes the distance handling logic and which sensor calibration table is used.

        Returns:
            desired mm captured
        '''
        self.check_instance_distance_sensor()
        if mm_to_object > 800 or mm_to_object < 95:
            log('You can only put a value in range of 100 - 800 for the distance parameter!', in_exception=True, important=True)
            raise ValueError(
                'wait_til_distance_reached() Exception: You can only put a value in range of 100 - 800 for the distance parameter!')

        self.isClose = False
        self.running_allowed = True
        val = mm_to_object

        # being far away
        far_sensor_values = [500, 530, 600, 670, 715, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800,
                             1900,
                             2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900]
        far_distances_mm = [800, 700, 600, 580, 540, 480, 400, 360, 320, 285, 260, 235, 220, 205, 190, 180, 170,
                            160, 150, 140, 135, 130, 125, 120, 115, 110, 100]
        combination_far = dict(zip(far_distances_mm, far_sensor_values))
        next_step_far = min(combination_far, key=lambda x: abs(x - val))
        next_value_far = combination_far[next_step_far]

        # being close
        close_sensor_values = [1500, 1600, 1650, 1700, 1750, 1850, 1950, 2050, 2150, 2300, 2450, 2650, 2850, 2900]
        close_distances_mm = [220, 210, 200, 190, 180, 170, 160, 150, 140, 130, 120, 110, 100, 95]
        combination_close = dict(zip(close_distances_mm, close_sensor_values))
        next_step_close = min(combination_close, key=lambda x: abs(x - val))
        next_value_close = combination_close[next_step_close]

        def distance_stopper(far_away: bool):
            self.isClose = False
            tolerance = val / 10  # has to be 90% accurate
            try:
                if far_away:
                    lookup = interp1d(far_sensor_values, far_distances_mm, kind='linear', fill_value="extrapolate")
                else:
                    lookup = interp1d(close_sensor_values, close_distances_mm, kind='linear', fill_value="extrapolate")
            except Exception as e:
                log(str(e), important=True, in_exception=True)

            def get_distance_from_sensor(sensor_value: int) -> float:
                return float(lookup(sensor_value))

            def is_target_distance_reached():
                value = self.distance_sensor.current_value()
                dist = get_distance_from_sensor(value)
                return dist - val < tolerance

            while self.running_allowed:
                if is_target_distance_reached():
                    self.isClose = True
                    sys.exit()
                    break

        if not sideways or (sideways and mm_to_object >= 200):
            if self.distance_sensor.current_value() < next_value_far:
                th_distance_stopper = threading.Thread(target=distance_stopper, args=(True,))
                th_distance_stopper.start()
                
                log('waiting for wished distance...')
                while th_distance_stopper.is_alive():
                    continue

            if not sideways and mm_to_object <= 200:
                counter = 200
                while counter > mm_to_object:
                    counter -= 1
                    time.sleep(0.0023)

        elif sideways and mm_to_object < 200:
            th_distance_stopper = threading.Thread(target=distance_stopper, args=(False,))
            th_distance_stopper.start()

            while th_distance_stopper.is_alive():  # @TODO -> fail save could be needed
                continue

        return True

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