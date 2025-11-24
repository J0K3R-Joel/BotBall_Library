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
    import time
    import threading
    import uuid
    import math
    from scipy.interpolate import interp1d
    from wheelR import WheelR  # selfmade
    from analog import Analog  # selfmade
    from distance_sensor import DistanceSensor  # selfmade
    from light_sensor import LightSensor  # selfmade
    from digital import Digital  # selfmade
    from fileR import FileR  # selfmade
    from stop_manager import stop_manager  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

try:
    file_Manager = FileR()
except Exception as e:
    log(f'FileR Error: {str(e)}', important=True, in_exception=True)

BIAS_FOLDER = '/usr/lib/bias_files'
os.makedirs(BIAS_FOLDER, exist_ok=True)


class Rubber_Wheels_two():
    def __init__(self,
                 Instance_right_wheel: WheelR,
                 Instance_left_wheel: WheelR,
                 controller_standing: bool,
                 DS_SPEED: int = 1400,
                 Instance_button_front_right: Digital = None,
                 Instance_button_front_left: Digital = None,
                 Instance_button_back_right: Digital = None,
                 Instance_button_back_left: Digital = None,
                 Instance_light_sensor_front: LightSensor = None,
                 Instance_light_sensor_back: LightSensor = None,
                 Instance_light_sensor_side: LightSensor = None,
                 Instance_distance_sensor: DistanceSensor = None):

        self.right_wheel = Instance_right_wheel
        self.left_wheel = Instance_left_wheel

        self.standing = controller_standing

        self.button_fr = Instance_button_front_right
        self.button_fl = Instance_button_front_left
        self.button_br = Instance_button_back_right
        self.button_bl = Instance_button_back_left

        self.light_sensor_front = Instance_light_sensor_front
        self.light_sensor_back = Instance_light_sensor_back
        self.light_sensor_side = Instance_light_sensor_side

        self.distance_sensor = Instance_distance_sensor

        self.ds_speed = DS_SPEED
        self.bias_gyro_z = None
        self.bias_gyro_y = None
        self.bias_accel_z = None  # There are no function where you can do anything with the accel x -> you need to invent them by yourself
        self.bias_accel_y = None  # There are no function where you can do anything with the accel y -> you need to invent them by yourself
        self.isClose = False
        self.distance_far_values, self.distance_far_mm = self.get_distances()
        self.ONEEIGHTY_DEGREES_SECS = None
        self.NINETY_DEGREES_SECS = None
        self._motor_stoppers = {}
        self._next_id = 0
        self._motor_lock = threading.Lock()
        self.max_speed = 1500

        stop_manager.register_driver(self)
        self.mm_per_sec_file = BIAS_FOLDER + '/mm_per_sec.txt'

        self._set_values()

    # ======================== HELPER  ========================
    def _set_values(self) -> None:
        '''
        Sets all internal values

        Args:
            None

        Returns:
            None
        '''
        self.mm_per_sec = self.get_mm_per_sec()
        self.ONEEIGHTY_DEGREES_SECS = self.get_degrees()
        self.NINETY_DEGREES_SECS = self.ONEEIGHTY_DEGREES_SECS / 2
        self.bias_gyro_z = self.get_bias_gyro_z()
        self.bias_gyro_y = self.get_bias_gyro_y()
        self.bias_accel_z = self.get_bias_accel_z()
        self.bias_accel_y = self.get_bias_accel_y()

        if self.standing:
            self.standard_bias_gyro = self.bias_gyro_y
            self.standard_bias_accel = self.bias_accel_z
        else:
            self.standard_bias_gyro = self.bias_gyro_z
            self.standard_bias_accel = self.bias_accel_y

    def _manage_motor_stopper(self, beginning: bool) -> str:
        '''
        Manages the Lock of every class method, so if it (for example) gets spun clockwise and counterclockwise at the same time, the one that was sent through high priority will get executed and the other one does not

        Args:
            beginning (bool): is it in the beginning of a function (True) or at the end of a function (False)

        Returns:
            str: the ID of the motor at this moment
        '''
        with self._motor_lock:
            if beginning:
                self._next_id += 1
                motor_id = self._next_id
                self._motor_stoppers[motor_id] = True
                return motor_id
            else:
                if self._next_id in self._motor_stoppers:
                    self._motor_stoppers[self._next_id] = False
                return self._next_id


    def is_motor_active(self, motor_id: str) -> bool:
        '''
        Validates if the motor ID is still the same

        Args:
            motor_id (str): the ID from the manager

        Returns:
            bool: Is it still valid (True), or not (False)
        '''
        with self._motor_lock:
            return self._motor_stoppers.get(motor_id, False)


    # ======================== SET INSTANCES ========================
    def set_degrees(self, secs:float) -> None:
        '''
        Sets the amount of degrees for a 180° turn

        Args:
            secs (float): the time in seconds it takes for a 180° turn

        Returns:
            None
        '''
        self.ONEEIGHTY_DEGREES_SECS = secs
        self.NINETY_DEGREES_SECS = secs / 2

    def set_gyro_z(self, bias:float) -> None:
        '''
        Sets the amount of bias where the controller is laying down (for example) and getting turned from left to right or right to left

        Args:
            bias (float): the average of gyro_z after some time

        Returns:
            None
        '''
        self.bias_gyro_z = bias

    def set_gyro_y(self, bias:float) -> None:
        '''
        Sets the amount of bias where the controller is standing (for example) and getting turned from left to right or right to left

        Args:
            bias (float): the average of _kipr.gyro_y() after some time

        Returns:
            None
        '''
        self.bias_gyro_y = bias

    def set_accel_z(self, bias:float) -> None:
        '''
        Sets the amount of bias where the controller is standing (for example) and moving backward or forward

        Args:
            bias (float): the average of _kipr.accel_y() after some time

        Returns:
            None
        '''
        self.bias_accel_z = bias

    def set_accel_y(self, bias:float) -> None:
        '''
        Sets the amount of bias where the controller is laying down (for example) and moving backward or forward

        Args:
            bias (float): the average of _kipr.accel_y() after some time

        Returns:
            None
        '''
        self.bias_accel_y = bias

    def set_instance_distance_sensor(self, Instance_distance_sensor: DistanceSensor) -> None:
        '''
        create or overwrite the existence of the distance_sensor

        Args:
            Instance_distance_sensor (DistanceSensor): the instance of the distance sensor

       Returns:
            None
        '''
        self.distance_sensor = Instance_distance_sensor

    def set_instance_light_sensors(self, Instance_light_sensor_front: LightSensor,
                                   Instance_light_sensor_back: LightSensor,
                                   Instance_light_sensor_side: LightSensor) -> None:
        '''
        create or overwrite the existence of all light sensors

        Args:
            Instance_light_sensor_front (LightSensor): the instance of the front light sensor
            Instance_light_sensor_back (LightSensor): the instance of the back light sensor
            Instance_light_sensor_side (LightSensor):  the instance of the side light sensor

       Returns:
            None
        '''
        self.light_sensor_front = Instance_light_sensor_front
        self.light_sensor_back = Instance_light_sensor_back
        self.light_sensor_side = Instance_light_sensor_side

    def set_instance_light_sensor_front(self, Instance_light_sensor_front: LightSensor) -> None:
        '''
        create or overwrite the existence of the front light sensors

        Args:
            Instance_light_sensor_front (LightSensor): the instance of the front light sensor

       Returns:
            None
        '''
        self.light_sensor_front = Instance_light_sensor_front

    def set_instance_light_sensor_back(self, Instance_light_sensor_back: LightSensor) -> None:
        '''
        create or overwrite the existence of the back light sensor

        Args:
            Instance_light_sensor_back (LightSensor): the instance of the back light sensor

       Returns:
            None
        '''
        self.light_sensor_back = Instance_light_sensor_back

    def set_instance_light_sensor_side(self, Instance_light_sensor_side: LightSensor) -> None:
        '''
        create or overwrite the existence of the side light sensor

        Args:
            Instance_light_sensor_side (LightSensor):  the instance of the side light sensor

       Returns:
            None
        '''
        self.light_sensor_side = Instance_light_sensor_side

    def set_instances_buttons(self, Instance_button_front_right: Digital, Instance_button_front_left: Digital,
                              Instance_button_back_right: Digital, Instance_button_back_left: Digital) -> None:
        '''
        create or overwrite the existence of all buttons

        Args:
            Instance_button_front_right (Digital): the instance of the front right button
            Instance_button_front_left (Digital): the instance of the front left button
            Instance_button_back_left (Digital):  the instance of the back left button
            Instance_button_back_right (Digital):  the instance of the back right button

       Returns:
            None
        '''
        self.button_fl = Instance_button_front_left
        self.button_fr = Instance_button_front_right
        self.button_br = Instance_button_back_right
        self.button_bl = Instance_button_back_left

    def set_instance_button_fl(self, Instance_button_front_left: Digital) -> None:
        '''
        create or overwrite the existence of the front left button

        Args:
            Instance_button_front_left (Digital): the instance of the front left button

       Returns:
            None
        '''
        self.button_fl = Instance_button_front_left

    def set_instance_button_fr(self, Instance_button_front_right: Digital) -> None:
        '''
        create or overwrite the existence of the front right button

        Args:
            Instance_button_front_right (Digital): the instance of the front right button

       Returns:
            None
        '''
        self.button_fr = Instance_button_front_right

    def set_instance_button_bl(self, Instance_button_back_left: Digital) -> None:
        '''
        create or overwrite the existence of the back left button

        Args:
            Instance_button_back_left (Digital):  the instance of the back left button

       Returns:
            None
        '''
        self.button_bl = Instance_button_back_left

    def set_instance_button_br(self, Instance_button_back_right: Digital) -> None:
        '''
        create or overwrite the existence of the back right button

        Args:
            Instance_button_back_right (Digital):  the instance of the back right button

       Returns:
            None
        '''
        self.button_br = Instance_button_back_right

    def set_TOTAL_mm_per_sec(self, mm: int = None, sec: float = None) -> None:
        '''
        Sets the millimeters and / or seconds for driving mm per seconds

        Args:
            sec (float): The amount of time (in seconds) it took to drive
             mm (int): How far it drove (in mm)

        Returns:
            None
        '''
        if mm is None and sec is None:
            log('By setting the mm and sec at least one of those values need to be assigned to a number!', important=True, in_exception=True)
            raise ValueError('By setting the mm and sec at least one of those values need to be assigned to a number!')
        if not isinstance(mm, int) and mm is not None:
            log('mm need to stay in mm! make sure mm is not in seconds!', important=True, in_exception=True)
            raise TypeError('mm need to stay in mm! make sure mm is not in seconds!')
        if (not isinstance(sec, int) and not isinstance(sec, float)) and sec is not None:
            str_instance = isinstance(sec, str)
            log(f'seconds need to stay as a float or int! seconds being a string: {str_instance}', important=True, in_exception=True)
            raise TypeError(f'seconds need to stay as a float or int! seconds being a string: {str_instance}')


        text = file_Manager.reader(self.mm_per_sec_file).split('\n')
        file_mm = int(text[1].strip())
        file_sec = float(text[2].strip())
        actual_sec = sec if sec is not None else file_sec
        actual_mm = mm if mm is not None else file_mm

        self.mm_per_sec = actual_mm/actual_sec
        file_Manager.writer(self.mm_per_sec_file, 'w', self.mm_per_sec)
        file_Manager.writer(self.mm_per_sec_file, 'a', '\n' + str(actual_mm))
        file_Manager.writer(self.mm_per_sec_file, 'a', '\n' + str(actual_sec))

    def set_MM_mm_per_sec(self, mm: int) -> None:
        '''
        Specifically sets the millimeters for driving mm per seconds

        Args:
            mm (int): How far it drove (in mm)

        Returns:
            None
        '''
        self.set_TOTAL_mm_per_sec(mm=mm)

    def set_SEC_mm_per_sec(self, sec: float) -> None:
        '''
        Specifically sets the seconds for driving mm per seconds

        Args:
            sec (float): The amount of time (in seconds) it took to drive

        Returns:
            None
        '''
        self.set_TOTAL_mm_per_sec(sec=sec)

    # ======================== CHECK INSTANCES ========================

    def check_instance_light_sensors(self) -> bool:
        '''
        inspect the existence of all light sensors

        Args:
            None

       Returns:
            if there is an instance of all light sensor in existence
        '''
        if not isinstance(self.light_sensor_front, LightSensor):
            log('Light sensor front is not initialized!', in_exception=True)
            raise TypeError('Light sensor front is not initialized!')

        if not isinstance(self.light_sensor_back, LightSensor):
            log('Light sensor back is not initialized!', in_exception=True)
            raise TypeError('Light sensor back is not initialized!')

        if not isinstance(self.light_sensor_side, LightSensor):
            log('Light sensor side is not initialized!', in_exception=True)
            raise TypeError('Light sensor side is not initialized!')
        return True

    def check_instance_light_sensors_middle(self) -> bool:
        '''
        inspect the existence of the middle light sensors

        Args:
            None

       Returns:
            if there is an instance of the middle light sensors in existence
        '''
        if not isinstance(self.light_sensor_front, LightSensor):
            log('Light sensor front is not initialized!', in_exception=True)
            raise TypeError('Light sensor front is not initialized!')

        if not isinstance(self.light_sensor_back, LightSensor):
            log('Light sensor back is not initialized!', in_exception=True)
            raise TypeError('Light sensor back is not initialized!')
        return True

    def check_instance_light_sensor_front(self) -> bool:
        '''
        inspect the existence of the front light sensor

        Args:
            None

       Returns:
            if there is an instance of the front light sensor in existence
        '''
        if not isinstance(self.light_sensor_front, LightSensor):
            log('Light sensor front is not initialized!', in_exception=True)
            raise TypeError('Light sensor front is not initialized!')
        return True

    def check_instance_light_sensor_back(self) -> bool:
        '''
        inspect the existence of the back light sensor

        Args:
            None

       Returns:
            if there is an instance of the back light sensor in existence
        '''
        if not isinstance(self.light_sensor_back, LightSensor):
            log('Light sensor back is not initialized!', in_exception=True)
            raise TypeError('Light sensor back is not initialized!')
        return True

    def check_instance_light_sensor_side(self) -> bool:
        '''
        inspect the existence of the side light sensor

        Args:
            None

       Returns:
            if there is an instance of the side light sensor in existence
        '''
        if not isinstance(self.light_sensor_side, LightSensor):
            log('Light sensor side is not initialized!', in_exception=True)
            raise TypeError('Light sensor side is not initialized!')
        return True

    def check_instance_distance_sensor(self) -> bool:
        '''
        inspect the existence of the distance sensor

        Args:
            None

       Returns:
            if there is an instance of the distance sensor in existence
        '''
        if not isinstance(self.distance_sensor, DistanceSensor):
            log('Distance sensor is not initialized!', in_exception=True)
            raise TypeError('Distance sensor is not initialized!')
        return True

    def check_instance_button_fl(self) -> bool:
        '''
        inspect the existence of the front left button

        Args:
            None

       Returns:
            if there is an instance of the front left button in existence
        '''
        if not isinstance(self.button_fl, Digital):
            log('Button front left is not initialized!', in_exception=True)
            raise TypeError('Button front left is not initialized!')
        return True

    def check_instance_button_fr(self) -> bool:
        '''
        inspect the existence of the front right button

        Args:
            None

       Returns:
            if there is an instance of the front right button in existence
        '''
        if not isinstance(self.button_fr, Digital):
            log('Button front right is not initialized!', in_exception=True)
            raise TypeError('Button front right is not initialized!')
        return True

    def check_instance_button_bl(self) -> bool:
        '''
        inspect the existence of the back left button

        Args:
            None

       Returns:
            if there is an instance of the back left button in existence
        '''
        if not isinstance(self.button_bl, Digital):
            log('Button back left is not initialized!', in_exception=True)
            raise TypeError('Button back left is not initialized!')
        return True

    def check_instance_button_br(self) -> bool:
        '''
        inspect the existence of the back right button

        Args:
            None

       Returns:
            if there is an instance of the back right button in existence
        '''
        if not isinstance(self.button_br, Digital):
            log('Button back right is not initialized!', in_exception=True)
            raise TypeError('Button back right is not initialized!')
        return True

    def check_instances_buttons_front(self) -> bool:
        '''
        inspect the existence of the front buttons

        Args:
            None

       Returns:
            if there is an instance of the front buttons in existence
        '''
        if not isinstance(self.button_fl, Digital):
            log('Button front left is not initialized!', in_exception=True)
            raise TypeError('Button front left is not initialized!')

        if not isinstance(self.button_fr, Digital):
            log('Button front right is not initialized!', in_exception=True)
            raise TypeError('Button front right is not initialized!')

        return True

    def check_instances_buttons_back(self) -> bool:
        '''
        inspect the existence of the back buttons

        Args:
            None

       Returns:
            if there is an instance of the back buttons in existence
        '''
        if not isinstance(self.button_bl, Digital):
            log('Button back left is not initialized!', in_exception=True)
            raise TypeError('Button back left is not initialized!')

        if not isinstance(self.button_br, Digital):
            log('Button back right is not initialized!', in_exception=True)
            raise TypeError('Button back right is not initialized!')

        return True

    def check_instances_buttons(self) -> bool:
        '''
        inspect the existence of all buttons

        Args:
            None

       Returns:
            if there is an instance of all buttons in existence
        '''
        if not isinstance(self.button_fl, Digital):
            log('Button front left is not initialized!', in_exception=True)
            raise TypeError('Button front left is not initialized!')

        if not isinstance(self.button_fr, Digital):
            log('Button front right is not initialized!', in_exception=True)
            raise TypeError('Button front right is not initialized!')

        if not isinstance(self.button_bl, Digital):
            log('Button back left is not initialized!', in_exception=True)
            raise TypeError('Button back left is not initialized!')

        if not isinstance(self.button_br, Digital):
            log('Button back right is not initialized!', in_exception=True)
            raise TypeError('Button back right is not initialized!')

        return True

    # ===================== CALIBRATE BIAS =====================
    def auto_calibration(self, times:int) -> None:
        '''
        Automatically calibrates as often as you wish

        Args:
            times (int): The number of times it should calibrate

        Returns:
            None
        '''
        for i in range(times):
            self.calibrate(False)
            self.break_all_motors()
            print(f'=== {i+1} / {times} times calibrated ===', flush=True)
        log('AUTO CALIBRATION DONE')

    def calibrate(self, output:bool = True) -> float:
        '''
        Calibrates all necessairy bias depending on the controller standing or laying down

        Args:
            output (bool): If it should make an output, that it is done calibrating (True, default) or not (False)

        Returns:
            None. Writes bias into files
        '''
        self.calibrate_gyro_y(counter=1, max=4)
        self.calibrate_accel_z(counter=2, max=4)
        self.calibrate_gyro_z(counter=3, max=4)
        self.calibrate_accel_y(counter=4, max=4)
        self.bias_gyro_y = self.get_bias_gyro_y(True)
        self.bias_accel_z = self.get_bias_accel_y(True)
        self.bias_gyro_z = self.get_bias_gyro_z(True)
        self.bias_accel_y = self.get_bias_accel_y(True)
        self.calibrate_degrees()
        self.ONEEIGHTY_DEGREES_SECS = self.get_degrees(True)
        self.NINETY_DEGREES_SECS = self.ONEEIGHTY_DEGREES_SECS / 2
        if output:
            log('CALIBRATION DONE', important=True)

    def calibrate_gyro_z(self, counter: int = None, max: int = None, times: int = 8000) -> None:
        '''
        calibrates the bias from the gyro to be able to drive straight, since the bias is for telling us how far off from driving straight the wombat is

        Args:
            counter (int): the number where it is at the moment
            max (int): how many caLibrations there are (to show it on the screen and for debugging usage)
            times (int, optional): how many calibrations should be done (default: 8000)

        Returns:
            None
        '''
        i: int = 0
        avg: float = 0
        while i < times:
            avg += k.gyro_z()
            k.msleep(1)
            i += 1
        self.bias_gyro_z = avg / times
        if counter is not None and max is not None:
            log(f'{counter}/{max} - GYRO Z CALIBRATED')

    def calibrate_gyro_y(self, counter: int = None, max: int = None, times: int = 8000) -> None:
        '''
        calibrates the bias from the gyro to be able to drive straight, since the bias is for telling us how far off from driving straight the wombat is (theoretically it is for driving sideways)

        Args:
            counter (int, default): the number where it is at the moment (default: None)
            max (int, default): how many caLibrations there are (to show it on the screen and for debugging usage) (default: None)
            times (int, optional): how many calibrations should be done (default: 8000)

        Returns:
            None
        '''
        i: int = 0
        avg: float = 0
        time: int = 8000
        while i < times:
            avg += k.gyro_y()
            k.msleep(1)
            i += 1
        self.bias_gyro_y = avg / times
        if counter is not None and max is not None:
            log(f'{counter}/{max} - GYRO Y CALIBRATED')

    def calibrate_accel_z(self, counter: int = None, max: int = None, times: int = 8000) -> None:
        '''
        calibrates the bias from the accelerometer to know how fast the wombat is going towards the x-axis(accelerometer is not yet in use though)

        Args:
            counter (int, optional): the number where it is at the moment (default: None)
            max (int, optional): how many caLibrations there are (to show it on the screen and for debugging usage) (default: None)
            times (int, optional): how many calibrations should be done (default: 8000)

        Returns:
            None
        '''
        i: int = 0
        avg: float = 0
        while i < times:
            avg += k.accel_z()
            k.msleep(1)
            i += 1
        self.bias_accel_z = avg / times
        if counter is not None and max is not None:
            log(f'{counter}/{max} - ACCEL X CALIBRATED')

    def calibrate_accel_y(self, counter: int = None, max: int = None, times: int = 8000) -> None:
        '''
        calibrates the bias from the accelerometer to know how fast the wombat is going towards the y-axis(accelerometer is not yet in use though)

        Args:
            counter (int, optional): the number where it is at the moment (default: None)
            max (int, optional): how many caLibrations there are (to show it on the screen and for debugging usage) (default: None)
            times (int, optional): how many calibrations should be done (default: 8000)

        Returns:
            None
        '''
        i: int = 0
        avg: float = 0
        while i < times:
            avg += k.accel_y()
            k.msleep(1)
            i += 1
        self.bias_accel_y = avg / times
        if counter is not None and max is not None:
            log(f'{counter}/{max} - ACCEL Y CALIBRATED')

    def calibrate_degrees(self) -> None:
        '''
        The wombat has to be aligned on the black line. Afterwards it turns 180 degrees to see how long it takes for a full 180 degrees turn
        Improvement: Drives straight and after it recognises a black line it turns right (or left) to be aligned with the line. Afterwards doing a full 180 degrees turn to know how long it takes for a 180B0 turn

        Args:
            None

       Returns:
            None (but sets a class variable)
        '''
        self.check_instance_light_sensors_middle()
        startTime = time.time()
        while k.seconds() - startTime < (1200) / 1000:
            self.left_wheel.drive_dfw()
            self.right_wheel.drive_dbw()
        while not self.light_sensor_front.sees_black():
            self.left_wheel.drive_dfw()
            self.right_wheel.drive_dbw()
        while not self.light_sensor_back.sees_black():
            self.left_wheel.drive_dfw()
            self.right_wheel.drive_dbw()
        self.break_all_motors()
        endTime = time.time()
        self.ONEEIGHTY_DEGREES_SECS = (endTime - startTime) * 0.995
        self.NINETY_DEGREES_SECS = endTime - startTime
        log('DEGREES CALIBRATED')

    def calibrate_mm_per_sec(self, millis: int = 5000, speed: int = None) -> None:
        '''
        calibrates the mm per second. You need to mark the beginning on where it began to drive from, since you need to know how far it went (in mm)

        Args:
            millis (int, optional): How long it should drive (in milliseconds) (default: 5000)
            speed (int, optional): How fast it should drive (default: ds_speed)

        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed

        start_time = time.time()
        self.drive_straight(speed=speed, millis=millis)
        sec = time.time() - start_time
        mm = int(input('How many mm did the robot drive from the beginning on?: '))

        self.set_TOTAL_mm_per_sec(mm=mm, sec=sec)


    def calibrate_distance(self, start_mm: int, min_sensor_value: int, speed: int = None, step: float = 0.1) -> None:
        '''
        calibrates the values for the distance sensor. HINT: calibrate the gyro first (if you did not already do that), so it drives straight. Also it calibrates one time, make sure it is as accurate as possible.
        It needs to be 800mm away from an object and both object has to be as parallel to each other as possible.

        Args:
            start_mm (int): known starting distance (e.g. 95)
            max_sensor_value (int): the value until where the robot should drive (the lower the value,
            speed (int, optional): constant speed (default: ds_speed)
            step (float, optional): time between two measurements (default: 0.1)


        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed

        self.check_instance_distance_sensor()

        if self.mm_per_sec == 0:
            log('You need to calibrate the mm per sec first. Execute the function calibrate_mm_per_sec first!', important=True, in_exception=True)
            raise ValueError('You need to calibrate the mm per sec first. Execute the function calibrate_mm_per_sec first!')

        self.distance_far_values = []
        self.distance_far_mm = []

        threading.Thread(target=self.drive_straight, args=(9999999, -speed//2,)).start()

        start_time = time.time()

        while True:
            elapsed = (time.time() - start_time) / 2
            traveled = self.mm_per_sec * elapsed
            current_mm = max(start_mm + traveled, 0)

            sensor_value = self.distance_sensor.current_value()

            self.distance_far_values.append(sensor_value)
            self.distance_far_mm.append(int(current_mm))

            if sensor_value <= min_sensor_value:
                break

            time.sleep(step)
        self.break_all_motors(True)
        self.get_distances(calibrated=True)

        log(f"Calibration finished. {len(self.distance_far_mm)} datapoints collected.")

    # ================== GET / OVERWRITE BIAS ==================
    def get_mm_per_sec(self, only_mm: bool = False, only_sec: bool = False) -> None:  # @TODO schauen, wie man float ODER int (ODER list) zurückgeben kann als typ
        '''
        Getting the mm, sec, mm and sec or total it takes to drive a certain distance (in mm)

        Args:
            only_mm (bool, optional): If you specifically need the mm
            only_sec (bool, optional): If you specifically need the sec

        Returns:
            One of the following options:
                - List[int, float]: the mm and time in seconds it takes to drive
                - int: the mm of distance for driving
                - float: time in seconds for driving
                - float: calculated value of mm/sec
        '''

        text = file_Manager.reader(self.mm_per_sec_file).split('\n')
        total = float(text[0])
        mm = int(text[1])
        sec = float(text[2])

        if only_mm and only_sec:
            return mm, sec
        if only_mm:
            return mm
        if only_sec:
            return sec
        return total


    def get_distances(self, calibrated: bool = False) -> tuple:
        '''
        Getting the disances from the distances_arr.txt file

        Args:
            calibrated (bool, optional): Writing to the file distances_arr.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            tuple[list[int], list[int]] | None:
                If calibrated=False: (values, mm)
                If calibrated=True: None
        '''
        file_name = os.path.join(BIAS_FOLDER, 'distances_arr.txt')

        try:
            if calibrated:
                with open(file_name, "w") as f:
                    f.write("value=" + ",".join(map(str, self.distance_far_values)) + "\n")
                    f.write("mm=" + ",".join(map(str, self.distance_far_mm)) + "\n")
                log(f"Distances saved to {file_name}")

            else:
                if not os.path.exists(file_name):
                    raise FileNotFoundError(f"{file_name} not found. Run calibration first.")

                with open(file_name, "r") as f:
                    lines = f.readlines()
                values = []
                mm = []

                for line in lines:
                    if line.startswith("value="):
                        values = list(map(int, line.strip().split("=")[1].split(",")))
                    elif line.startswith("mm="):
                        mm = list(map(int, line.strip().split("=")[1].split(",")))

                return values, mm

        except Exception as e:
            log(str(e), important=True, in_exception=True)
            return None


    def get_current_standard_gyro(self) -> int:
        '''
        Getting the current value of the bias depending on if the controller is standing or laying down

        Args:
            None

        Returns:
            int: the gyro_z or gyro_y value
        '''
        return k.gyro_y() if self.standing else k.gyro_z()

    def get_degrees(self, calibrated: bool = False) -> float:
        '''
        Getting the average degrees from the bias_degrees.txt file

        Args:
            calibrated (bool, optional): Writing to the file bias_degrees.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)

        Returns:
            Average of the bias_degrees.txt file (optionally with the recent calibrated bias as well)
        '''
        avg = 0
        file_name = os.path.join(BIAS_FOLDER, 'bias_degrees.txt')
        try:
            temp_deg = file_Manager.reader(file_name)
            if calibrated:
                avg = (float(temp_deg) + self.ONEEIGHTY_DEGREES_SECS) / 2
                file_Manager.writer(file_name, 'w', avg)
            else:
                avg = float(temp_deg)

            return avg
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def get_bias_gyro_z(self, calibrated: bool = False) -> float:
        '''
        Getting the average bias from the bias_gyro_z.txt file

        Args:
            calibrated (bool, optional): Writing to the file bias_gyro_z.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            Average of the bias_gyro_z.txt file (optionally with the recent calibrated bias as well)
        '''
        avg = 0
        file_name = os.path.join(BIAS_FOLDER, 'bias_gyro_z.txt')
        try:
            with open(file_name, "r") as f:
                temp_bias = f.read()
                if calibrated:
                    avg = (float(temp_bias) + self.bias_gyro_z) / 2
                    file_Manager.writer(file_name, 'w', avg)
                else:
                    avg = float(temp_bias)
            return avg
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def get_bias_gyro_y(self, calibrated: bool = False) -> float:
        '''
        Getting the average bias from the bias_gyro_y.txt file

        Args:
            calibrated (bool, optional): Writing to the file bias_gyro_y.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            Average of the bias_gyro_y.txt file (optionally with the recent calibrated bias as well)
        '''
        avg = 0
        file_name = os.path.join(BIAS_FOLDER, 'bias_gyro_y.txt')
        try:
            with open(file_name, "r") as f:
                temp_bias = f.read()
                if calibrated:
                    avg = (float(temp_bias) + self.bias_gyro_y) / 2
                    file_Manager.writer(file_name, 'w', avg)
                else:
                    avg = float(temp_bias)
            return avg
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def get_bias_accel_z(self, calibrated: bool = False) -> float:
        '''
        Getting the average bias from the bias_accel_z.txt file

        Args:
            calibrated (bool, optional): Writing to the file bias_accel_z.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            Average of the bias_accel_z.txt file (optionally with the recent calibrated bias as well)
        '''
        avg = 0
        file_name = os.path.join(BIAS_FOLDER, 'bias_accel_z.txt')
        try:
            with open(file_name, "r") as f:
                temp_bias = f.read()
                if calibrated:
                    avg = (float(temp_bias) + self.bias_accel_z) / 2
                    file_Manager.writer(file_name, 'w', avg)
                else:
                    avg = float(temp_bias)
            return avg
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def get_bias_accel_y(self, calibrated: bool = False) -> float:
        '''
        Getting the average bias from the bias_accel_y.txt file

        Args:
            calibrated (bool, optional): Writing to the file bias_accel_y.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            Average of the bias_accel_y.txt file (optionally with the recent calibrated bias as well)
        '''
        avg = 0
        file_name = os.path.join(BIAS_FOLDER, 'bias_accel_y.txt')
        try:
            with open(file_name, "r") as f:
                temp_bias = f.read()
                if calibrated:
                    avg = (float(temp_bias) + self.bias_accel_y) / 2
                    file_Manager.writer(file_name, 'w', avg)
                else:
                    avg = float(temp_bias)
            return avg
        except Exception as e:
            log(str(e), important=True, in_exception=True)


    def get_standard_speed(self) -> int:
        '''
        Getting the default speed on which the robot moves

        Args:
            None

        Returns:
            int: the speed it is set to
        '''
        return self.ds_speed

    # ======================== PUBLIC METHODS =======================

    def break_motor(self, *args) -> None:
        '''
        immediately stop the motor(s) of the given port

        Args:
            *args: All of the desired (motor) ports which should be stopped

        Returns:
            None
        '''
        try:
            if isinstance(args[0], int):
                for port in args:
                    k.freeze(port)
            elif isinstance(args[0], WheelR):
                for wheel in args:
                    wheel.stop()
            else:
                log('Only integer (port number) or WheelR instance are allowed!', in_exception=True)
                raise TypeError('Only integer (port number) or WheelR instance are allowed!')
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def break_all_motors(self, stop:bool = False) -> None:
        '''
        immediately stop all motors

        Args:
            stop (bool, optional): If it should be turned off completly and everywhere (True), or just stop driving (False, default)

        Returns:
            None
        '''
        self.left_wheel.stop()
        self.right_wheel.stop()
        if stop:
            self._manage_motor_stopper(False)

    def align_drive_side(self, speed: int, drive_dir: bool = True, millis: int = 5000) -> None:
        '''
        Drives (forwards or backwards, depending if the speed is positive or negative) until it bumps into something, but it won't readjust with the other wheel, resulting in aligning as far away as possible

        Args:
            speed (int): How fast the robot should drive (and if it should go backwards (negative value) or forward (positive value)
            drive_dir (bool, optional): If True it should drive the other direction to be able to turn again, without bumping (default: True) -> sometimes you want to be as close to an object as possible
            millis (int): The maximum amount of time (in milliseconds) it is allowed to try to align itself (default: 5000)

        Returns:
            bool: True when all specified motors are done.
        '''
        self.check_instances_buttons()
        motor_id = self._manage_motor_stopper(True)
        theta = 0
        adjuster = 100
        hit = False
        instances = self.right_wheel, self.left_wheel, self.button_fl, self.button_fr
        if speed < 0:
            instances = self.left_wheel, self.right_wheel, self.button_bl, self.button_br

        startTime: float = k.seconds()
        while k.seconds() - startTime < (millis) / 1000 and self.is_motor_active(motor_id):
            if instances[2].is_pressed() and instances[3].is_pressed():
                hit = True
                break
            elif instances[2].is_pressed():
                hit = True
                instances[1].drive(0)
                instances[0].drive(speed)
            elif instances[3].is_pressed():
                hit = True
                instances[0].drive(0)
                instances[1].drive(speed)
            else:
                if theta < 10 and theta > -10:
                    instances[1].drive(speed)
                    instances[0].drive(speed)
                elif theta < 10:
                    instances[1].drive(speed + adjuster)
                    instances[0].drive(speed - adjuster * 3)
                else:
                    instances[1].drive(speed - adjuster * 3)
                    instances[0].drive(speed + adjuster)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 3
        if drive_dir and hit:
            self.drive_straight(200, -speed)
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def align_drive_front(self, drive_bw: bool = True, millis: int = 2000) -> None:
        '''
        aligning front by bumping into something, so both buttons on the front will be pressed. If there's an error by pressing the buttons, a fail save will occur. If at will it also drive backwards a little bit to be able to turn after it bumped into something

        Args:
            drive_bw (bool, optional): If you desire to drive backward a little bit (default: True) -> (but sometimes you want to stay aligned at the object)
            millis (int): The maximum amount of time (in milliseconds) it is allowed to try to align itself (default: 2000)

        Returns:
            None
        '''
        self.check_instances_buttons_front()
        motor_id = self._manage_motor_stopper(True)
        theta = 0
        adjuster = 100
        hit = False
        startTime: float = k.seconds()
        while k.seconds() - startTime < millis / 1000 and self.is_motor_active(motor_id):
            if self.button_fl.is_pressed() and self.button_fr.is_pressed():
                hit = True
                break
            elif self.button_fl.is_pressed():
                hit = True
                self.left_wheel.backward_max()
                self.right_wheel.forward_max()
            elif self.button_fr.is_pressed():
                hit = True
                self.left_wheel.forward_max()
                self.right_wheel.backward_max()
            else:
                if theta < 10 and theta > -10:
                    self.right_wheel.drive_dfw()
                    self.left_wheel.drive_dfw()
                elif theta < 10:
                    self.right_wheel.drive_dfw(-adjuster*3)
                    self.left_wheel.drive_dfw(adjuster)
                else:
                    self.left_wheel.drive_dfw(-adjuster*3)
                    self.right_wheel.drive_dfw(adjuster)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 3
        if drive_bw and hit:
            self.drive_straight(200, -500)
        self.break_all_motors()
        self._manage_motor_stopper(False)


    def align_drive_back(self, drive_fw: bool = True, millis: int = 2000) -> None:
        '''
        aligning back by bumping into something, so both buttons on the back will be pressed. If there's an error by pressing the buttons, a fail save will occur. If at will it also drive forwards a little bit to be able to turn after it bumped into something

        Args:
            drive_fw (bool, optional): If you desire to drive forward a little bit (default: True) -> (but sometimes you want to stay aligned at the object)
            millis (int): The maximum amount of time (in milliseconds) it is allowed to try to align itself (default: 2000)

        Returns:
            None
        '''
        self.check_instances_buttons_back()
        motor_id = self._manage_motor_stopper(True)
        hit = False
        startTime: float = k.seconds()
        while k.seconds() - startTime < (millis) / 1000 and self.is_motor_active(motor_id):
            if self.button_br.is_pressed() and self.button_bl.is_pressed():
                hit = True
                break
            elif self.button_br.is_pressed():
                hit = True
                self.left_wheel.drive(-500)
                self.right_wheel.drive_mfw()
            elif self.button_bl.is_pressed():
                hit = True
                self.right_wheel.drive(-500)
                self.left_wheel.drive_mfw()
            else:
                self.right_wheel.drive_mbw()
                self.left_wheel.drive_mbw()
        if drive_fw and hit:
            self.drive_straight(200, 500)
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def turn_wheel(self, direction: str, millis: int, speed: int = None) -> None:
        '''
        turning with only one wheel

        Args:
            direction (str): "left" or "right" - depends on where you want to go
            millis (int): how long it should perform this task
            speed (int, optional): how fast (and direction) it should drive (default: ds_speed)

        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed

        start_time = time.time()
        motor_id = self._manage_motor_stopper(True)
        if direction == 'left':
            while (time.time() - start_time) < millis / 1000 and self.is_motor_active(motor_id):
                self.right_wheel.drive(speed)
        elif direction == 'right':
            while (time.time() - start_time) < millis / 1000 and self.is_motor_active(motor_id):
                self.left_wheel.drive(speed)
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def drive_straight_condition_digital(self, Instance: Digital, condition: str, value: int, millis: int = 9999999, speed: int = None):
        '''
        drive straight until an digital value gets reached for the desired instance

        Args:
            Instance (Digital): just has to be from something digital (buttons)
            condition (str): should it match "==" or not "!="
            value (int): The value that the current value gets compared to and has to be reached / not matched
            millis (int, optional): The maximum amount of time (in milliseconds) which can be taken (default: 9999999)
            speed (int, optional): The speed it drives straight (default: ds_speed)

        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed
        motor_id = self._manage_motor_stopper(True)
        theta = 0
        adjuster = 100
        start_time = k.seconds()
        instances = self.left_wheel, self.right_wheel
        if speed < 0:
            instances = self.right_wheel, self.left_wheel
            adjuster = -adjuster
        if condition == "==":
            while (Instance.current_value() == value) and (k.seconds() - start_time < millis/1000) and self.is_motor_active(motor_id):
                if theta < 10 and theta > -10:
                    instances[0].drive(speed)
                    instances[1].drive(speed)
                elif theta < 10:
                    instances[0].drive(speed + adjuster)
                    instances[1].drive(speed - adjuster * 3)
                else:
                    instances[1].drive(speed + adjuster)
                    instances[0].drive(speed - adjuster * 3)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 3
        elif condition == "!=":
            while (Instance.current_value() != value) and (k.seconds() - start_time < millis/1000) and self.is_motor_active(motor_id):
                if theta < 10 and theta > -10:
                    instances[0].drive(speed)
                    instances[1].drive(speed)
                elif theta < 10:
                    instances[0].drive(speed + adjuster)
                    instances[1].drive(speed - adjuster * 3)
                else:
                    instances[1].drive(speed + adjuster)
                    instances[0].drive(speed - adjuster * 3)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 3
        else:
            log('Only "==" or "!=" is available for the condition!', important=True, in_exception=True)
            raise ValueError('Only "==" or "!=" is available for the condition!')
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def drive_straight_condition_analog(self, Instance: Analog, condition: str, value: int, millis: int = 9999999, speed: int = None) -> None:
        '''
        drive straight until an analog value gets reached for the desired instance

        Args:
            Instance (Analog): just has to be from something analog (since there is (as of time of creation) only light and distance sensors, which are valid for this argument, just those should be used.
            condition (str): ("let" / "<=") or ("get" / ">=") or ("ht" / ">") or ("lt" / "<") are valid. Notice: l -> less | h -> higher | e -> equal | t -> than. (The parentheses should be left out, as well as the slash, only choose one argument Example: ">=")
            value (int): The value that the current value gets compared to and has to be reached
            millis (int, optional): The maximum amount of time (in milliseconds) which can be taken (default: 9999999)
            speed (int, optional): The speed it drives straight (default: ds_speed)

        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed
        self.check_instances_buttons()
        motor_id = self._manage_motor_stopper(True)
        theta = 0.0
        startTime = k.seconds()
        adjuster = 100
        instances = self.left_wheel, self.right_wheel, self.button_fl, self.button_fr
        if speed < 0:
            instances = self.right_wheel, self.left_wheel, self.button_bl, self.button_br
            adjuster = -adjuster

        if condition == 'let' or condition == '<=':  # let -> less or equal than
            while Instance.current_value() <= value and (not instances[2].is_pressed() and not instances[3].is_pressed()) and k.seconds() - startTime < millis / 1000 and self.is_motor_active(motor_id):
                if theta < 10 and theta > -10:
                    instances[0].drive(speed)
                    instances[1].drive(speed)
                elif theta < 10:
                    instances[0].drive(speed + adjuster)
                    instances[1].drive(speed - adjuster * 3)
                else:
                    instances[1].drive(speed + adjuster)
                    instances[0].drive(speed - adjuster * 3)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 3

        elif condition == 'het' or condition == '>=':  # het -> higher or equal than
            while Instance.current_value() >= value and (not instances[2].is_pressed() and not instances[3].is_pressed()) and k.seconds() - startTime < millis / 1000 and self.is_motor_active(motor_id):
                if theta < 10 and theta > -10:
                    instances[0].drive(speed)
                    instances[1].drive(speed)
                elif theta < 10:
                    instances[0].drive(speed + adjuster)
                    instances[1].drive(speed - adjuster * 3)
                else:
                    instances[1].drive(speed + adjuster)
                    instances[0].drive(speed - adjuster * 3)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 3

        elif condition == 'ht' or condition == '>':  # ht -> higher than
            while Instance.current_value() > value and (not instances[2].is_pressed() and not instances[3].is_pressed()) and k.seconds() - startTime < millis / 1000 and self.is_motor_active(motor_id):
                if theta < 10 and theta > -10:
                    instances[0].drive(speed)
                    instances[1].drive(speed)
                elif theta < 10:
                    instances[0].drive(speed + adjuster)
                    instances[1].drive(speed - adjuster * 3)
                else:
                    instances[1].drive(speed + adjuster)
                    instances[0].drive(speed - adjuster * 3)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 3

        elif condition == 'lt' or condition == '<':  # lt -> less than
            while Instance.current_value() < value and (not instances[2].is_pressed() and not instances[3].is_pressed()) and k.seconds() - startTime < millis / 1000 and self.is_motor_active(motor_id):
                if theta < 10 and theta > -10:
                    instances[0].drive(speed)
                    instances[1].drive(speed)
                elif theta < 10:
                    instances[0].drive(speed + adjuster)
                    instances[1].drive(speed - adjuster * 3)
                else:
                    instances[1].drive(speed + adjuster)
                    instances[0].drive(speed - adjuster * 3)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 3
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def turn_to_black_line(self, direction: str, millis: int = 80, speed: int = None) -> None:
        '''
       Turn as long as the light sensor (front or back, depends if the speed is positive or negative) sees the black line

       Args:
           direction (str): "right" or "left" - depends on where you want to go
           millis (int, optional): how long (in milliseconds) to drive until the sensor gets checked (no threading is used) (default: 80)
           speed (int, optional): how fast it should turn. Note: with negative speed it will also look at the brightness sensor on the back (default: ds_speed)

       Returns:
           None
       '''
        if speed is None:
            speed = self.max_speed
        self.check_instance_light_sensors_middle()
        motor_id = self._manage_motor_stopper(True)
        instances = self.right_wheel, self.left_wheel, self.light_sensor_front
        if speed < 0:
            instances = self.left_wheel, self.right_wheel, self.light_sensor_back

        if direction == 'right':
            while not instances[2].sees_black() and self.is_motor_active(motor_id):
                instances[1].drive(speed)
                instances[0].drive(-speed)
                k.msleep(millis)
        elif direction == 'left':
            while not instances[2].sees_black() and self.is_motor_active(motor_id):
                instances[0].drive(speed)
                instances[1].drive(-speed)
                k.msleep(millis)
        else:
            log('Only "right" and "left" are valid commands for the direction!', in_exception=True)
            raise ValueError(
                'turn_black_line() Exception: Only "right" and "left" are valid commands for the direction!')
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def drive_align_line(self, direction: str, speed: int = None) -> None:
        '''
        If you are not on the line, it drives (forwards or backwards, depends if the speed is positive or negative) until the line was found and then aligns as desired.

        Args:
           direction (str): "right" or "left" - depends on where you want to go
           speed (int, optional): how fast it should drive (default: ds_speed)

        Returns:
           None
        '''
        if speed is None:
            speed = self.ds_speed
        self.check_instances_buttons()
        self.check_instance_light_sensors_middle()

        if direction != 'left' and direction != 'right':
            log('If the Wombat is not on the line, please tell it which direction it should face when it is on the line ("right" or "left")',
                in_exception=True)
            raise ValueError('drive_align_line() Exception: If the Wombat is not on the line, please tell it which direction it should face when it is on the line ("right" or "left")')

        ports = self.light_sensor_back, self.light_sensor_front
        if speed < 0:
            ports = self.light_sensor_front, self.light_sensor_back

        self.drive_straight_condition_analog(ports[1], '<=', ports[1].get_value_black() - ports[1].get_bias(), speed=speed)
        start_time = k.seconds()
        self.drive_straight_condition_analog(ports[0], '<=', ports[0].get_value_black() - ports[0].get_bias(), speed=speed)
        end_time = k.seconds()
        self.break_all_motors()

        seconds = end_time - start_time
        self.drive_straight((seconds * 1000) // 2, speed=-speed)
        self.turn_to_black_line(direction, speed=abs(speed))

    def drift(self, direction: str, end: str, degree: int) -> None:
        # missing in the function table
        if direction != 'left' and direction != 'right':
            log('direction parameter has to be "left" or "right"!', in_exception=True, important=True)
            raise ValueError('direction parameter has to be "left" or "right"!')

        if end != 'front' and end != 'back':
            log('end parameter has to be "front" or "back"!', in_exception=True, important=True)
            raise ValueError('end parameter has to be "front" or "back"!')

        if degree < 1 or degree > 180:
            log('Only values from range 1 - 180 are valid for the "degree" parameter', in_exception=True)
            raise ValueError(
                'Only values from range 1 - 180 are valid for the "degree" parameter')

        def get_kgv(a: int, b: int):
            a = abs(a)
            b = abs(b)

            if a == 0 or b == 0:
                return 0

            gcd = math.gcd(a, b)
            return (a*b)//gcd
        if end == 'front':
            if direction == 'left':
                speed = self.ds_speed
                instances = self.right_wheel, self.left_wheel
                nums = [3, 2]
                mods = [4, 2]
            else:
                speed = self.ds_speed
                instances = self.left_wheel, self.right_wheel
                nums = [3, 2]
                mods = [4, 2]
            positive = True
        else:
            if direction == 'left':
                speed = -self.ds_speed
                instances = self.right_wheel, self.left_wheel
                nums = [3, 2]
                mods = [4, 2]
            else:
                speed = -self.ds_speed
                instances = self.left_wheel, self.right_wheel
                nums = [3, 2]
                mods = [4, 2]
            positive = False


        divisor = 180 / degree
        degree_total_time = self.ONEEIGHTY_DEGREES_SECS / divisor
        tries = int((degree_total_time / 2) * 100)
        kgV = get_kgv(mods[0], mods[1])
        for i in range(1, tries+1):
            num = kgV * i
            if num >= tries:
                tries += (kgV * i) - tries
                break

        degree_try_time = degree_total_time / (tries/10)
        first_run_time = 0
        total_time = 0
        i = 1

        def direction_one(loop_index: int, speed: int):
            instances[0].drive(-speed)
            if loop_index % mods[0] == 0:
                time.sleep(degree_try_time / nums[0])
            else:
                time.sleep(degree_try_time)
            instances[0].stop()

        def direction_two(loop_index: int, speed: int):
            instances[1].drive(-speed)
            if loop_index % mods[1] == 0:
                if loop_index % mods[0] != 0:
                    time.sleep(degree_try_time * nums[1])
                else:
                    time.sleep(degree_try_time)
            else:
                time.sleep(degree_try_time)
            instances[1].stop()

        start_time = k.seconds()
        while True:
            if positive:
                if speed > 0:
                    start_time = k.seconds()
                direction_one(i, speed)
                direction_two(i, speed)

            else:
                if speed < 0:
                    start_time = k.seconds()
                direction_two(i, speed)
                direction_one(i, speed)


            if (positive and speed > 0) or (not positive and speed < 0):
                total_time += k.seconds() - start_time
                if not first_run_time:
                    first_run_time = k.seconds() - start_time

            if total_time >= degree_try_time * (tries/2) - (first_run_time*((self.ONEEIGHTY_DEGREES_SECS*2)/divisor)):
                if direction == 'left':
                    for j in range(int((self.ONEEIGHTY_DEGREES_SECS*2)/divisor)+1):
                        i += 1
                        speed = -speed
                        direction_one(i, speed)
                        direction_two(i, speed)
                    direction_two(i, speed)

                else:
                    direction_one(i-1, speed)
                    speed = self.ds_speed if positive else -self.ds_speed

                    instances[0].drive(-speed)
                    instances[1].drive(-speed)
                    time.sleep(degree_try_time/divisor)
                break

            speed = -speed
            i += 1

        self.break_all_motors()


    def on_line_align(self, millis: int = None, speed: int = None, leaning_side: str = None, adjust_wanted: bool = True) -> None:
        '''
        If you are on the line, then it will turn as long as you wish and look for the line. If the line was not found in the time given, then it will turn the other way

        Args:
            millis (int, optional): how long it is allowed to look for the line (default: NINETY_DEGREES_SECS)
            speed (int, optional): how fast it should drive (default: ds_speed)
            leaning_side (str, optional): the side ("right" or "left") where the wombat has to get to (default: None)
            adjust_wanted (bool, optional): should it get in the dead center of the line (True) or is it enough if just the desired sensor is on the line (False)? (default: True)

        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed
        startTime = k.seconds()
        maxDuration = millis/1000 if millis is not None else self.NINETY_DEGREES_SECS
        motor_id = self._manage_motor_stopper(True)
        instances = self.right_wheel, self.left_wheel, self.button_fl, self.button_fr, self.light_sensor_front
        counter_drive = False
        direction = 'left', 'right'
        if speed < 0:
            instances = self.left_wheel, self.right_wheel, self.button_bl, self.button_br, self.light_sensor_back
            direction = 'right', 'left'

        if leaning_side == 'left' or leaning_side == 'right':
            direction = leaning_side, 'right' if leaning_side != 'right' else 'left'
        elif leaning_side != None:
            log('leaning_side parameter has to be None, "left" or "right"!', important=True, in_exception=True)
            raise ValueError('leaning_side parameter has to be None, "left" or "right"!')

        while self.is_motor_active(motor_id):
            if direction[0] == 'left':
                instances[0].drive(speed)
                instances[1].drive(-speed)
            else:
                instances[0].drive(-speed)
                instances[1].drive(speed)
            if k.seconds() - startTime > maxDuration:
                self.turn_to_black_line(direction[1], 15, speed)

                counter_drive = True
                break
            if instances[4].sees_black():
                counter_drive = True
                break
            if instances[2].is_pressed() or instances[3].is_pressed():
                break

        if counter_drive and adjust_wanted:  #@TODO some kind of drift function here so the rear moves but the front stays still
            self.turn_to_black_line(direction[1], 20, speed=-speed)
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def black_line(self, millis: int, speed: int = None) -> None:
        '''
       drive on the black line as long as wished

       Args:
           millis (int): how long you want to follow the black line (in milliseconds)
           speed (int, optional): how fast it should drive straight (default: ds_speed)

       Returns:
           None
       '''
        if speed is None:
            speed = self.ds_speed
        self.check_instances_buttons()
        self.check_instance_light_sensors_middle()
        motor_id = self._manage_motor_stopper(True)
        startTime: float = k.seconds()
        ports = self.button_fl, self.button_fr, self.light_sensor_front
        if speed < 0:
            ports = self.button_bl, self.button_br, self.light_sensor_back
        while k.seconds() - startTime < millis/1000 and (not ports[0].is_pressed() and not ports[1].is_pressed()) and self.is_motor_active(motor_id):
            self.drive_straight_condition_analog(ports[2], '>=', ports[2].get_value_black() - ports[2].get_bias(), speed=speed, millis=100)

            if ports[2].current_value() < ports[2].get_value_black() - ports[2].get_bias():
                self.on_line_align(millis=80, speed=speed, adjust_wanted=False)
        self.break_all_motors()
        self._manage_motor_stopper(False)


    def drive_straight(self, millis: int, speed: int = None) -> None:
        '''
        drive straight for as long as you want to (in millis)

        Args:
            millis (int): for how long you want to drive straight
            speed (int, optional): the speed it is going to drive straight (default: ds_speed)

        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed
        motor_id = self._manage_motor_stopper(True)
        startTime: float = k.seconds()
        theta = 0.0
        adjuster = 100
        instances = self.left_wheel, self.right_wheel
        if speed < 0:
            instances = self.right_wheel, self.left_wheel
            adjuster = -adjuster

        while k.seconds() - startTime < (millis) / 1000 and self.is_motor_active(motor_id):
            if theta < 10 and theta > -10:
                instances[0].drive(speed)
                instances[1].drive(speed)
            elif theta < 10:
                instances[0].drive(speed + adjuster)
                instances[1].drive(speed - adjuster * 3)
            else:
                instances[0].drive(speed - adjuster * 3)
                instances[1].drive(speed + adjuster)
            k.msleep(10)
            theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 3
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def next_to_onto_line(self, leaning_side: str = None) -> None:
        '''
        If you are next to a black line, you can get onto it and be aligned

        Args:
            leaning_side (str, optional): the side ("right" or "left") where the wombat has to get to (default: None)

        Returns:
            None
        '''
        self.check_instance_light_sensors_middle()
        motor_id = self._manage_motor_stopper(True)
        if not leaning_side or leaning_side == 'right':
            instances = self.left_wheel, self.right_wheel
        else:
            instances = self.right_wheel, self.left_wheel
        startTime = k.seconds()

        while self.light_sensor_back.sees_white() and self.light_sensor_front.sees_white() and self.is_motor_active(motor_id):
            if k.seconds() - startTime < self.NINETY_DEGREES_SECS:
                instances[0].drive_dfw()
                instances[1].drive_dbw()
            else:
                instances[0].drive_dbw()
                instances[1].drive(instances[1].get_default_speed()//2)
                k.msleep(1)

        if not self.light_sensor_back.sees_white():
            while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                instances[0].drive_dbw()
                instances[1].drive_dbw()
            self.break_all_motors()
            while self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                instances[0].drive_mfw()
            self.break_all_motors()
            while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                instances[1].drive_mfw()
            self.break_all_motors()
            while self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                instances[1].drive_mfw()
            self.break_all_motors()
            while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                instances[1].drive_mbw()
                instances[0].drive(-200)
            # maybe add drift here

        elif not self.light_sensor_front.sees_white():
            while not self.light_sensor_back.sees_black() and self.is_motor_active(motor_id):
                instances[0].drive_dfw()
                instances[1].drive_dfw()
            while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                instances[0].drive_mbw()
                instances[1].drive_mfw()

            self.break_all_motors()

            if not self.light_sensor_front.sees_black():
                self.break_all_motors()
                while not self.light_sensor_front.sees_white() and self.is_motor_active(motor_id):
                    instances[1].drive_mfw()
                while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    instances[1].drive_mfw()

            if not self.light_sensor_back.sees_black():
                while self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    instances[1].drive_mfw()
                while self.light_sensor_back.sees_white() and self.is_motor_active(motor_id):
                    instances[1].drive_mbw()
                    instances[0].drive_mfw()
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def align_on_black_line(self, direction: str = 'vertical', leaning_side: str = None) -> None:
        '''
       Align yourself on the black line. It will only align itself on one line and not a collections of lines (crossings of lines)! You need to be somewhere on top of the black line to let this function work!

       Args:
           direction (str, optional): "vertical" (default) or "horizontal" - depends on where you want to go
           leaning_side (str, optional): "left" or "right" - helps the roboter to turn in the right direction (-> faster)

       Returns:
           None
       '''
        self.check_instance_light_sensors_middle()
        motor_id = self._manage_motor_stopper(True)
        try:
            if direction != 'vertical' and direction != 'horizontal':
                log('Only "vertical" or "horizontal" are valid options for the "direction" parameter',
                    in_exception=True)
                raise ValueError(
                    'align_on_black_line() Exception: Only "vertical" or "horizontal" are valid options for the "direction" parameter')

            if leaning_side != None and leaning_side != 'right' and leaning_side != 'left':
                log('Only "right", "left" or None / nothing are valid options for the "leaning_side" parameter',
                    in_exception=True)
                raise ValueError(
                    'align_on_black_line() Exception: Only "right", "left" or None / nothing are valid options for the "leaning_side" parameter')


            if not leaning_side or leaning_side == 'right':
                instances = self.left_wheel, self.right_wheel
            else:
                instances = self.right_wheel, self.left_wheel
            startTime = k.seconds()
            while self.light_sensor_back.sees_white() and self.light_sensor_front.sees_white() and self.is_motor_active(motor_id):
                if k.seconds() - startTime < self.NINETY_DEGREES_SECS:
                    instances[0].drive_dfw()
                    instances[1].drive_dbw()
                else:
                    instances[0].drive_dbw()
                    instances[1].drive(instances[1].get_default_speed()//2)
                    k.msleep(1)

            self.break_all_motors()

            if not self.light_sensor_back.sees_white():
                while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    instances[0].drive_dbw()
                    instances[1].drive_dbw()
                self.break_all_motors()
                while self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    instances[0].drive_mfw()
                self.break_all_motors()
                while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    instances[1].drive_mfw()
                self.break_all_motors()
                while self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    instances[1].drive_mfw()
                self.break_all_motors()
                while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    instances[1].drive_mbw()
                    instances[0].drive(-200)
                self.break_all_motors()

            elif not self.light_sensor_front.sees_white():
                while not self.light_sensor_back.sees_black() and self.is_motor_active(motor_id):
                    instances[0].drive_dfw()
                    instances[1].drive_dfw()
                while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    instances[0].drive_mbw()
                    instances[1].drive_mfw()

            self.break_all_motors()

            if not self.light_sensor_front.sees_black():
                self.break_all_motors()
                while not self.light_sensor_front.sees_white() and self.is_motor_active(motor_id):
                    instances[1].drive_mfw()

                while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    instances[1].drive_mfw()

            if not self.light_sensor_back.sees_black():
                while self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    instances[1].drive_mfw()
                while self.light_sensor_back.sees_white() and self.is_motor_active(motor_id):
                    instances[1].drive_mbw()
                    instances[0].drive_mfw()

            # @TODO a drift would fit here

            self.break_all_motors()
            self._manage_motor_stopper(False)


        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def drive_til_distance(self, mm_to_object: int, speed: int = None) -> None:
        '''
        drive straight as long as the object in front of the distance sensor (in mm) is not in reach

        Args:
            mm_to_object (int): the distance (in mm) between the distance sensor and the object in front of the sensor
            speed (int, optional): the speed it is going to drive straight (default: ds_speed)

        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed
        if mm_to_object > self.distance_far_mm[-1] or mm_to_object < 10:
            log(f'You can only put a value in range of 10 - {self.distance_far_mm[-1]} for the distance parameter!',
                in_exception=True)
            raise ValueError(
                f'drive_til_distance() Exception: You can only put a value in range of 10 - {self.distance_far_mm[-1]} for the distance parameter!')

        self.check_instances_buttons_back()
        self.check_instance_distance_sensor()

        if self.distance_far_values == 0 and self.distance_far_mm == 0:
            log('You need to calibrate the distance using the calibrate_distance function first!', important=True, in_exception=True)
            raise ValueError('You need to calibrate the distance using the calibrate_distance function first!')

        motor_id = self._manage_motor_stopper(True)
        self.isClose = False
        theta = 0.0
        adjuster = 100
        instances = self.left_wheel, self.right_wheel
        if speed < 0:
            instances = self.right_wheel, self.left_wheel
            adjuster = -adjuster

        else:
            if self.distance_sensor.current_value() > 1800: # this is because if it is already too close, it will back out a little bit to get the best result
                while self.distance_sensor.current_value() > 1800 and (
                        not self.button_bl.is_pressed() and not self.button_br.is_pressed()) and self.is_motor_active(
                    motor_id):
                    if theta < 10 and theta > -10:
                        instances[0].drive(speed)
                        instances[1].drive(speed)
                    elif theta < 10:
                        instances[0].drive(speed + adjuster)
                        instances[1].drive(speed - adjuster * 3)
                    else:
                        instances[1].drive(speed + adjuster)
                        instances[0].drive(speed - adjuster * 3)
                    k.msleep(10)
                    theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 3
                if theta != 0.0:
                    self.left_wheel.drive(speed)
                    self.right_wheel.drive(speed)
                    k.msleep(20)
                    self.break_all_motors()

        combination = dict(zip(self.distance_far_mm, self.distance_far_values))
        next_step = min(combination, key=lambda x: abs(x - mm_to_object))
        next_value = combination[next_step]

        def distance_stopper(positive):
            tolerance = mm_to_object / 20  # /20 makes it that it is 90% accurate
            try:
                lookup = interp1d(self.distance_far_values, self.distance_far_mm, kind='linear',
                                  fill_value="extrapolate")
            except Exception as e:
                log(str(e), important=True, in_exception=True)

            def get_distance_from_sensor(sensor_value):
                return float(lookup(sensor_value))

            def is_target_distance_reached():
                value = self.distance_sensor.current_value()
                dist = get_distance_from_sensor(value)
                if str(dist) == 'inf' or dist <= self.distance_far_mm[0]:
                    return True

                if positive:
                    return dist < mm_to_object + tolerance
                else:
                    return dist > mm_to_object - tolerance

            while self.is_motor_active(motor_id):
                if is_target_distance_reached():
                    self.isClose = True
                    sys.exit()
                    break

        if speed > 0:
            if self.distance_sensor.current_value() < next_value:
                threading.Thread(target=distance_stopper, args=(True,)).start()

                while not self.isClose and self.is_motor_active(motor_id):
                    if theta < 10 and theta > -10:
                        instances[0].drive(speed)
                        instances[1].drive(speed)
                    elif theta < 10:
                        instances[0].drive(speed + adjuster)
                        instances[1].drive(speed - adjuster * 3)
                    else:
                        instances[1].drive(speed + adjuster)
                        instances[0].drive(speed - adjuster * 3)
                    k.msleep(10)
                    theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 3

            if mm_to_object < self.distance_far_mm[0]:
                counter = self.distance_far_mm[0]
                mult = self.ds_speed / speed
                timer = 0.001 * mult
                while counter > mm_to_object and self.is_motor_active(motor_id):
                    counter -= 1
                    if theta < 10 and theta > -10:
                        instances[0].drive(speed)
                        instances[1].drive(speed)
                    elif theta < 10:
                        instances[0].drive(speed + adjuster)
                        instances[1].drive(speed - adjuster * 3)
                    else:
                        instances[1].drive(speed + adjuster)
                        instances[0].drive(speed - adjuster * 3)
                    time.sleep(timer)
                    theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 3
        else:
            if self.distance_sensor.current_value() > next_value:
                threading.Thread(target=distance_stopper, args=(False,)).start()

                while not self.isClose and self.is_motor_active(motor_id):
                    if theta < 10 and theta > -10:
                        instances[0].drive(speed)
                        instances[1].drive(speed)
                    elif theta < 10:
                        instances[0].drive(speed + adjuster)
                        instances[1].drive(speed - adjuster * 3)
                    else:
                        instances[1].drive(speed + adjuster)
                        instances[0].drive(speed - adjuster * 3)
                    k.msleep(10)
                    theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 3

        self.break_all_motors()
        self._manage_motor_stopper(False)

    def turn_degrees_far(self, direction: str, degree: int, straight: bool = True) -> None:
        '''
        turn the amount of degrees given, to take a turn with only one wheel, resulting in a turn not on the spot

        Args:
            direction (str): "left" or "right", depending on where you want to go
            degree (int): the amount of degrees to turn from the current point (only values from 0 - 180 allowed for maximum efficiency)
            straight (bool, optional): If True, it will drive forward for the direction. If False, it will drive backward. (default: True)

        Returns:
            None
        '''
        speed = self.max_speed if straight else -self.max_speed

        motor_id = self._manage_motor_stopper(True)
        if direction != 'right' and direction != 'left':
            log('Only "right" or "left" are valid options for the "direction" parameter', in_exception=True)
            raise ValueError(
                'turn_degrees_far() Exception: Only "right" or "left" are valid options for the "direction" parameter')

        if degree > 180 and degree < 0:
            log('Only values from range 0 - 180 are valid for the "degree" parameter', in_exception=True)
            raise ValueError(
                'turn_degrees_far() Exception: Only values from range 0 - 180 are valid for the "degree" parameter')

        div = 180 / degree
        value = self.ONEEIGHTY_DEGREES_SECS / div
        if degree <= 90:
            div = 90 / degree
            value = self.NINETY_DEGREES_SECS / div
        self.break_all_motors()
        start_time = time.time()
        if direction == 'right':
            while time.time() - start_time < 2 * value and self.is_motor_active(motor_id):
                self.left_wheel.drive(speed)
        elif direction == 'left':
            while time.time() - start_time < 2 * value and self.is_motor_active(motor_id):
                self.right_wheel.drive(speed)
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def turn_degrees(self, direction: str, degree: int) -> None:
        '''
        turn the amount of degrees given, to take a turn with all wheels, resulting in a turn on the spot

        Args:
            direction (str): "left" or "right", depending on where you want to go
            degree (int): the amount of degrees (B0) to turn from the current point (only values from 0 - 180 allowed for maximum efficiency)

        Returns:
            None
        '''
        motor_id = self._manage_motor_stopper(True)
        if direction != 'right' and direction != 'left':
            log('Only "right" or "left" are valid options for the "direction" parameter', in_exception=True)
            raise ValueError(
                'turn_degrees() Exception: Only "right" or "left" are valid options for the "direction" parameter')

        if degree > 180 or degree < 1:
            log('Only values from range 1 - 180 are valid for the "degree" parameter', in_exception=True)
            raise ValueError(
                'turn_degrees() Exception: Only values from range 1 - 180 are valid for the "degree" parameter')

        div = 180 / degree
        value = self.ONEEIGHTY_DEGREES_SECS / div
        if degree <= 90:
            div = 90 / degree
            value = self.NINETY_DEGREES_SECS / div

        start_time = time.time()
        if direction == 'right':
            while time.time() - start_time < value and self.is_motor_active(motor_id):
                self.left_wheel.drive_dfw()
                self.right_wheel.drive_dbw()
        elif direction == 'left':
            while time.time() - start_time < value and self.is_motor_active(motor_id):
                self.left_wheel.drive_dbw()
                self.right_wheel.drive_dfw()
        self.break_all_motors()
        k.msleep(200)
        self._manage_motor_stopper(False)


class Mechanum_Wheels_four:
    def __init__(self,
                 Instance_front_right_wheel: WheelR,
                 Instance_front_left_wheel: WheelR,
                 Instance_back_left_wheel: WheelR,
                 Instance_back_right_wheel: WheelR,
                 controller_standing: bool,
                 DS_SPEED: int = 1400,
                 Instance_button_front_right: Digital = None,
                 Instance_button_front_left: Digital = None,
                 Instance_button_back_right: Digital = None,
                 Instance_button_back_left: Digital = None,
                 Instance_light_sensor_front: LightSensor = None,
                 Instance_light_sensor_back: LightSensor = None,
                 Instance_light_sensor_side: LightSensor = None,
                 Instance_distance_sensor: DistanceSensor = None,
                 ):

        self.fr_wheel = Instance_front_right_wheel
        self.fl_wheel = Instance_front_left_wheel
        self.bl_wheel = Instance_back_left_wheel
        self.br_wheel = Instance_back_right_wheel

        self.standing = controller_standing

        self.button_fr = Instance_button_front_right
        self.button_fl = Instance_button_front_left
        self.button_br = Instance_button_back_right
        self.button_bl = Instance_button_back_left

        self.light_sensor_front = Instance_light_sensor_front
        self.light_sensor_back = Instance_light_sensor_back
        self.light_sensor_side = Instance_light_sensor_side

        self.distance_sensor = Instance_distance_sensor

        self.ds_speed = DS_SPEED
        self.distance_far_values, self.distance_far_mm = self.get_distances()
        self.isClose = False
        self._motor_lock = threading.Lock()
        self._motor_stoppers = {}
        self._next_motor_id = 0
        self.max_speed = 1500

        self.mm_per_sec_file = BIAS_FOLDER + '/mm_per_sec.txt'
        stop_manager.register_driver(self)
        self._set_values()

    # ======================== HELPER  ========================
    def _set_values(self):
        '''
        Sets all internal values

        Args:
            None

        Returns:
            None
        '''
        self.mm_per_sec = self.get_mm_per_sec()
        self.ONEEIGHTY_DEGREES_SECS = self.get_degrees()
        self.NINETY_DEGREES_SECS = self.ONEEIGHTY_DEGREES_SECS / 2
        self.bias_gyro_z = self.get_bias_gyro_z()
        self.bias_gyro_y = self.get_bias_gyro_y()
        self.bias_accel_z = self.get_bias_accel_z()  # There are no function where you can do anything with the accel y -> you need to invent them by yourself
        self.bias_accel_y = self.get_bias_accel_y()  # There are no function where you can do anything with the accel y -> you need to invent them by yourself
        self._handle_standard_bias()


    def _handle_standard_bias(self):
        if self.standing:
            self.standard_bias_gyro = self.bias_gyro_y
            self.standard_bias_accel = self.bias_accel_z
            self.rev_standard_bias_gyro = self.bias_gyro_z
            self.rev_standard_bias_accel = self.bias_gyro_y
        else:
            self.standard_bias_gyro = self.bias_gyro_z
            self.standard_bias_accel = self.bias_accel_y
            self.rev_standard_bias_gyro = self.bias_gyro_y
            self.rev_standard_bias_accel = self.bias_gyro_z


    def _manage_motor_stopper(self, beginning: bool) -> str:
        '''
        Manages the Lock of every class method, so if it (for example) gets spun clockwise and counterclockwise at the same time, the one that was sent through high priority will get executed and the other one does not

        Args:
            beginning (bool): is it in the beginning of a function (True) or at the end of a function (False)

        Returns:
            str: the ID of the motor at this moment
        '''
        with self._motor_lock:
            if beginning:
                self._next_motor_id += 1
                motor_id = self._next_motor_id
                self._motor_stoppers[motor_id] = True
                return motor_id
            else:
                if self._next_motor_id in self._motor_stoppers:
                    self._motor_stoppers[self._next_motor_id] = False
                return self._next_motor_id

    def is_motor_active(self, motor_id: str) -> bool:
        '''
        Validates if the motor ID is still the same

        Args:
            motor_id (str): the ID from the manager

        Returns:
            bool: Is it still valid (True), or not (False)
        '''
        with self._motor_lock:
            return self._motor_stoppers.get(motor_id, False)

    # ======================== SET INSTANCES ========================

    def set_degrees(self, secs:float) -> None:
        '''
        Sets the amount of degrees for a 180° turn

        Args:
            secs (float): the time in seconds it takes for a 180° turn

        Returns:
            None
        '''
        self.ONEEIGHTY_DEGREES_SECS = secs
        self.NINETY_DEGREES_SECS = secs / 2

    def set_gyro_z(self, bias:float) -> None:
        '''
        Sets the amount of bias where the controller is laying down (for example) and getting turned from left to right or right to left

        Args:
            bias (float): the average of gyro_z after some time

        Returns:
            None
        '''
        self.bias_gyro_z = bias
        self._handle_standard_bias()

    def set_gyro_y(self, bias:float) -> None:
        '''
        Sets the amount of bias where the controller is standing (for example) and getting turned from left to right or right to left

        Args:
            bias (float): the average of _kipr.gyro_y() after some time

        Returns:
            None
        '''
        self.bias_gyro_y = bias
        self._handle_standard_bias()

    def set_accel_z(self, bias:float) -> None:
        '''
        Sets the amount of bias where the controller is standing (for example) and moving backward or forward

        Args:
            bias (float): the average of _kipr.accel_y() after some time

        Returns:
            None
        '''
        self.bias_accel_z = bias
        self._handle_standard_bias()

    def set_accel_y(self, bias:float) -> None:
        '''
        Sets the amount of bias where the controller is laying down (for example) and moving backward or forward

        Args:
            bias (float): the average of _kipr.accel_y() after some time

        Returns:
            None
        '''
        self.bias_accel_y = bias
        self._handle_standard_bias()

    def set_instance_distance_sensor(self, Instance_distance_sensor: DistanceSensor) -> None:
        '''
        create or overwrite the existence of the distance_sensor

        Args:
            Instance_distance_sensor (DistanceSensor): the instance of the distance sensor

       Returns:
            None
        '''
        self.distance_sensor = Instance_distance_sensor

    def set_instance_light_sensors(self, Instance_light_sensor_front: LightSensor,
                                   Instance_light_sensor_back: LightSensor,
                                   Instance_light_sensor_side: LightSensor) -> None:
        '''
        create or overwrite the existence of all light sensors

        Args:
            Instance_light_sensor_front (LightSensor): the instance of the front light sensor
            Instance_light_sensor_back (LightSensor): the instance of the back light sensor
            Instance_light_sensor_side (LightSensor):  the instance of the side light sensor

       Returns:
            None
        '''
        self.light_sensor_front = Instance_light_sensor_front
        self.light_sensor_back = Instance_light_sensor_back
        self.light_sensor_side = Instance_light_sensor_side

    def set_instance_light_sensor_front(self, Instance_light_sensor_front: LightSensor) -> None:
        '''
        create or overwrite the existence of the front light sensors

        Args:
            Instance_light_sensor_front (LightSensor): the instance of the front light sensor

       Returns:
            None
        '''
        self.light_sensor_front = Instance_light_sensor_front

    def set_instance_light_sensor_back(self, Instance_light_sensor_back: LightSensor) -> None:
        '''
        create or overwrite the existence of the back light sensor

        Args:
            Instance_light_sensor_back (LightSensor): the instance of the back light sensor

       Returns:
            None
        '''
        self.light_sensor_back = Instance_light_sensor_back

    def set_instance_light_sensor_side(self, Instance_light_sensor_side: LightSensor) -> None:
        '''
        create or overwrite the existence of the side light sensor

        Args:
            Instance_light_sensor_side (LightSensor):  the instance of the side light sensor

       Returns:
            None
        '''
        self.light_sensor_side = Instance_light_sensor_side

    def set_instances_buttons(self, Instance_button_front_right: Digital, Instance_button_front_left: Digital,
                              Instance_button_back_right: Digital, Instance_button_back_left: Digital) -> None:
        '''
        create or overwrite the existence of all buttons

        Args:
            Instance_button_front_right (Digital): the instance of the front right button
            Instance_button_front_left (Digital): the instance of the front left button
            Instance_button_back_left (Digital):  the instance of the back left button
            Instance_button_back_right (Digital):  the instance of the back right button

       Returns:
            None
        '''
        self.button_fl = Instance_button_front_left
        self.button_fr = Instance_button_front_right
        self.button_br = Instance_button_back_right
        self.button_bl = Instance_button_back_left

    def set_instance_button_fl(self, Instance_button_front_left: Digital) -> None:
        '''
        create or overwrite the existence of the front left button

        Args:
            Instance_button_front_left (Digital): the instance of the front left button

       Returns:
            None
        '''
        self.button_fl = Instance_button_front_left

    def set_instance_button_fr(self, Instance_button_front_right: Digital) -> None:
        '''
        create or overwrite the existence of the front right button

        Args:
            Instance_button_front_right (Digital): the instance of the front right button

       Returns:
            None
        '''
        self.button_fr = Instance_button_front_right

    def set_instance_button_bl(self, Instance_button_back_left: Digital) -> None:
        '''
        create or overwrite the existence of the back left button

        Args:
            Instance_button_back_left (Digital):  the instance of the back left button

       Returns:
            None
        '''
        self.button_bl = Instance_button_back_left

    def set_instance_button_br(self, Instance_button_back_right: Digital) -> None:
        '''
        create or overwrite the existence of the back right button

        Args:
            Instance_button_back_right (Digital):  the instance of the back right button

       Returns:
            None
        '''
        self.button_br = Instance_button_back_right

    def set_TOTAL_mm_per_sec(self, mm: int = None, sec: float = None) -> None:
        '''
        Sets the millimeters and / or seconds for driving mm per seconds

        Args:
            sec (float): The amount of time (in seconds) it took to drive
             mm (int): How far it drove (in mm)

        Returns:
            None
        '''
        if mm is None and sec is None:
            log('By setting the mm and sec at least one of those values need to be assigned to a number!',
                important=True, in_exception=True)
            raise ValueError('By setting the mm and sec at least one of those values need to be assigned to a number!')
        if not isinstance(mm, int) and mm is not None:
            log('mm need to stay in mm! make sure mm is not in seconds!', important=True, in_exception=True)
            raise TypeError('mm need to stay in mm! make sure mm is not in seconds!')
        if (not isinstance(sec, int) and not isinstance(sec, float)) and sec is not None:
            str_instance = isinstance(sec, str)
            log(f'seconds need to stay as a float or int! seconds being a string: {str_instance}', important=True,
                in_exception=True)
            raise TypeError(f'seconds need to stay as a float or int! seconds being a string: {str_instance}')

        text = file_Manager.reader(self.mm_per_sec_file).split('\n')
        file_mm = int(text[1].strip())
        file_sec = float(text[2].strip())
        actual_sec = sec if sec is not None else file_sec
        actual_mm = mm if mm is not None else file_mm

        self.mm_per_sec = actual_mm/actual_sec
        file_Manager.writer(self.mm_per_sec_file, 'w', self.mm_per_sec)
        file_Manager.writer(self.mm_per_sec_file, 'a', '\n' + str(actual_mm))
        file_Manager.writer(self.mm_per_sec_file, 'a', '\n' + str(actual_sec))

    def set_MM_mm_per_sec(self, mm: int) -> None:
        '''
        Specifically sets the millimeters for driving mm per seconds

        Args:
            mm (int): How far it drove (in mm)

        Returns:
            None
        '''
        self.set_TOTAL_mm_per_sec(mm=mm)

    def set_SEC_mm_per_sec(self, sec: float) -> None:
        '''
        Specifically sets the seconds for driving mm per seconds

        Args:
            sec (float): The amount of time (in seconds) it took to drive

        Returns:
            None
        '''
        self.set_TOTAL_mm_per_sec(sec=sec)

    # ======================== CHECK INSTANCES ========================

    def check_instance_light_sensors(self) -> bool:
        '''
        inspect the existence of all light sensors

        Args:
            None

       Returns:
            if there is an instance of all light sensor in existence
        '''
        if not isinstance(self.light_sensor_front, LightSensor):
            log('Light sensor front is not initialized!', in_exception=True)
            raise TypeError('Light sensor front is not initialized!')

        if not isinstance(self.light_sensor_back, LightSensor):
            log('Light sensor back is not initialized!', in_exception=True)
            raise TypeError('Light sensor back is not initialized!')

        if not isinstance(self.light_sensor_side, LightSensor):
            log('Light sensor side is not initialized!', in_exception=True)
            raise TypeError('Light sensor side is not initialized!')
        return True

    def check_instance_light_sensors_middle(self) -> bool:
        '''
        inspect the existence of the middle light sensors

        Args:
            None

       Returns:
            if there is an instance of the middle light sensors in existence
        '''
        if not isinstance(self.light_sensor_front, LightSensor):
            log('Light sensor front is not initialized!', in_exception=True)
            raise TypeError('Light sensor front is not initialized!')

        if not isinstance(self.light_sensor_back, LightSensor):
            log('Light sensor back is not initialized!', in_exception=True)
            raise TypeError('Light sensor back is not initialized!')
        return True

    def check_instance_light_sensor_front(self) -> bool:
        '''
        inspect the existence of the front light sensor

        Args:
            None

       Returns:
            if there is an instance of the front light sensor in existence
        '''
        if not isinstance(self.light_sensor_front, LightSensor):
            log('Light sensor front is not initialized!', in_exception=True)
            raise TypeError('Light sensor front is not initialized!')
        return True

    def check_instance_light_sensor_back(self) -> bool:
        '''
        inspect the existence of the back light sensor

        Args:
            None

       Returns:
            if there is an instance of the back light sensor in existence
        '''
        if not isinstance(self.light_sensor_back, LightSensor):
            log('Light sensor back is not initialized!', in_exception=True)
            raise TypeError('Light sensor back is not initialized!')
        return True

    def check_instance_light_sensor_side(self) -> bool:
        '''
        inspect the existence of the side light sensor

        Args:
            None

       Returns:
            if there is an instance of the side light sensor in existence
        '''
        if not isinstance(self.light_sensor_side, LightSensor):
            log('Light sensor side is not initialized!', in_exception=True)
            raise TypeError('Light sensor side is not initialized!')
        return True

    def check_instance_distance_sensor(self) -> bool:
        '''
        inspect the existence of the distance sensor

        Args:
            None

       Returns:
            if there is an instance of the distance sensor in existence
        '''
        if not isinstance(self.distance_sensor, DistanceSensor):
            log('Distance sensor is not initialized!', in_exception=True)
            raise TypeError('Distance sensor is not initialized!')
        return True

    def check_instance_button_fl(self) -> bool:
        '''
        inspect the existence of the front left button

        Args:
            None

       Returns:
            if there is an instance of the front left button in existence
        '''
        if not isinstance(self.button_fl, Digital):
            log('Button front left is not initialized!', in_exception=True)
            raise TypeError('Button front left is not initialized!')
        return True

    def check_instance_button_fr(self) -> bool:
        '''
        inspect the existence of the front right button

        Args:
            None

       Returns:
            if there is an instance of the front right button in existence
        '''
        if not isinstance(self.button_fr, Digital):
            log('Button front right is not initialized!', in_exception=True)
            raise TypeError('Button front right is not initialized!')
        return True

    def check_instance_button_bl(self) -> bool:
        '''
        inspect the existence of the back left button

        Args:
            None

       Returns:
            if there is an instance of the back left button in existence
        '''
        if not isinstance(self.button_bl, Digital):
            log('Button back left is not initialized!', in_exception=True)
            raise TypeError('Button back left is not initialized!')
        return True

    def check_instance_button_br(self) -> bool:
        '''
        inspect the existence of the back right button

        Args:
            None

       Returns:
            if there is an instance of the back right button in existence
        '''
        if not isinstance(self.button_br, Digital):
            log('Button back right is not initialized!', in_exception=True)
            raise TypeError('Button back right is not initialized!')
        return True

    def check_instances_buttons_front(self) -> bool:
        '''
        inspect the existence of the front buttons

        Args:
            None

       Returns:
            if there is an instance of the front buttons in existence
        '''
        if not isinstance(self.button_fl, Digital):
            log('Button front left is not initialized!', in_exception=True)
            raise TypeError('Button front left is not initialized!')

        if not isinstance(self.button_fr, Digital):
            log('Button front right is not initialized!', in_exception=True)
            raise TypeError('Button front right is not initialized!')

        return True

    def check_instances_buttons_back(self) -> bool:
        '''
        inspect the existence of the back buttons

        Args:
            None

       Returns:
            if there is an instance of the back buttons in existence
        '''
        if not isinstance(self.button_bl, Digital):
            log('Button back left is not initialized!', in_exception=True)
            raise TypeError('Button back left is not initialized!')

        if not isinstance(self.button_br, Digital):
            log('Button back right is not initialized!', in_exception=True)
            raise TypeError('Button back right is not initialized!')

        return True

    def check_instances_buttons(self) -> bool:
        '''
        inspect the existence of all buttons

        Args:
            None

       Returns:
            if there is an instance of all buttons in existence
        '''
        if not isinstance(self.button_fl, Digital):
            log('Button front left is not initialized!', in_exception=True)
            raise TypeError('Button front left is not initialized!')

        if not isinstance(self.button_fr, Digital):
            log('Button front right is not initialized!', in_exception=True)
            raise TypeError('Button front right is not initialized!')

        if not isinstance(self.button_bl, Digital):
            log('Button back left is not initialized!', in_exception=True)
            raise TypeError('Button back left is not initialized!')

        if not isinstance(self.button_br, Digital):
            log('Button back right is not initialized!', in_exception=True)
            raise TypeError('Button back right is not initialized!')

        return True

    # ===================== CALIBRATE BIAS =====================
    def auto_calibration(self, times: int, on_line: bool) -> None:
        '''
        Automatically calibrates as often as you wish

        Args:
            times (int): The number of times it should calibrate
            on_line (bool): If it is already perfectly aligned in the middle of a black line (True) or if it still has to align itself (False)

        Returns:
            None
        '''
        line_found = on_line
        for i in range(times):
            self.calibrate(on_line=line_found, output=False)
            self.break_all_motors()
            line_found = True
            print(f'=== {i+1} / {times} times calibrated ===', flush=True)
        log('AUTO CALIBRATION DONE')


    def calibrate(self, on_line:bool = False, output:bool = True) -> None:
        '''
        Calibrates all necessairy bias

        Args:
            on_line (bool): If it is already perfectly aligned in the middle of a black line (True) or if it still has to align itself (False, default)
            output (bool): If it should make an output, that it is done calibrating (True, default) or not (False)

        Returns:
            None. Writes bias into files
        '''
        self.calibrate_gyro_y(counter=1, max=4)
        self.calibrate_accel_z(counter=2, max=4)
        self.calibrate_gyro_z(counter=3, max=4)
        self.calibrate_accel_y(counter=4, max=4)
        self.bias_gyro_y = self.get_bias_gyro_y(True)
        self.bias_accel_z = self.get_bias_accel_y(True)
        self.bias_gyro_z = self.get_bias_gyro_z(True)
        self.bias_accel_y = self.get_bias_accel_y(True)
        self.calibrate_degrees(on_line=on_line, output=output)
        self.ONEEIGHTY_DEGREES_SECS = self.get_degrees(True)
        self.NINETY_DEGREES_SECS =  self.ONEEIGHTY_DEGREES_SECS / 2
        if output:
            log('CALIBRATION DONE', important=True)

    def calibrate_degrees(self, on_line: bool = False, output:bool = True) -> None:
        '''
        drive to the side until a black line was found and then slowly turn 180 degrees to know how long it takes to make one 180B0 turn

        Args:
            on_line (bool): If it is already perfectly aligned in the middle of a black line (True) or if it still has to align itself (False, default)
            output (bool): If it should make an output, that it is done calibrating (True, default) or not (False)

       Returns:
            None (but sets a class variable)
        '''
        self.check_instance_light_sensors_middle()
        if not on_line:
            self.drive_side_condition_analog('left', self.light_sensor_front, '<', self.light_sensor_front.get_value_black() - self.light_sensor_front.get_bias(), speed=self.ds_speed // 2)
            k.msleep(1000)
        startTime = time.time()
        while k.seconds() - startTime < (1200) / 1000:
            self.fl_wheel.drive(self.fl_wheel.get_default_speed()//2)
            self.fr_wheel.drive(-self.fl_wheel.get_default_speed()//2)
            self.bl_wheel.drive(self.fl_wheel.get_default_speed()//2)
            self.br_wheel.drive(-self.fl_wheel.get_default_speed()//2)
        while self.light_sensor_front.sees_white():
            self.fl_wheel.drive(self.fl_wheel.get_default_speed()//2)
            self.fr_wheel.drive(-self.fl_wheel.get_default_speed()//2)
            self.bl_wheel.drive(self.fl_wheel.get_default_speed()//2)
            self.br_wheel.drive(-self.fl_wheel.get_default_speed()//2)
        while self.light_sensor_back.sees_white():
            self.fl_wheel.drive(self.fl_wheel.get_default_speed()//2)
            self.fr_wheel.drive(-self.fl_wheel.get_default_speed()//2)
            self.bl_wheel.drive(self.fl_wheel.get_default_speed()//2)
            self.br_wheel.drive(-self.fl_wheel.get_default_speed()//2)
        endTime = time.time()
        self.break_all_motors()
        self.ONEEIGHTY_DEGREES_SECS = (endTime - startTime) * 0.73
        self.NINETY_DEGREES_SECS = endTime - startTime
        if output:
            log('DEGREES CALIBRATED')

    def calibrate_gyro_z(self, counter: int = None, max: int = None, times: int = 8000) -> None:
        '''
        calibrates the bias from the gyro to be able to drive straight, since the bias is for telling us how far off from driving straight the wombat is

        Args:
            counter (int): the number where it is at the moment
            max (int): how many caLibrations there are (to show it on the screen and for debugging usage)
            times (int, optional): how many calibrations should be done (default: 8000)

        Returns:
            None
        '''
        i: int = 0
        avg: float = 0
        while i < times:
            avg += k.gyro_z()
            k.msleep(1)
            i += 1
        self.bias_gyro_z = avg / time
        if counter is not None and max is not None:
            log(f'{counter}/{max} - GYRO Z CALIBRATED')

    def calibrate_gyro_y(self, counter: int = None, max: int = None, times: int = 8000) -> None:
        '''
        calibrates the bias from the gyro to be able to drive straight, since the bias is for telling us how far off from driving straight the wombat is (theoretically it is for driving sideways)

        Args:
            counter (int, default): the number where it is at the moment (default: None)
            max (int, default): how many caLibrations there are (to show it on the screen and for debugging usage) (default: None)
            times (int, optional): how many calibrations should be done (default: 8000)

        Returns:
            None
        '''
        i: int = 0
        avg: float = 0
        time: int = 8000
        while i < time:
            avg += k.gyro_y()
            k.msleep(1)
            i += 1
        self.bias_gyro_y = avg / time
        if counter is not None and max is not None:
            log(f'{counter}/{max} - GYRO Y CALIBRATED')

    def calibrate_accel_z(self, counter: int = None, max: int = None, times: int = 8000) -> None:
        '''
        calibrates the bias from the accelerometer to know how fast the wombat is going towards the x-axis(accelerometer is not yet in use though)

        Args:
            counter (int, optional): the number where it is at the moment (default: None)
            max (int, optional): how many caLibrations there are (to show it on the screen and for debugging usage) (default: None)
            times (int, optional): how many calibrations should be done (default: 8000)

        Returns:
            None
        '''
        i: int = 0
        avg: float = 0
        while i < times:
            avg += k.accel_z()
            k.msleep(1)
            i += 1
        self.bias_accel_z = avg / time
        if counter is not None and max is not None:
            log(f'{counter}/{max} - ACCEL X CALIBRATED')

    def calibrate_accel_y(self, counter: int = None, max: int = None, times: int = 8000) -> None:
        '''
        calibrates the bias from the accelerometer to know how fast the wombat is going towards the y-axis(accelerometer is not yet in use though)

        Args:
            counter (int, optional): the number where it is at the moment (default: None)
            max (int, optional): how many caLibrations there are (to show it on the screen and for debugging usage) (default: None)
            times (int, optional): how many calibrations should be done (default: 8000)

        Returns:
            None
        '''
        i: int = 0
        avg: float = 0
        while i < times:
            avg += k.accel_y()
            k.msleep(1)
            i += 1
        self.bias_accel_y = avg / time
        if counter is not None and max is not None:
            log(f'{counter}/{max} - ACCEL Y CALIBRATED')

    def calibrate_distance(self, start_mm: int, min_sensor_value: int, speed: int = None, step: float = 0.1) -> None:
        '''
        calibrates the values for the distance sensor. HINT: calibrate the gyro first (if you did not already do that), so it drives straight. Also it calibrates one time, make sure it is as accurate as possible.
        It needs to be 800mm away from an object and both object has to be as parallel to each other as possible.

        Args:
            start_mm (int): known starting distance (e.g. 95)
            max_sensor_value (int): the value until where the robot should drive (the lower the value,
            speed (int, optional): constant speed (default: ds_speed)
            step (float, optional): time between two measurements (default: 0.1)


        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed

        self.check_instance_distance_sensor()

        if self.mm_per_sec == 0:
            log('You need to calibrate the mm per sec first. Execute the function calibrate_mm_per_sec first!', important=True, in_exception=True)
            raise ValueError(
                'You need to calibrate the mm per sec first. Execute the function calibrate_mm_per_sec first!')

        self.distance_far_values = []
        self.distance_far_mm = []

        threading.Thread(target=self.drive_straight, args=(9999999, -speed//2,)).start()

        start_time = time.time()

        while True:
            elapsed = (time.time() - start_time) / 2
            traveled = self.mm_per_sec * elapsed
            current_mm = max(start_mm + traveled, 0)

            sensor_value = self.distance_sensor.current_value()

            self.distance_far_values.append(sensor_value)
            self.distance_far_mm.append(int(current_mm))

            if sensor_value <= min_sensor_value:
                break

            time.sleep(step)
        self.break_all_motors(True)
        self.get_distances(calibrated=True)

        log(f"Calibration finished. {len(self.distance_far_mm)} datapoints collected.")

    def calibrate_mm_per_sec(self, millis: int = 5000, speed: int = None) -> None:
        '''
        calibrates the mm per second. You need to mark the beginning on where it began to drive from, since you need to know how far it went (in mm)

        Args:
            millis (int, optional): How long it should drive (in milliseconds) (default: 5000)
            speed (int, optional): How fast it should drive (default: ds_speed)

        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed

        start_time = time.time()
        self.drive_straight(speed=speed, millis=millis)
        sec = time.time() - start_time
        mm = int(input('How many mm did the robot drive from the beginning on?: '))

        self.mm_per_sec = mm/sec
        self.set_TOTAL_mm_per_sec(mm=mm, sec=sec)

    # ================== GET / OVERWRITE BIAS ==================
    def get_mm_per_sec(self, only_mm: bool = False, only_sec: bool = False) -> None:  # @TODO schauen, wie man float ODER int (ODER list) zurückgeben kann als typ
        '''
        Getting the mm, sec, mm and sec or total it takes to drive a certain distance (in mm)

        Args:
            only_mm (bool, optional): If you specifically need the mm
            only_sec (bool, optional): If you specifically need the sec

        Returns:
            One of the following options:
                - List[int, float]: the mm and time in seconds it takes to drive
                - int: the mm of distance for driving
                - float: time in seconds for driving
                - float: calculated value of mm/sec
        '''

        text = file_Manager.reader(self.mm_per_sec_file).split('\n')
        total = float(text[0])
        mm = int(text[1])
        sec = float(text[2])

        if only_mm and only_sec:
            return mm, sec
        if only_mm:
            return mm
        if only_sec:
            return sec
        return total

    def get_distances(self, calibrated: bool = False) -> tuple:
        '''
        Getting the disances from the distances_arr.txt file

        Args:
            calibrated (bool, optional): Writing to the file distances_arr.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            tuple[list[int], list[int]] | None:
                If calibrated=False: (values, mm)
                If calibrated=True: None
        '''
        file_name = os.path.join(BIAS_FOLDER, 'distances_arr.txt')

        try:
            if calibrated:
                with open(file_name, "w") as f:
                    f.write("value=" + ",".join(map(str, self.distance_far_values)) + "\n")
                    f.write("mm=" + ",".join(map(str, self.distance_far_mm)) + "\n")
                log(f"Distances saved to {file_name}")

            else:
                if not os.path.exists(file_name):
                    raise FileNotFoundError(f"{file_name} not found. Run calibration first.")

                with open(file_name, "r") as f:
                    lines = f.readlines()

                values = []
                mm = []

                for line in lines:
                    if line.startswith("value="):
                        values = list(map(int, line.strip().split("=")[1].split(",")))
                    elif line.startswith("mm="):
                        mm = list(map(int, line.strip().split("=")[1].split(",")))

                if not values or not mm:
                    raise ValueError("File format is invalid or empty.")

                return values, mm

        except Exception as e:
            log(str(e), important=True, in_exception=True)
            return None


    def get_current_standard_gyro(self, reverse: bool = False) -> int:
        '''
        Getting the current value of the bias depending on if the controller is standing or laying down

        Args:
            reverse (bool): it it should return the reversed value or not

        Returns:
            int: the gyro_z or gyro_y value
        '''
        if reverse:
            return k.gyro_z() if self.standing else k.gyro_y()
        return k.gyro_y() if self.standing else k.gyro_z()


    def get_degrees(self, calibrated: bool = False) -> float:
        '''
        Getting the average degrees from the bias_degrees.txt file

        Args:
            calibrated (bool, optional): Writing to the file bias_degrees.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            Average of the bias_degrees.txt file (optionally with the recent calibrated bias as well)
        '''
        avg = 0
        file_name = os.path.join(BIAS_FOLDER, 'bias_degrees.txt')
        try:
            temp_deg = file_Manager.reader(file_name)
            if calibrated:
                avg = (float(temp_deg) + self.ONEEIGHTY_DEGREES_SECS) / 2
                file_Manager.writer(file_name, 'w', avg)
            else:
                avg = float(temp_deg)

            return avg
        except Exception as e:
            log(str(e), important=True, in_exception=True)


    def get_bias_gyro_z(self, calibrated: bool = False) -> float:
        '''
        Getting the average bias from the bias_gyro_z.txt file

        Args:
            calibrated (bool, optional): Writing to the file bias_gyro_z.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            Average of the bias_gyro_z.txt file (optionally with the recent calibrated bias as well)
        '''
        avg = 0
        file_name = os.path.join(BIAS_FOLDER, 'bias_gyro_z.txt')
        try:
            with open(file_name, "r") as f:
                temp_bias = f.read()
                if calibrated:
                    avg = (float(temp_bias) + self.bias_gyro_z) / 2
                    file_Manager.writer(file_name, 'w', avg)
                else:
                    avg = float(temp_bias)
            return avg
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def get_bias_gyro_y(self, calibrated: bool = False) -> float:
        '''
        Getting the average bias from the bias_gyro_y.txt file

        Args:
            calibrated (bool, optional): Writing to the file bias_gyro_y.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            Average of the bias_gyro_y.txt file (optionally with the recent calibrated bias as well)
        '''
        avg = 0
        file_name = os.path.join(BIAS_FOLDER, 'bias_gyro_y.txt')
        try:
            with open(file_name, "r") as f:
                temp_bias = f.read()
                if calibrated:
                    avg = (float(temp_bias) + self.bias_gyro_y) / 2
                    file_Manager.writer(file_name, 'w', avg)
                else:
                    avg = float(temp_bias)
            return avg
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def get_bias_accel_z(self, calibrated: bool = False) -> float:
        '''
        Getting the average bias from the bias_accel_z.txt file

        Args:
            calibrated (bool, optional): Writing to the file bias_accel_z.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            Average of the bias_accel_z.txt file (optionally with the recent calibrated bias as well)
        '''
        avg = 0
        file_name = os.path.join(BIAS_FOLDER, 'bias_accel_z.txt')
        try:
            with open(file_name, "r") as f:
                temp_bias = f.read()
                if calibrated:
                    avg = (float(temp_bias) + self.bias_accel_z) / 2
                    file_Manager.writer(file_name, 'w', avg)
                else:
                    avg = float(temp_bias)
            return avg
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def get_bias_accel_y(self, calibrated: bool = False) -> float:
        '''
        Getting the average bias from the bias_accel_y.txt file

        Args:
            calibrated (bool, optional): Writing to the file bias_accel_y.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            Average of the bias_accel_y.txt file (optionally with the recent calibrated bias as well)
        '''
        avg = 0
        file_name = os.path.join(BIAS_FOLDER, 'bias_accel_y.txt')
        try:
            with open(file_name, "r") as f:
                temp_bias = f.read()
                if calibrated:
                    avg = (float(temp_bias) + self.bias_accel_y) / 2
                    file_Manager.writer(file_name, 'w', avg)
                else:
                    avg = float(temp_bias)
            return avg
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def get_standard_speed(self) -> int:
        '''
        Getting the default speed on which the robot moves

        Args:
            None

        Returns:
            int: the speed it is set to
        '''
        return self.ds_speed

    # ======================== PUBLIC METHODS =======================

    def drive_side(self, direction: str, millis: int, speed: int = None) -> None:
        '''
        drive sideways for as long as you want to (in millis)

        Args:
            direction (str): "left" or "right", depending on where you want to go
            millis (int): for how long you want to drive sideways
            speed (int, optional): the speed it is going to drive sideways (default: ds_speed)

        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed
        startTime: float = k.seconds()
        motor_id = self._manage_motor_stopper(True)
        theta = 0
        t = 10
        adjuster = 100
        lower_theta = 500
        higher_theta = 3000
        speed = abs(speed)
        if direction == 'right':
            while k.seconds() - startTime < (millis) / 1000 and self.is_motor_active(motor_id):
                if lower_theta > theta > -lower_theta:
                    self.fl_wheel.drive(speed)
                    self.fr_wheel.drive(-speed)
                    self.bl_wheel.drive(-speed)
                    self.br_wheel.drive(speed)
                elif -lower_theta > theta > -higher_theta:
                    self.fl_wheel.drive(speed - adjuster)
                    self.fr_wheel.drive(-speed - adjuster)
                    self.bl_wheel.drive(-speed + adjuster)
                    self.br_wheel.drive(speed - adjuster)
                elif lower_theta < theta < higher_theta:
                    self.fl_wheel.drive(speed + adjuster)
                    self.fr_wheel.drive(-speed - adjuster)
                    self.bl_wheel.drive(-speed + adjuster)
                    self.br_wheel.drive(speed + adjuster)
                elif theta < -higher_theta:
                    k.ao()
                    self.fr_wheel.drive_mfw()
                    self.br_wheel.drive_mbw()
                    theta = 0
                elif theta > higher_theta:
                    k.ao()
                    self.fl_wheel.drive_mbw()
                    self.bl_wheel.drive_mbw()
                    theta = 0

                k.msleep(t)
                theta += (self.get_current_standard_gyro(True) - self.rev_standard_bias_gyro) * 3

        elif direction == 'left':
            while k.seconds() - startTime < (millis) / 1000 and self.is_motor_active(motor_id):
                if lower_theta > theta > -lower_theta:
                    self.fl_wheel.drive(-speed)
                    self.fr_wheel.drive(speed)
                    self.bl_wheel.drive(speed)
                    self.br_wheel.drive(-speed)
                elif -lower_theta > theta > -higher_theta:
                    self.fl_wheel.drive(-speed + adjuster)
                    self.fr_wheel.drive(speed + adjuster)
                    self.bl_wheel.drive(speed - adjuster)
                    self.br_wheel.drive(-speed + adjuster)
                elif lower_theta < theta < higher_theta:
                    self.fl_wheel.drive(-speed - adjuster)
                    self.fr_wheel.drive(speed + adjuster)
                    self.bl_wheel.drive(speed - adjuster)
                    self.br_wheel.drive(-speed - adjuster)
                elif theta < -higher_theta:
                    k.ao()
                    self.fr_wheel.drive_mbw()
                    self.br_wheel.drive_mfw()
                    theta = 0
                elif theta > higher_theta:
                    k.ao()
                    self.fl_wheel.drive_mfw()
                    self.bl_wheel.drive_mfw()
                    theta = 0

                k.msleep(t)
                theta += (self.get_current_standard_gyro(True) - self.rev_standard_bias_gyro) * 3
        else:
            log('Only "right" and "left" are valid commands for the direction!', in_exception=True)
            raise ValueError('drive_side() Exception: Only "right" and "left" are valid commands for the direction!')

        self.break_all_motors()
        self._manage_motor_stopper(False)


    def drive_straight(self, millis: int, speed: int = None) -> None:
        '''
        drive straight for as long as you want to (in millis)

        Args:
            millis (int): for how long you want to drive straight
            speed (int, optional): the speed it is going to drive straight (default: ds_speed)

        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed
        startTime: float = k.seconds()
        motor_id = self._manage_motor_stopper(True)
        theta = 0
        adjuster = 100
        self.break_all_motors()
        while k.seconds() - startTime < (millis) / 1000 and self.is_motor_active(motor_id):
            if 1000 > theta > -1000:
                self.fl_wheel.drive(speed)
                self.fr_wheel.drive(speed)
                self.bl_wheel.drive(speed)
                self.br_wheel.drive(speed)
            elif theta > 1000:
                self.fl_wheel.drive(speed - adjuster)
                self.fr_wheel.drive(speed + adjuster)
                self.bl_wheel.drive(speed - adjuster)
                self.br_wheel.drive(speed + adjuster)
            else:
                self.fl_wheel.drive(speed + adjuster)
                self.fr_wheel.drive(speed - adjuster)
                self.bl_wheel.drive(speed + adjuster)
                self.br_wheel.drive(speed - adjuster)
            k.msleep(10)
            theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 1.5
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def drive_diagonal(self, end: str, side: str, millis: int, speed: int = None) -> None:
        # side -> left + right
        # end -> front + back
        '''
        drive diagonal for as long as you want to (in millis)

        Args:
            end (str): "front" or "back", depending on where you want to go (either backwards or forwards)
            side (str): "left" or "right", depending on where you want to go
            millis (int): for how long you want to drive sideways
            speed (int, optional): the speed it is going to drive sideways (default: ds_speed)

        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed
        motor_id = self._manage_motor_stopper(True)
        if end != 'front' and end != 'back':
            log('Only "front" or "back" are valid options for the "end" parameter', in_exception=True)
            raise ValueError(
                'drive_diagonal() Exception: Only "front" or "back" are valid options for the "end" parameter')

        if side != 'right' and side != 'left':
            log('Only "right" or "left" are valid options for the "side" parameter', in_exception=True)
            raise ValueError(
                'drive_diagonal() Exception: Only "right" or "left" are valid options for the "side" parameter')

        points = 0
        if end == 'front':
            points += 1
        if side == 'right':
            points += 1

        startTime: float = k.seconds()
        theta_z = 0
        adjuster = 100
        if side == 'left':
            adjuster = -adjuster
        speed = abs(speed)
        instances_left = self.fr_wheel, self.bl_wheel
        instances_right = self.fl_wheel, self.br_wheel
        instances = instances_left
        if side == 'right':
            instances = instances_right
        if end == 'back':
            speed = -speed
            if self.fr_wheel in instances:  # its associated to the left
                instances = instances_right
            else:
                instances = instances_left

        if points == 2 or points == 0:
            while k.seconds() - startTime < (millis) / 1000 and self.is_motor_active(motor_id):
                if theta_z < -1200:
                    instances[0].drive(speed)
                    instances[1].drive(speed - adjuster)
                elif theta_z > 1200:
                    instances[0].drive(speed)
                    instances[1].drive(speed - adjuster)
                else:
                    instances[0].drive(speed)
                    instances[1].drive(speed)
                k.msleep(10)
                theta_z += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 1.5
        else:
            t = 10
            while k.seconds() - startTime < (millis) / 1000 and self.is_motor_active(motor_id):
                if t == 200:
                    t = 10
                    k.ao()
                if theta_z > 4000:
                    t = 200
                    theta_z = 0
                    self.br_wheel.drive(speed - speed//2)
                elif theta_z < -4000:
                    t = 200
                    theta_z = 0
                    self.fl_wheel.drive(-speed + speed//2)
                elif theta_z < -800:
                    instances[0].drive(speed - adjuster)
                    instances[1].drive(speed)
                elif theta_z > 800:
                    instances[0].drive(speed - adjuster)
                    instances[1].drive(speed)
                else:
                    instances[0].drive(speed)
                    instances[1].drive(speed)
                k.msleep(t)
                theta_z += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 1.5

        self.break_all_motors()
        self._manage_motor_stopper(False)

    def turn_degrees_far(self, direction: str, degree: int, speed=None) -> None:
        '''
        turn the amount of degrees given, to take a turn with only two wheels, resulting in a turn not on the spot

        Args:
            direction (str): "left" or "right", depending on where you want to go
            degree (int): the amount of degrees (B0) to turn from the current point (only values from 0 - 180 allowed for maximum efficiency)

        Returns:
            None
        '''
        if direction != 'right' and direction != 'left':
            log('Only "right" or "left" are valid options for the "direction" parameter', in_exception=True)
            raise ValueError(
                'turn_degrees_far() Exception: Only "right" or "left" are valid options for the "direction" parameter')

        if degree > 180 and degree < 0:
            log('Only values from range 0 - 180 are valid for the "degree" parameter', in_exception=True)
            raise ValueError(
                'turn_degrees_far() Exception: Only values from range 0 - 180 are valid for the "degree" parameter')

        if speed is None:
            speed = self.ds_speed + 100  # +100 to make it drive full speed (capped at 1500 and ds_speed is just 1400)
        elif speed == -self.ds_speed:
            speed -= 100  # -100 to make it drive full speed (capped at -1500 and "ds_speed" is in this case just -1400)
        elif speed == self.ds_speed:
            speed += 100  # +100 to make it drive full speed (capped at 1500 and ds_speed is just 1400)
        motor_id = self._manage_motor_stopper(True)
        div = 180 / degree
        value = self.ONEEIGHTY_DEGREES_SECS / div
        if degree <= 90:
            div = 90 / degree
            value = self.NINETY_DEGREES_SECS / div

        start_time = time.time()
        if direction == 'right':
            while time.time() - start_time < 2 * value and self.is_motor_active(motor_id):
                self.fl_wheel.drive(speed)
                self.bl_wheel.drive(speed)
        elif direction == 'left':
            while time.time() - start_time < 2 * value and self.is_motor_active(motor_id):
                self.fr_wheel.drive(speed)
                self.br_wheel.drive(speed)
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def turn_degrees(self, direction: str, degree: int) -> None:
        '''
        turn the amount of degrees given, to take a turn with all four wheels, resulting in a turn on the spot

        Args:
            direction (str): "left" or "right", depending on where you want to go
            degree (int): the amount of degrees (B0) to turn from the current point (only values from 0 - 180 allowed for maximum efficiency)

        Returns:
            None
        '''
        if direction != 'right' and direction != 'left':
            log('Only "right" or "left" are valid options for the "direction" parameter', in_exception=True)
            raise ValueError(
                'turn_degrees() Exception: Only "right" or "left" are valid options for the "direction" parameter')

        if degree > 180 and degree < 1:
            log('Only values from range 1 - 180 are valid for the "degree" parameter', in_exception=True)
            raise ValueError(
                'turn_degrees_far() Exception: Only values from range 1 - 180 are valid for the "degree" parameter')
        motor_id = self._manage_motor_stopper(True)
        div = 180 / degree
        value = self.ONEEIGHTY_DEGREES_SECS / div
        if degree <= 90:
            div = 90 / degree
            value = self.NINETY_DEGREES_SECS / div

        start_time = time.time()
        if direction == 'right':
            while time.time() - start_time < value and self.is_motor_active(motor_id):
                self.fl_wheel.drive_mfw()
                self.fr_wheel.drive_mbw()
                self.bl_wheel.drive_mfw()
                self.br_wheel.drive_mbw()
        elif direction == 'left':
            while time.time() - start_time < value and self.is_motor_active(motor_id):
                self.fl_wheel.drive_mbw()
                self.fr_wheel.drive_mfw()
                self.bl_wheel.drive_mbw()
                self.br_wheel.drive_mfw()
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def drive_side_til_mm_found(self, mm_to_object: int, direction: str, speed: int = None) -> None:
        '''
        turn the amount of degrees given, to take a turn with basically only two, resulting in a turn not on the spot
        This function might me unreliable! keep track of the distances!

        Args:
            mm_to_object (int): the distance (in mm) between the distance sensor and the object in front of the sensor
            direction (str): "left" or "right", depending on where you want to go
            speed (int, optional): the speed it is going to drive straight (default: ds_speed)

        Returns:
            None
        '''
        motor_id = self._manage_motor_stopper(True)
        if speed is None:
            speed = self.ds_speed
        if direction != 'right' and direction != 'left':
            log('Only "right" or "left" are valid options for the "direction" parameter', in_exception=True)
            raise ValueError(
                'drive_side_til_mm_found() Exception: Only "right" or "left" are valid options for the "direction" parameter')
        if self.distance_far_values == 0 and self.distance_far_mm == 0:
            log('You need to calibrate the distance using the calibrate_distance function first!', important=True, in_exception=True)
            raise ValueError('You need to calibrate the distance using the calibrate_distance function first!')

        self.isClose = False
        theta = 0
        t = 10
        adjuster = 100
        lower_theta = 500
        higher_theta = 3000
        speed = abs(speed)
        combination = dict(zip(self.distance_far_mm, self.distance_far_values))
        next_step = min(combination, key=lambda x: abs(x - mm_to_object))
        next_value = combination[next_step]

        def distance_stopper():
            tolerance = mm_to_object / 20  # /20 makes it that it is 90% accurate
            try:
                lookup = interp1d(self.distance_far_values, self.distance_far_mm, kind='linear',
                                  fill_value="extrapolate")
            except Exception as e:
                log(str(e), important=True, in_exception=True)

            def get_distance_from_sensor(sensor_value):
                return float(lookup(sensor_value))

            def is_target_distance_reached():
                value = self.distance_sensor.current_value()
                dist = get_distance_from_sensor(value)
                if str(dist) == 'inf' or dist <= self.distance_far_mm[0]:
                    return True
                return dist < mm_to_object + tolerance

            while self.is_motor_active(motor_id):
                if is_target_distance_reached():
                    self.isClose = True
                    sys.exit()
                    break

        threading.Thread(target=distance_stopper).start()
        if direction == 'right':
            while not self.isClose and self.is_motor_active(motor_id):
                if lower_theta > theta > -lower_theta:
                    self.fl_wheel.drive(speed)
                    self.fr_wheel.drive(-speed)
                    self.bl_wheel.drive(-speed)
                    self.br_wheel.drive(speed)
                elif -lower_theta > theta > -higher_theta:
                    self.fl_wheel.drive(speed - adjuster)
                    self.fr_wheel.drive(-speed - adjuster)
                    self.bl_wheel.drive(-speed + adjuster)
                    self.br_wheel.drive(speed - adjuster)
                elif lower_theta < theta < higher_theta:
                    self.fl_wheel.drive(speed + adjuster)
                    self.fr_wheel.drive(-speed - adjuster)
                    self.bl_wheel.drive(-speed + adjuster)
                    self.br_wheel.drive(speed + adjuster)
                elif theta < -higher_theta:
                    k.ao()
                    self.fr_wheel.drive_mfw()
                    self.br_wheel.drive_mbw()
                    theta = 0
                elif theta > higher_theta:
                    k.ao()
                    self.fl_wheel.drive_mbw()
                    self.bl_wheel.drive_mbw()
                    theta = 0

                k.msleep(t)
                theta += (self.get_current_standard_gyro(True) - self.rev_standard_bias_gyro) * 3

        elif direction == 'left':
            while not self.isClose and self.is_motor_active(motor_id):
                if lower_theta > theta > -lower_theta:
                    self.fl_wheel.drive(-speed)
                    self.fr_wheel.drive(speed)
                    self.bl_wheel.drive(speed)
                    self.br_wheel.drive(-speed)
                elif -lower_theta > theta > -higher_theta:
                    self.fl_wheel.drive(-speed + adjuster)
                    self.fr_wheel.drive(speed + adjuster)
                    self.bl_wheel.drive(speed - adjuster)
                    self.br_wheel.drive(-speed + adjuster)
                elif lower_theta < theta < higher_theta:
                    self.fl_wheel.drive(-speed - adjuster)
                    self.fr_wheel.drive(speed + adjuster)
                    self.bl_wheel.drive(speed - adjuster)
                    self.br_wheel.drive(-speed - adjuster)
                elif theta < -higher_theta:
                    k.ao()
                    self.fr_wheel.drive_mbw()
                    self.br_wheel.drive_mfw()
                    theta = 0
                elif theta > higher_theta:
                    k.ao()
                    self.fl_wheel.drive_mfw()
                    self.bl_wheel.drive_mfw()
                    theta = 0

                k.msleep(t)
                theta += (self.get_current_standard_gyro(True) - self.rev_standard_bias_gyro) * 3
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def drive_til_distance(self, mm_to_object: int, speed: int = None) -> None:
        # distance in mm
        '''
        drive straight as long as the object in front of the distance sensor (in mm) is not in reach

        Args:
            mm_to_object (int): the distance (in mm) between the distance sensor and the object in front of the sensor
            speed (int, optional): the speed it is going to drive straight (default: ds_speed)

        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed
        if mm_to_object > self.distance_far_mm[-1] or mm_to_object < 10:
            log(f'You can only put a value in range of 10 - {self.distance_far_mm[-1]} for the distance parameter!', in_exception=True)
            raise ValueError(
                f'drive_til_distance() Exception: You can only put a value in range of 10 - {self.distance_far_mm[-1]} for the distance parameter!')
        if self.distance_far_values == 0 and self.distance_far_mm == 0:
            log('You need to calibrate the distance using the calibrate_distance function first!', important=True, in_exception=True)
            raise ValueError('You need to calibrate the distance using the calibrate_distance function first!')

        self.check_instances_buttons_back()
        self.check_instance_distance_sensor()
        motor_id = self._manage_motor_stopper(True)
        self.isClose = False
        theta = 0.0
        adjuster = 100
        if self.distance_sensor.current_value() > 1800:
            while self.distance_sensor.current_value() > 1800 and (
                    not self.button_bl.is_pressed() and not self.button_br.is_pressed()) and self.is_motor_active(motor_id):  # this is because if it is already too close, it will back out a little bit to get the best result
                if 1000 > theta > -1000:  # left
                    self.fl_wheel.drive(-speed)
                    self.fr_wheel.drive(-speed)
                    self.bl_wheel.drive(-speed)
                    self.br_wheel.drive(-speed)
                elif theta > 1000:  # right
                    self.fl_wheel.drive(-speed - adjuster)
                    self.fr_wheel.drive(-speed + adjuster)
                    self.bl_wheel.drive(-speed - adjuster)
                    self.br_wheel.drive(-speed + adjuster)
                else:
                    self.fl_wheel.drive(-speed + adjuster)
                    self.fr_wheel.drive(-speed - adjuster)
                    self.bl_wheel.drive(-speed + adjuster)
                    self.br_wheel.drive(-speed - adjuster)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 1.5
            if theta != 0.0:
                self.fl_wheel.drive(speed)
                self.fr_wheel.drive(speed)
                self.bl_wheel.drive(speed)
                self.br_wheel.drive(speed)
                k.msleep(20)
                self.break_all_motors()

        combination = dict(zip(self.distance_far_mm, self.distance_far_values))
        next_step = min(combination, key=lambda x: abs(x - mm_to_object))
        next_value = combination[next_step]

        def distance_stopper():
            tolerance = mm_to_object / 20 # /20 makes it that it is 90% accurate
            try:
                lookup = interp1d(self.distance_far_values, self.distance_far_mm, kind='linear', fill_value="extrapolate")
            except Exception as e:
                log(str(e), important=True, in_exception=True)

            def get_distance_from_sensor(sensor_value):
                return float(lookup(sensor_value))

            def is_target_distance_reached():
                value = self.distance_sensor.current_value()
                dist = get_distance_from_sensor(value)
                if str(dist) == 'inf' or dist <= self.distance_far_mm[0]:
                    return True
                return dist < mm_to_object + tolerance

            while self.is_motor_active(motor_id):
                if is_target_distance_reached():
                    self.isClose = True
                    sys.exit()
                    break

        if self.distance_sensor.current_value() < next_value:
            threading.Thread(target=distance_stopper).start()

            while not self.isClose and self.is_motor_active(motor_id):
                if 1000 > theta > -1000:  # left
                    self.fl_wheel.drive(speed)
                    self.fr_wheel.drive(speed)
                    self.bl_wheel.drive(speed)
                    self.br_wheel.drive(speed)
                elif theta > 1000:  # right
                    self.fl_wheel.drive(speed - adjuster)
                    self.fr_wheel.drive(speed + adjuster)
                    self.bl_wheel.drive(speed - adjuster)
                    self.br_wheel.drive(speed + adjuster)
                else:
                    self.fl_wheel.drive(speed + adjuster)
                    self.fr_wheel.drive(speed - adjuster)
                    self.bl_wheel.drive(speed + adjuster)
                    self.br_wheel.drive(speed - adjuster)

                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 1.5

        if mm_to_object < self.distance_far_mm[0]:
            counter = self.distance_far_mm[0]
            mult = self.ds_speed / speed
            timer = 0.001 * mult
            while counter > mm_to_object and self.is_motor_active(motor_id):
                counter -= 1
                if 1000 > theta > -1000:  # left
                    self.fl_wheel.drive(speed)
                    self.fr_wheel.drive(speed)
                    self.bl_wheel.drive(speed)
                    self.br_wheel.drive(speed)
                elif theta > 1000:  # right
                    self.fl_wheel.drive(speed - adjuster)
                    self.fr_wheel.drive(speed + adjuster)
                    self.bl_wheel.drive(speed - adjuster)
                    self.br_wheel.drive(speed + adjuster)
                else:
                    self.fl_wheel.drive(speed + adjuster)
                    self.fr_wheel.drive(speed - adjuster)
                    self.bl_wheel.drive(speed + adjuster)
                    self.br_wheel.drive(speed - adjuster)
                time.sleep(timer)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 1.5

        self.break_all_motors()
        self._manage_motor_stopper(False)

    def break_motor(self, *args) -> None:
        '''
        immediately stop the motor(s) of the given port

        Args:
            *args: All of the desired (motor) ports which should be stopped

        Returns:
            None
        '''
        try:
            if isinstance(args[0], int):
                for port in args:
                    k.freeze(port)
            elif isinstance(args[0], WheelR):
                for wheel in args:
                    wheel.stop()
            else:
                log('Only integer (port number) or WheelR instance are allowed!', in_exception=True)
                raise TypeError('Only integer (port number) or WheelR instance are allowed!')
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def break_all_motors(self, stop:bool = False) -> None:
        '''
        immediately stop all motors

        Args:
            stop (bool, optional): If it should be turned off completly and everywhere (True), or just stop driving (False, default)

        Returns:
            None
        '''
        self.fl_wheel.stop()
        self.fr_wheel.stop()
        self.bl_wheel.stop()
        self.br_wheel.stop()
        if stop:
            self._manage_motor_stopper(False)

    def shake_side(self, times: int, millis: int = 90) -> None:
        '''
        drive right and left in small steps

        Args:
            times (int): how often it should shake itself
            millis (int, optional): how long it should drive left and right (default: 90)

        Returns:
            None
        '''
        motor_id = self._manage_motor_stopper(True)
        for i in range(times):
            if self.is_motor_active(motor_id):
                self.drive_side('right', millis)
                self.break_all_motors()
                self.drive_side('left', millis)
                self.break_all_motors()
            else:
                break
        self._manage_motor_stopper(False)

    def align_drive_front(self, drive_bw: bool = True, max_millis: int = 9999999) -> None:
        '''
        aligning front by bumping into something, so both buttons on the front will be pressed. If there's an error by pressing the buttons, a fail save will occur. If at will it also drive backwards a little bit to be able to turn after it bumped into something

        Args:
            drive_bw (bool, optional): If you desire to drive back a little bit (default: True) -> (but sometimes you want to stay aligned at the object)
            max_millis (int, optional): The maximum amount of time (in milliseconds) on how long it can try to align itself (default: 9999999)

        Returns:
            None

        '''
        self.check_instances_buttons_front()
        motor_id = self._manage_motor_stopper(True)
        startTime: float = k.seconds()
        while k.seconds() - startTime < (max_millis) / 1000 and self.is_motor_active(motor_id):
            if self.button_fl.is_pressed() and self.button_fr.is_pressed():
                break
            elif self.button_fl.is_pressed():
                self.break_all_motors()
                self.fl_wheel.drive(-self.fl_wheel.get_default_speed()//2)
                self.fr_wheel.drive_dfw()
            elif self.button_fr.is_pressed():
                self.break_all_motors()
                self.fr_wheel.drive(-self.fl_wheel.get_default_speed()//2)
                self.fl_wheel.drive_dfw()
            else:
                self.fr_wheel.drive_dfw()
                self.fl_wheel.drive_dfw()
                self.br_wheel.drive_dfw()
                self.bl_wheel.drive_dfw()
        self.break_all_motors()
        if drive_bw:
            self.fr_wheel.drive_dbw()
            self.fl_wheel.drive_dbw()
            self.br_wheel.drive_dbw()
            self.bl_wheel.drive_dbw()
            k.msleep(100)
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def align_drive_back(self, drive_fw: bool = True, max_millis: int = 9999999) -> None:
        '''
        aligning back by bumping into something, so both buttons on the back will be pressed. If there's an error by pressing the buttons, a fail save will occur. If at will it also drive forwards a little bit to be able to turn after it bumped into something

        Args:
            drive_fw (bool, optional): If you desire to drive forward a little bit (default: True) -> (but sometimes you want to stay aligned at the object)
            max_millis (int, optional): The maximum amount of time (in milliseconds) on how long it can try to align itself (default: 9999999)

        Returns:
            None
        '''
        self.check_instances_buttons_back()
        motor_id = self._manage_motor_stopper(True)
        startTime: float = k.seconds()
        while k.seconds() - startTime < (max_millis) / 1000 and self.is_motor_active(motor_id):
            if self.button_br.is_pressed() and self.button_bl.is_pressed():
                break
            elif self.button_br.is_pressed():
                self.break_all_motors()
                self.bl_wheel.drive_dbw()
                self.br_wheel.drive(self.br_wheel.get_default_speed()//2)
            elif self.button_bl.is_pressed():
                self.break_all_motors()
                self.br_wheel.drive_dbw()
                self.bl_wheel.drive(self.br_wheel.get_default_speed() // 2)
            else:
                self.fr_wheel.drive_dbw()
                self.fl_wheel.drive_dbw()
                self.br_wheel.drive_dbw()
                self.bl_wheel.drive_dbw()
        self.break_all_motors()
        if drive_fw:
            self.fr_wheel.drive_dfw()
            self.fl_wheel.drive_dfw()
            self.br_wheel.drive_dfw()
            self.bl_wheel.drive_dfw()
            k.msleep(50)
            self.break_all_motors()
        self._manage_motor_stopper(False)

    def drive_straight_condition_digital(self, Instance: Digital, condition: str, value: int, millis: int = 9999999, speed: int = None):
        # @TODO -> test this out
        '''
        drive straight until an digital value gets reached for the desired instance

        Args:
            Instance (Digital): just has to be from something digital (buttons)
            condition (str): should it match "==" or not "!="
            value (int): The value that the current value gets compared to and has to be reached / not matched
            millis (int, optional): The maximum amount of time (in milliseconds) which can be taken (default: 9999999)
            speed (int, optional): The speed it drives straight (default: ds_speed)

        Returns:
            None
        '''
        if speed is None:
            speed = self.ds_speed
        motor_id = self._manage_motor_stopper(True)
        theta = 0
        adjuster = 100
        start_time = k.seconds()

        if condition == "==":
            while (Instance.current_value() == value) and (k.seconds() - start_time < millis/1000) and self.is_motor_active(motor_id):
                if 1000 > theta > -1000:
                    self.fl_wheel.drive(speed)
                    self.fr_wheel.drive(speed)
                    self.bl_wheel.drive(speed)
                    self.br_wheel.drive(speed)
                elif theta > 1000:
                    self.fl_wheel.drive(speed - adjuster)
                    self.fr_wheel.drive(speed + adjuster)
                    self.bl_wheel.drive(speed - adjuster)
                    self.br_wheel.drive(speed + adjuster)
                else:
                    self.fl_wheel.drive(speed + adjuster)
                    self.fr_wheel.drive(speed - adjuster)
                    self.bl_wheel.drive(speed + adjuster)
                    self.br_wheel.drive(speed - adjuster)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 1.5
        elif condition == "!=":
            while (Instance.current_value() != value) and (k.seconds() - start_time < millis/1000) and self.is_motor_active(motor_id):
                if 1000 > theta > -1000:
                    self.fl_wheel.drive(speed)
                    self.fr_wheel.drive(speed)
                    self.bl_wheel.drive(speed)
                    self.br_wheel.drive(speed)
                elif theta > 1000:
                    self.fl_wheel.drive(speed - adjuster)
                    self.fr_wheel.drive(speed + adjuster)
                    self.bl_wheel.drive(speed - adjuster)
                    self.br_wheel.drive(speed + adjuster)
                else:
                    self.fl_wheel.drive(speed + adjuster)
                    self.fr_wheel.drive(speed - adjuster)
                    self.bl_wheel.drive(speed + adjuster)
                    self.br_wheel.drive(speed - adjuster)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 1.5
        else:
            log('Only "==" or "!=" is available for the condition!', important=True, in_exception=True)
            raise ValueError('Only "==" or "!=" is available for the condition!')
        print()
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def drive_side_condition_analog(self, direction: str, Instance, condition: str, value: int, millis: int = 9999999,
                                    speed: int = None) -> None:
        '''
        drive sideways until an analog value gets reached for the desired instance

        Args:
            direction (str): "left" or "right" - depends on where you want to go
            Instance: just has to be from something analog (since there is (as of time of creation) only light and distance sensors, which are valid for this argument, just those should be used.
            condition (str): ("let" / "<=") or ("get" / ">=") or ("ht" / ">") or ("lt" / "<") are valid. Notice: l -> less | h -> higher | e -> equal | t -> than. (The parentheses should be left out, as well as the slash, only choose one argument Example: ">=")
            value (int): The value that the current value gets compared to and has to be reached
            millis (int, optional): The maximum amount of time (in milliseconds) which can be taken (default: 9999999)
            speed (int, optional): The speed it drives sideways (default: ds_speed)

        Returns:
            None
        '''
        motor_id = self._manage_motor_stopper(True)
        if speed is None:
            speed = self.ds_speed
        if direction != 'right' and direction != 'left':
            log('Only "right" or "left" are valid arguments for the direction parameter!', in_exception=True)
            raise ValueError(
                'drive_side_condition_analog() Exception: Only "right" or "left" are valid arguments for the direction parameter! ')

        startTime: float = k.seconds()
        theta = 0
        t = 10
        adjuster = 100
        lower_theta = 500
        higher_theta = 3000
        speed = abs(speed)
        if condition == 'let' or condition == '<=':  # let -> less or equal than
            while (Instance.current_value() <= value) and (k.seconds() - startTime < (millis) / 1000) and self.is_motor_active(motor_id):
                if direction == 'right':
                    if lower_theta > theta > -lower_theta:
                        self.fl_wheel.drive(speed)
                        self.fr_wheel.drive(-speed)
                        self.bl_wheel.drive(-speed)
                        self.br_wheel.drive(speed)
                    elif -lower_theta > theta > -higher_theta:
                        self.fl_wheel.drive(speed - adjuster)
                        self.fr_wheel.drive(-speed - adjuster)
                        self.bl_wheel.drive(-speed + adjuster)
                        self.br_wheel.drive(speed - adjuster)
                    elif lower_theta < theta < higher_theta:
                        self.fl_wheel.drive(speed + adjuster)
                        self.fr_wheel.drive(-speed - adjuster)
                        self.bl_wheel.drive(-speed + adjuster)
                        self.br_wheel.drive(speed + adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        self.fr_wheel.drive_mfw()
                        self.br_wheel.drive_mbw()
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        self.fl_wheel.drive_mbw()
                        self.bl_wheel.drive_mbw()
                        theta = 0
                    k.msleep(t)
                    theta += (self.get_current_standard_gyro(True) - self.rev_standard_bias_gyro) * 3

                elif direction == 'left':
                    if lower_theta > theta > -lower_theta:
                        self.fl_wheel.drive(-speed)
                        self.fr_wheel.drive(speed)
                        self.bl_wheel.drive(speed)
                        self.br_wheel.drive(-speed)
                    elif -lower_theta > theta > -higher_theta:
                        self.fl_wheel.drive(-speed + adjuster)
                        self.fr_wheel.drive(speed + adjuster)
                        self.bl_wheel.drive(speed - adjuster)
                        self.br_wheel.drive(-speed + adjuster)
                    elif lower_theta < theta < higher_theta:
                        self.fl_wheel.drive(-speed - adjuster)
                        self.fr_wheel.drive(speed + adjuster)
                        self.bl_wheel.drive(speed - adjuster)
                        self.br_wheel.drive(-speed - adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        self.fr_wheel.drive_mbw()
                        self.br_wheel.drive_mfw()
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        self.fl_wheel.drive_mfw()
                        self.bl_wheel.drive_mfw()
                        theta = 0
                    k.msleep(t)
                    theta += (self.get_current_standard_gyro(True) - self.rev_standard_bias_gyro) * 3


        elif condition == 'het' or condition == '>=':  # het -> higher or equal than
            while (Instance.current_value() >= value) and (k.seconds() - startTime < (millis) / 1000) and self.is_motor_active(motor_id):
                if direction == 'right':
                    if lower_theta > theta > -lower_theta:
                        self.fl_wheel.drive(speed)
                        self.fr_wheel.drive(-speed)
                        self.bl_wheel.drive(-speed)
                        self.br_wheel.drive(speed)
                    elif -lower_theta > theta > -higher_theta:
                        self.fl_wheel.drive(speed - adjuster)
                        self.fr_wheel.drive(-speed - adjuster)
                        self.bl_wheel.drive(-speed + adjuster)
                        self.br_wheel.drive(speed - adjuster)
                    elif lower_theta < theta < higher_theta:
                        self.fl_wheel.drive(speed + adjuster)
                        self.fr_wheel.drive(-speed - adjuster)
                        self.bl_wheel.drive(-speed + adjuster)
                        self.br_wheel.drive(speed + adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        self.fr_wheel.drive_mfw()
                        self.br_wheel.drive_mbw()
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        self.fl_wheel.drive_mbw()
                        self.bl_wheel.drive_mbw()
                        theta = 0
                    k.msleep(t)
                    theta += (self.get_current_standard_gyro(True) - self.rev_standard_bias_gyro) * 3


                elif direction == 'left':
                    if lower_theta > theta > -lower_theta:
                        self.fl_wheel.drive(-speed)
                        self.fr_wheel.drive(speed)
                        self.bl_wheel.drive(speed)
                        self.br_wheel.drive(-speed)
                    elif -lower_theta > theta > -higher_theta:
                        self.fl_wheel.drive(-speed + adjuster)
                        self.fr_wheel.drive(speed + adjuster)
                        self.bl_wheel.drive(speed - adjuster)
                        self.br_wheel.drive(-speed + adjuster)
                    elif lower_theta < theta < higher_theta:
                        self.fl_wheel.drive(-speed - adjuster)
                        self.fr_wheel.drive(speed + adjuster)
                        self.bl_wheel.drive(speed - adjuster)
                        self.br_wheel.drive(-speed - adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        self.fr_wheel.drive_mbw()
                        self.br_wheel.drive_mfw()
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        self.fl_wheel.drive_mfw()
                        self.bl_wheel.drive_mfw()
                        theta = 0
                    k.msleep(t)
                    theta += (self.get_current_standard_gyro(True) - self.rev_standard_bias_gyro) * 3

        elif condition == 'ht' or condition == '>':  # ht -> higher than
            while (Instance.current_value() > value) and (k.seconds() - startTime < (millis) / 1000) and self.is_motor_active(motor_id):
                if direction == 'right':
                    if lower_theta > theta > -lower_theta:
                        self.fl_wheel.drive(speed)
                        self.fr_wheel.drive(-speed)
                        self.bl_wheel.drive(-speed)
                        self.br_wheel.drive(speed)
                    elif -lower_theta > theta > -higher_theta:
                        self.fl_wheel.drive(speed - adjuster)
                        self.fr_wheel.drive(-speed - adjuster)
                        self.bl_wheel.drive(-speed + adjuster)
                        self.br_wheel.drive(speed - adjuster)
                    elif lower_theta < theta < higher_theta:
                        self.fl_wheel.drive(speed + adjuster)
                        self.fr_wheel.drive(-speed - adjuster)
                        self.bl_wheel.drive(-speed + adjuster)
                        self.br_wheel.drive(speed + adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        self.fr_wheel.drive_mfw()
                        self.br_wheel.drive_mbw()
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        self.fl_wheel.drive_mbw()
                        self.bl_wheel.drive_mbw()
                        theta = 0
                    k.msleep(t)
                    theta += (self.get_current_standard_gyro(True) - self.rev_standard_bias_gyro) * 3


                elif direction == 'left':
                    if lower_theta > theta > -lower_theta:
                        self.fl_wheel.drive(-speed)
                        self.fr_wheel.drive(speed)
                        self.bl_wheel.drive(speed)
                        self.br_wheel.drive(-speed)
                    elif -lower_theta > theta > -higher_theta:
                        self.fl_wheel.drive(-speed + adjuster)
                        self.fr_wheel.drive(speed + adjuster)
                        self.bl_wheel.drive(speed - adjuster)
                        self.br_wheel.drive(-speed + adjuster)
                    elif lower_theta < theta < higher_theta:
                        self.fl_wheel.drive(-speed - adjuster)
                        self.fr_wheel.drive(speed + adjuster)
                        self.bl_wheel.drive(speed - adjuster)
                        self.br_wheel.drive(-speed - adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        self.fr_wheel.drive_mbw()
                        self.br_wheel.drive_mfw()
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        self.fl_wheel.drive_mfw()
                        self.bl_wheel.drive_mfw()
                        theta = 0
                    k.msleep(t)
                    theta += (self.get_current_standard_gyro(True) - self.rev_standard_bias_gyro) * 3

        elif condition == 'lt' or condition == '<':  # lt -> less than
            while (Instance.current_value() < value) and (k.seconds() - startTime < (millis) / 1000) and self.is_motor_active(motor_id):
                if lower_theta > theta > -lower_theta:
                    self.fl_wheel.drive(speed)
                    self.fr_wheel.drive(-speed)
                    self.bl_wheel.drive(-speed)
                    self.br_wheel.drive(speed)
                elif -lower_theta > theta > -higher_theta:
                    self.fl_wheel.drive(speed - adjuster)
                    self.fr_wheel.drive(-speed - adjuster)
                    self.bl_wheel.drive(-speed + adjuster)
                    self.br_wheel.drive(speed - adjuster)
                elif lower_theta < theta < higher_theta:
                    self.fl_wheel.drive(speed + adjuster)
                    self.fr_wheel.drive(-speed - adjuster)
                    self.bl_wheel.drive(-speed + adjuster)
                    self.br_wheel.drive(speed + adjuster)
                elif theta < -higher_theta:
                    k.ao()
                    self.fr_wheel.drive_mfw()
                    self.br_wheel.drive_mbw()
                    theta = 0
                elif theta > higher_theta:
                    k.ao()
                    self.fl_wheel.drive_mbw()
                    self.bl_wheel.drive_mbw()
                    theta = 0
                    k.msleep(t)
                    theta += (self.get_current_standard_gyro(True) - self.rev_standard_bias_gyro) * 3


                elif direction == 'left':
                    if lower_theta > theta > -lower_theta:
                        self.fl_wheel.drive(-speed)
                        self.fr_wheel.drive(speed)
                        self.bl_wheel.drive(speed)
                        self.br_wheel.drive(-speed)
                    elif -lower_theta > theta > -higher_theta:
                        self.fl_wheel.drive(-speed + adjuster)
                        self.fr_wheel.drive(speed + adjuster)
                        self.bl_wheel.drive(speed - adjuster)
                        self.br_wheel.drive(-speed + adjuster)
                    elif lower_theta < theta < higher_theta:
                        self.fl_wheel.drive(-speed - adjuster)
                        self.fr_wheel.drive(speed + adjuster)
                        self.bl_wheel.drive(speed - adjuster)
                        self.br_wheel.drive(-speed - adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        self.fr_wheel.drive_mbw()
                        self.br_wheel.drive_mfw()
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        self.fl_wheel.drive_mfw()
                        self.bl_wheel.drive_mfw()
                        theta = 0
                    k.msleep(t)
                    theta += (self.get_current_standard_gyro(True) - self.rev_standard_bias_gyro) * 3
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def drive_straight_condition_analog(self, Instance, condition: str, value: int, millis: int = 9999999, speed: int = None) -> None:
        '''
       drive straight until an analog value gets reached for the desired instance

       Args:
           Instance: just has to be from something analog (since there is (as of time of creation) only light and distance sensors, which are valid for this argument, just those should be used.
           condition (str): ("let" / "<=") or ("get" / ">=") or ("ht" / ">") or ("lt" / "<") are valid. Notice: l -> less | h -> higher | e -> equal | t -> than. (The parentheses should be left out, as well as the slash, only choose one argument Example: ">=")
           value (int): The value that the current value gets compared to and has to be reached
           millis (int, optional): The maximum amount of time (in milliseconds) which can be taken (default: 9999999)
           speed (int, optional): The speed it drives sideways (default: ds_speed)

       Returns:
           None
       '''
        if speed is None:
            speed = self.ds_speed
        self.check_instances_buttons()
        motor_id = self._manage_motor_stopper(True)
        theta = 0.0
        ports = self.button_fl, self.button_fr
        startTime = k.seconds()
        adjuster = 100
        if speed < 0:
            ports = self.button_bl, self.button_br

        if condition == 'let' or condition == '<=':  # let -> less or equal than
            while (Instance.current_value() <= value) and (not ports[0].is_pressed() and not ports[
                1].is_pressed()) and k.seconds() - startTime < millis / 1000 and self.is_motor_active(motor_id):
                if 1000 > theta > -1000:
                    self.fl_wheel.drive(speed)
                    self.fr_wheel.drive(speed)
                    self.bl_wheel.drive(speed)
                    self.br_wheel.drive(speed)
                elif theta > 1000:
                    self.fl_wheel.drive(speed - adjuster)
                    self.fr_wheel.drive(speed + adjuster)
                    self.bl_wheel.drive(speed - adjuster)
                    self.br_wheel.drive(speed + adjuster)
                else:
                    self.fl_wheel.drive(speed + adjuster)
                    self.fr_wheel.drive(speed - adjuster)
                    self.bl_wheel.drive(speed + adjuster)
                    self.br_wheel.drive(speed - adjuster)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 1.5

        elif condition == 'het' or condition == '>=':  # het -> higher or equal than
            while (Instance.current_value() >= value) and (not ports[0].is_pressed() and not ports[
                1].is_pressed()) and k.seconds() - startTime < millis / 1000 and self.is_motor_active(motor_id):
                print('condition ', self.is_motor_active(motor_id), flush=True)  #@TODO needs to be tested
                if 1000 > theta > -1000:
                    self.fl_wheel.drive(speed)
                    self.fr_wheel.drive(speed)
                    self.bl_wheel.drive(speed)
                    self.br_wheel.drive(speed)
                elif theta > 1000:
                    self.fl_wheel.drive(speed - adjuster)
                    self.fr_wheel.drive(speed + adjuster)
                    self.bl_wheel.drive(speed - adjuster)
                    self.br_wheel.drive(speed + adjuster)
                else:
                    self.fl_wheel.drive(speed + adjuster)
                    self.fr_wheel.drive(speed - adjuster)
                    self.bl_wheel.drive(speed + adjuster)
                    self.br_wheel.drive(speed - adjuster)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 1.5

        elif condition == 'ht' or condition == '>':  # ht -> higher than
            while (Instance.current_value() > value) and (not ports[0].is_pressed() and not ports[
                1].is_pressed() and k.seconds()) - startTime < millis / 1000 and self.is_motor_active(motor_id):
                if 1000 > theta > -1000:
                    self.fl_wheel.drive(speed)
                    self.fr_wheel.drive(speed)
                    self.bl_wheel.drive(speed)
                    self.br_wheel.drive(speed)
                elif theta > 1000:
                    self.fl_wheel.drive(speed - adjuster)
                    self.fr_wheel.drive(speed + adjuster)
                    self.bl_wheel.drive(speed - adjuster)
                    self.br_wheel.drive(speed + adjuster)
                else:
                    self.fl_wheel.drive(speed + adjuster)
                    self.fr_wheel.drive(speed - adjuster)
                    self.bl_wheel.drive(speed + adjuster)
                    self.br_wheel.drive(speed - adjuster)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 1.5

        elif condition == 'lt' or condition == '<':  # lt -> less than
            while (Instance.current_value() < value) and (not ports[0].is_pressed() and not ports[
                1].is_pressed()) and k.seconds() - startTime < millis / 1000 and self.is_motor_active(motor_id):
                if 1000 > theta > -1000:
                    self.fl_wheel.drive(speed)
                    self.fr_wheel.drive(speed)
                    self.bl_wheel.drive(speed)
                    self.br_wheel.drive(speed)
                elif theta > 1000:
                    self.fl_wheel.drive(speed - adjuster)
                    self.fr_wheel.drive(speed + adjuster)
                    self.bl_wheel.drive(speed - adjuster)
                    self.br_wheel.drive(speed + adjuster)
                else:
                    self.fl_wheel.drive(speed + adjuster)
                    self.fr_wheel.drive(speed - adjuster)
                    self.bl_wheel.drive(speed + adjuster)
                    self.br_wheel.drive(speed - adjuster)
                k.msleep(10)
                theta += (self.get_current_standard_gyro() - self.standard_bias_gyro) * 1.5

        self.break_all_motors()
        self._manage_motor_stopper(False)

    def align_on_black_line(self, crossing: bool, direction: str = 'vertical', leaning_side: str = None,
                            precise: bool = False) -> None:
        # hint: do not face the black line (?)
        '''
       Align yourself on the black line. If there is a crossing you can choose on which line you want to get onto by switching the direction parameter. You need to be somewhere on top of the black line to let this function work!

       Args:
           crossing (bool): are there two overlapping black lines (True) or not (False)
           direction (str, optional): "vertical" (default) or "horizontal" - depends on where you want to go
           leaning_side (str, optional): "left" or "right" - helps the roboter to turn in the right direction (-> faster)
           precise (bool, optional): if True, then it takes longer, but is slightly better aligned on the black line. If False, it takes less time but the bias is therefor more forgiving

       Returns:
           None
       '''
        self.check_instance_light_sensors_middle()
        motor_id = self._manage_motor_stopper(True)
        try:
            if direction != 'vertical' and direction != 'horizontal':
                log('Only "vertical" or "horizontal" are valid options for the "direction" parameter',
                    in_exception=True)
                raise ValueError(
                    'align_on_black_line() Exception: Only "vertical" or "horizontal" are valid options for the "direction" parameter')

            if leaning_side != None and leaning_side != 'right' and leaning_side != 'left':
                log('Only "right", "left" or None / nothing are valid options for the "leaning_side" parameter',
                    in_exception=True)
                raise ValueError(
                    'align_on_black_line() Exception: Only "right", "left" or None / nothing are valid options for the "leaning_side" parameter')

            if not crossing:
                if not leaning_side or leaning_side == 'right':
                    instances = self.fl_wheel, self.fr_wheel, self.bl_wheel, self.br_wheel
                else:
                    instances = self.fr_wheel, self.fl_wheel, self.br_wheel, self.bl_wheel
                adjuster = self.ds_speed
                if precise:
                    adjuster = self.ds_speed
                startTime = k.seconds()

                while self.light_sensor_back.sees_white() and self.light_sensor_front.sees_white() and self.is_motor_active(motor_id):
                    if k.seconds() - startTime < self.NINETY_DEGREES_SECS:
                        instances[0].drive_dfw()
                        instances[1].drive_dbw()
                        instances[2].drive_dfw()
                        instances[3].drive_dbw()
                    else:
                        instances[0].drive_dbw()
                        instances[1].drive_dfw()
                        instances[2].drive_dbw()

                self.break_all_motors()

                if not self.light_sensor_back.sees_white():  # hinten ist oben
                    while self.light_sensor_front.sees_white() and self.is_motor_active(motor_id):
                        instances[0].drive(-adjuster)
                        instances[1].drive(adjuster)

                if not self.light_sensor_front.sees_white():  # vorne ist oben
                    while self.light_sensor_back.sees_white() and self.is_motor_active(motor_id):
                        instances[2].drive(-adjuster)
                        instances[3].drive(adjuster)

                k.ao()
                k.msleep(50)
                if self.light_sensor_front.sees_white():
                    while self.light_sensor_front.sees_white() and self.is_motor_active(motor_id):
                        instances[0].drive(-adjuster)
                        instances[1].drive(adjuster)

                k.ao()
                k.msleep(10)
                if not self.light_sensor_back.sees_black() and not self.light_sensor_front.sees_black():
                    self.drive_side_condition_analog('left', self.light_sensor_front, '<', self.light_sensor_front.get_value_black() - self.light_sensor_front.get_bias())

            else:
                instances = self.fl_wheel, self.fr_wheel, self.bl_wheel, self.br_wheel
                on_line = False
                first_line_hit = None
                line_counter = 0
                line_timer = 0
                line_timer_collector = []

                startTime_front = k.seconds()
                while k.seconds() - startTime_front < self.ONEEIGHTY_DEGREES_SECS * 2 + 0.2 and self.is_motor_active(motor_id):  # +0.2 is just a bias
                    while self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                        on_line = True
                        line_timer += 1
                        instances[0].drive_dbw()
                        instances[1].drive_dfw()
                        instances[2].drive_dbw()
                        instances[3].drive_dfw()
                    if on_line:
                        if not first_line_hit:
                            first_line_hit = k.seconds() - startTime_front
                        on_line = False
                        line_counter += 1
                        line_timer_collector.append(line_timer)
                        line_timer = 0
                    instances[0].drive_dbw()
                    instances[1].drive_dfw()
                    instances[2].drive_dbw()
                    instances[3].drive_dfw()

                if line_counter > 4:
                    line_counter = 4
                on_line = False
                direct = 'right', 'left'
                dir_picker = self.NINETY_DEGREES_SECS / 1.4, first_line_hit
                if direction == 'horizontal':
                    dir_picker = dir_picker[1], dir_picker[0]

                if line_counter == 1 and line_timer_collector[0] < 400:  # There is no crossing, just the normal line
                    self.align_on_black_line(False, direction=direction, leaning_side=leaning_side)
                    return

                if line_counter == 2 and line_timer_collector[0] < 400 and line_timer_collector[
                    1] < 400:  # There is no crossing, just the normal line
                    self.align_on_black_line(False, direction=direction, leaning_side=leaning_side)
                    return

                if line_counter == 4:
                    if dir_picker[0] < dir_picker[1]:
                        d = direct[0]
                        while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                            instances[0].drive_dfw()
                            instances[1].drive_dbw()
                            instances[2].drive_dfw()
                            instances[3].drive_dbw()
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_black() and self.is_motor_active(motor_id):
                            instances[0].drive_dfw()
                            instances[1].drive_dfw()
                            instances[2].drive_dbw()
                            instances[3].drive_dfw()
                        while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                            instances[0].drive_dfw()
                            instances[1].drive_dbw()
                        self.break_all_motors()
                    else:
                        d = direct[1]
                        while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                            instances[0].drive_dbw()
                            instances[1].drive_dfw()
                            instances[2].drive_dbw()
                            instances[3].drive_dfw()
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_black() and self.is_motor_active(motor_id):
                            instances[0].drive_dfw()
                            instances[1].drive_dfw()
                            instances[2].drive_dfw()
                            instances[3].drive_dbw()
                        self.break_all_motors()
                        while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                            instances[0].drive_dbw()
                            instances[1].drive_dfw()
                        self.break_all_motors()
                    self.drive_side(d, 5)

                elif line_counter == 3:
                    if dir_picker[0] > dir_picker[1]:
                        d = direct[0]
                        while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                            instances[0].drive_dfw()
                            instances[1].drive_dbw()
                            instances[2].drive_dfw()
                            instances[3].drive_dbw()
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_black() and self.is_motor_active(motor_id):
                            instances[0].drive_dfw()
                            instances[1].drive_dfw()
                            instances[2].drive_dbw()
                            instances[3].drive_dfw()
                        self.break_all_motors()
                        if not self.light_sensor_front.sees_black():
                            while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                                instances[0].drive_dbw()
                                instances[1].drive_dfw()
                            self.break_all_motors()
                    else:
                        d = direct[1]
                        while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                            instances[0].drive_dbw()
                            instances[1].drive_dfw()
                            instances[2].drive_dbw()
                            instances[3].drive_dfw()
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_black() and self.is_motor_active(motor_id):
                            instances[0].drive_dfw()
                            instances[1].drive_dfw()
                            instances[2].drive_dfw()
                            instances[3].drive_dbw()
                        self.break_all_motors()
                        if not self.light_sensor_front.sees_black():
                            while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                                instances[0].drive_dbw()
                                instances[1].drive_dfw()
                            self.break_all_motors()
                    self.drive_side(d, 5)

                else:  # line_counter == 2
                    if dir_picker[0] < dir_picker[1]:
                        d = direct[0]
                        while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                            instances[0].drive_dfw()
                            instances[1].drive_dbw()
                            instances[2].drive_dfw()
                            instances[3].drive_dbw()
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_black() and self.is_motor_active(motor_id):
                            instances[0].drive_dfw()
                            instances[1].drive_dfw()
                            instances[2].drive_dbw()
                            instances[3].drive_dfw()
                        self.break_all_motors()
                    else:
                        d = direct[1]
                        while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                            instances[0].drive_dbw()
                            instances[1].drive_dfw()
                            instances[2].drive_dbw()
                            instances[3].drive_dfw()
                        self.break_all_motors()
                    self.drive_side(d, 5)
        except Exception as e:
            log(str(e), important=True, in_exception=True)
        self._manage_motor_stopper(False)

    def turn_to_black_line(self, direction: str, millis: int = 80, speed: int = None) -> None:
        '''
        Turn as long as the light sensor (front or back, depends if the speed is positive or negative) sees the black line

        Args:
           direction (str): "right" or "left" - depends on where you want to go
           millis (int, optional): how long (in milliseconds) it should keep turning after finding the black line (default: 80)
           speed (int, optional): which direction it has to drive (forward = positive or backward = negative) (default: ds_speed)

        Returns:
           None
        '''
        if speed is None:
            speed = self.ds_speed
        self.check_instance_light_sensors_middle()
        motor_id = self._manage_motor_stopper(True)
        instances = self.fl_wheel, self.fr_wheel, self.bl_wheel, self.br_wheel, self.light_sensor_front
        if speed < 0:
            instances = self.bl_wheel, self.br_wheel, self.fl_wheel, self.fr_wheel, self.light_sensor_back

        if direction == 'right':
            while not instances[4].sees_black() and self.is_motor_active(motor_id):
                instances[0].drive_mfw()
                instances[1].drive_mbw()
                instances[2].drive_mfw()
                instances[3].drive_mbw()
                k.msleep(millis)
        elif direction == 'left':
            while not instances[4].sees_black() and self.is_motor_active(motor_id):
                instances[0].drive_mbw()
                instances[1].drive_mfw()
                instances[2].drive_mbw()
                instances[3].drive_mfw()
                k.msleep(millis)
        else:
            log('Only "right" and "left" are valid commands for the direction!', in_exception=True)
            raise ValueError(
                'turn_black_line() Exception: Only "right" and "left" are valid commands for the direction!')
        self.break_all_motors()
        self._manage_motor_stopper(False)

    def align_line(self, onLine: bool, direction: str = None, speed: int = None, maxDuration: int = 100) -> None:
        '''
         If you are anywhere on the black line, you can align yourself on the black line. If you are not on the line, it drives (forwards or backwards, depends if the speed is positive or negative) until the line was found and then aligns as desired.
         Improvement: align backwards, so there is no need to make a 180 degrees turn. Would spare you some time.

        Args:
           onLine (bool): Are you already on the black line (True), or do you need to get onto it (False)? If you are not on the line, you need to write the direction you want to face to!
           direction (str): "right" or "left" - depends on where you want to go (only needed, if onLine is False)
           speed (int, optional): how fast it should drive (default: ds_speed)
           maxDuration  (int, optional): the time (in milliseconds) it is allowed to turn in one direction until a failsave gets executed to turn to the other direction (default: 100)

        Returns:
           None
        '''
        if speed is None:
            speed = self.ds_speed
        self.check_instances_buttons()
        self.check_instance_light_sensors_middle()
        motor_id = self._manage_motor_stopper(True)
        if not onLine:
            if direction != 'left' and direction != 'right':
                log('If the Wombat is not on the line, please tell it which direction it should face when it is on the line ("right" or "left")',
                    in_exception=True, important=True)
                raise ValueError(
                    'align_line() Exception: If the Wombat is not on the line, please tell it which direction it should face when it is on the line ("right" or "left")')

            ports = self.light_sensor_front, self.light_sensor_back
            if speed < 0:
                ports = self.light_sensor_back, self.light_sensor_front

            self.drive_straight_condition_analog(ports[0], '<=', ports[0].get_value_black() - ports[0].get_bias(), speed=speed)
            start_time = k.seconds()
            self.drive_straight_condition_analog(ports[1], '<=', ports[1].get_value_black() - ports[1].get_bias(), speed=speed)

            seconds = k.seconds() - start_time
            self.drive_straight((seconds * 1000) // 2, -speed)
            self.turn_to_black_line(direction, speed=abs(speed))
            self.turn_degrees(direction, 10)  # this is just so it is a little bit better aligned on the line
        else:
            startTime = k.seconds()
            instances = self.fl_wheel, self.fr_wheel, self.bl_wheel, self.br_wheel, self.button_fl, self.button_fr, self.light_sensor_front
            direction = 'right', 'left'
            if speed < 0:
                instances = self.bl_wheel, self.br_wheel, self.fl_wheel, self.fr_wheel, self.button_bl, self.button_br, self.light_sensor_back
                direction = 'left', 'right'

            while self.is_motor_active(motor_id):
                instances[0].drive(speed)
                instances[1].drive(-speed)
                instances[2].drive(speed)
                instances[3].drive(-speed)
                if k.seconds() - startTime > maxDuration / 1000:
                    self.turn_to_black_line(direction[1], millis=20, speed=speed)
                    break
                if instances[6].sees_black():
                    k.ao()
                    self.turn_to_black_line(direction[0], millis=20, speed=speed)
                    break
                if instances[4].is_pressed() or instances[5].is_pressed():
                    if speed < 0:
                        self.align_drive_back()
                    else:
                        self.align_drive_front()
                    break
            self.break_all_motors()
            self._manage_motor_stopper(False)

    def black_line(self, millis: int, speed: int = None) -> None:
        '''
       drive on the black line as long as wished

       Args:
           millis (int): how long you want to follow the black line (in milliseconds)
           speed (int, optional): how fast it should drive straight (default: ds_speed)

       Returns:
           None
       '''
        if speed is None:
            speed = self.ds_speed
        self.check_instances_buttons()
        self.check_instance_light_sensors_middle()
        motor_id = self._manage_motor_stopper(True)
        startTime: float = k.seconds()
        ports = self.button_fl, self.button_fr, self.light_sensor_front
        if speed < 0:
            ports = self.button_bl, self.button_br, self.light_sensor_back
        while (k.seconds() - startTime < millis / 1000) and (not ports[0].is_pressed() and not ports[1].is_pressed()) and self.is_motor_active(motor_id):
            self.drive_straight_condition_analog(ports[2], '>=', ports[2].get_value_black() - ports[2].get_bias(), speed=speed, millis=100)
            if ports[2].current_value() < ports[2].get_value_black() - ports[2].get_bias():
                self.align_line(True, speed=-speed, maxDuration=100)

        if ports[0].is_pressed() or ports[1].is_pressed():
            if speed < 0:
                self.align_drive_back()
            else:
                self.align_drive_front()
        self._manage_motor_stopper(False)

    def scanner_face_object(self, degree: int) -> None:
        '''
       Scan the location for the nearest object and then face the nearest object

       Args:
           degree (int): how much area the scan should cover

       Returns:
           None
       '''
        self.check_instance_distance_sensor()
        if degree > 90:
            log('Only a value under 91 is acceptable for the degree!', in_exception=True)
            raise ValueError('scan_front() Exception: Only a value under 91 is acceptable for the degree')
        motor_id = self._manage_motor_stopper(True)
        maxRuns = 2
        div = 90 / degree
        amount = degree
        value = self.NINETY_DEGREES_SECS / div
        instances = self.fl_wheel, self.fr_wheel, self.bl_wheel, self.br_wheel
        distance_saver = [None] * amount
        portion = (value * 2) / amount

        def build_avrg(index: int, value: int) -> None:
            if not distance_saver[index]:
                distance_saver[index] = value
            else:
                distance_saver[index] = (distance_saver[index] + value) / 2

        def slicer():
            startTime = k.seconds()
            i = 0
            while i < amount and self.is_motor_active(motor_id):
                newTime = k.seconds()
                avrg = 0
                while k.seconds() - newTime < portion and self.is_motor_active(motor_id):
                    avrg += self.distance_sensor.current_value()
                build_avrg(i, (avrg * portion) / amount)
                i += 1

        def adjust():
            inst = instances[1], instances[0], instances[3], instances[2]
            index = distance_saver.index(max(distance_saver))
            newTime = k.seconds()
            while k.seconds() - newTime < portion * (amount - index) and self.is_motor_active(motor_id):
                inst[0].drive_mfw()
                inst[1].drive_mbw()
                inst[2].drive_mfw()
                inst[3].drive_mbw()

            self.break_all_motors()

        for i in range(1, maxRuns + 1):
            if self.is_motor_active(motor_id):
                if i == 2:
                    th1 = threading.Thread(target=slicer)
                    th1.start()
                    value = value * 2
                instances[0].drive_mfw()
                instances[1].drive_mbw()
                instances[2].drive_mfw()
                instances[3].drive_mbw()
                time.sleep(value)
                if i % 2 != 0:
                    instances = instances[1], instances[0], instances[3], instances[2]
            else:
                break
        self.break_all_motors()
        while th1.is_alive() and self.is_motor_active(motor_id):
            continue
        adjust()
        self._manage_motor_stopper(False)