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
    from scipy.interpolate import interp1d
    from util import Util  # selfmade
    from distance_sensor import DistanceSensor  # selfmade
    from light_sensor import LightSensor  # selfmade
    from digital import Digital  # selfmade
    from fileR import FileR  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

try:
    file_Manager = FileR()
except Exception as e:
    log(f'FileR Error: {str(e)}', important=True, in_exception=True)


# bias_gyro_z.txt file -> should work
# bias_gyro_y.txt file -> should work
# bias_accel_x.txt file -> should work
# bias_accel_y.txt file -> should work

class driveR_two:
    def __init__(self,
                 Port_right_wheel: int,
                 Port_left_wheel: int,
                 DS_SPEED: int = 2600,
                 Instance_button_front_right: Digital = None,
                 Instance_button_front_left: Digital = None,
                 Instance_button_back_right: Digital = None,
                 Instance_button_back_left: Digital = None,
                 Instance_light_sensor_front: LightSensor = None,
                 Instance_light_sensor_back: LightSensor = None,
                 Instance_light_sensor_side: LightSensor = None,
                 Instance_distance_sensor: DistanceSensor = None):

        self.port_wheel_left = Port_left_wheel
        self.port_wheel_right = Port_right_wheel

        self.button_fr = Instance_button_front_right
        self.button_fl = Instance_button_front_left
        self.button_br = Instance_button_back_right
        self.button_bl = Instance_button_back_left

        self.light_sensor_front = Instance_light_sensor_front
        self.light_sensor_back = Instance_light_sensor_back
        self.light_sensor_side = Instance_light_sensor_side

        self.distance_sensor = Instance_distance_sensor

        self.ds_speed = self.ds_speed
        self.bias_gyro_z = None  # self.get_bias_gyro_z()
        self.bias_gyro_y = None  # self.get_bias_gyro_y()
        self.bias_accel_x = None  # There are no function where you can do anything with the accel x -> you need to invent them by yourself  
        self.bias_accel_y = None  # There are no function where you can do anything with the accel y -> you need to invent them by yourself
        self.isClose = False
        self.ONEEIGHTY_DEGREES_SECS = None
        self.NINETY_DEGREES_SECS = None


        # ======================== SET INSTANCES ========================

        def set_instance_distance_sensor(self, Instance_distance_sensor: DistanceSensor) -> None:
            '''
            create or overwrite the existance of the distance_sensor

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
            create or overwrite the existance of all light sensors

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
            create or overwrite the existance of the front light sensors

            Args:
                Instance_light_sensor_front (LightSensor): the instance of the front light sensor

           Returns:
                None
            '''
            self.light_sensor_front = Instance_light_sensor_front

        def set_instance_light_sensor_back(self, Instance_light_sensor_back: LightSensor) -> None:
            '''
            create or overwrite the existance of the back light sensor

            Args:
                Instance_light_sensor_back (LightSensor): the instance of the back light sensor

           Returns:
                None
            '''
            self.light_sensor_back = Instance_light_sensor_back

        def set_instance_light_sensor_side(self, Instance_light_sensor_side: LightSensor) -> None:
            '''
            create or overwrite the existance of the side light sensor

            Args:
                Instance_light_sensor_side (LightSensor):  the instance of the side light sensor

           Returns:
                None
            '''
            self.light_sensor_side = Instance_light_sensor_side

        def set_instances_buttons(self, Instance_button_front_right: Digital, Instance_button_front_left: Digital,
                                  Instance_button_back_right: Digital, Instance_button_back_left: Digital) -> None:
            '''
            create or overwrite the existance of all buttons

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
            create or overwrite the existance of the front left button

            Args:
                Instance_button_front_left (Digital): the instance of the front left button

           Returns:
                None
            '''
            self.button_fl = Instance_button_front_left

        def set_instance_button_fr(self, Instance_button_front_right: Digital) -> None:
            '''
            create or overwrite the existance of the front right button

            Args:
                Instance_button_front_right (Digital): the instance of the front right button

           Returns:
                None
            '''
            self.button_fr = Instance_button_front_right

        def set_instance_button_bl(self, Instance_button_back_left: Digital) -> None:
            '''
            create or overwrite the existance of the back left button

            Args:
                Instance_button_back_left (Digital):  the instance of the back left button

           Returns:
                None
            '''
            self.button_bl = Instance_button_back_left

        def set_instance_button_br(self, Instance_button_back_right: Digital) -> None:
            '''
            create or overwrite the existance of the back right button

            Args:
                Instance_button_back_right (Digital):  the instance of the back right button

           Returns:
                None
            '''
            self.button_br = Instance_button_back_right


        # ======================== CHECK INSTANCES ========================

        def check_instance_light_sensors(self) -> bool:
            '''
            inspect the existance of all light sensors

            Args:
                None

           Returns:
                if there is an instance of all light sensor in existance
            '''
            if not isinstance(self.light_sensor_front, LightSensor):
                log('Light sensor front is not initialized!', in_exception=True)
                raise Exception('Light sensor front is not initialized!')

            if not isinstance(self.light_sensor_back, LightSensor):
                log('Light sensor back is not initialized!', in_exception=True)
                raise Exception('Light sensor back is not initialized!')

            if not isinstance(self.light_sensor_side, LightSensor):
                log('Light sensor side is not initialized!', in_exception=True)
                raise Exception('Light sensor side is not initialized!')
            return True

        def check_instance_light_sensors_middle(self) -> bool:
            '''
            inspect the existance of the middle light sensors

            Args:
                None

           Returns:
                if there is an instance of the middle light sensors in existance
            '''
            if not isinstance(self.light_sensor_front, LightSensor):
                log('Light sensor front is not initialized!', in_exception=True)
                raise Exception('Light sensor front is not initialized!')

            if not isinstance(self.light_sensor_back, LightSensor):
                log('Light sensor back is not initialized!', in_exception=True)
                raise Exception('Light sensor back is not initialized!')
            return True

        def check_instance_light_sensor_front(self) -> bool:
            '''
            inspect the existance of the front light sensor

            Args:
                None

           Returns:
                if there is an instance of the front light sensor in existance
            '''
            if not isinstance(self.light_sensor_front, LightSensor):
                log('Light sensor front is not initialized!', in_exception=True)
                raise Exception('Light sensor front is not initialized!')
            return True

        def check_instance_light_sensor_back(self) -> bool:
            '''
            inspect the existance of the back light sensor

            Args:
                None

           Returns:
                if there is an instance of the back light sensor in existance
            '''
            if not isinstance(self.light_sensor_back, LightSensor):
                log('Light sensor back is not initialized!', in_exception=True)
                raise Exception('Light sensor back is not initialized!')
            return True

        def check_instance_light_sensor_side(self) -> bool:
            '''
            inspect the existance of the side light sensor

            Args:
                None

           Returns:
                if there is an instance of the side light sensor in existance
            '''
            if not isinstance(self.light_sensor_side, LightSensor):
                log('Light sensor side is not initialized!', in_exception=True)
                raise Exception('Light sensor side is not initialized!')
            return True

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
                raise Exception('Distance sensor is not initialized!')
            return True

        def check_instance_button_fl(self) -> bool:
            '''
            inspect the existance of the front left button

            Args:
                None

           Returns:
                if there is an instance of the front left button in existance
            '''
            if not isinstance(self.button_fl, Digital):
                log('Button front left is not initialized!', in_exception=True)
                raise Exception('Button front left is not initialized!')
            return True

        def check_instance_button_fr(self) -> bool:
            '''
            inspect the existance of the front right button

            Args:
                None

           Returns:
                if there is an instance of the front right button in existance
            '''
            if not isinstance(self.button_fr, Digital):
                log('Button front right is not initialized!', in_exception=True)
                raise Exception('Button front right is not initialized!')
            return True

        def check_instance_button_bl(self) -> bool:
            '''
            inspect the existance of the back left button

            Args:
                None

           Returns:
                if there is an instance of the back left button in existance
            '''
            if not isinstance(self.button_bl, Digital):
                log('Button back left is not initialized!', in_exception=True)
                raise Exception('Button back left is not initialized!')
            return True

        def check_instance_button_br(self) -> bool:
            '''
            inspect the existance of the back right button

            Args:
                None

           Returns:
                if there is an instance of the back right button in existance
            '''
            if not isinstance(self.button_br, Digital):
                log('Button back right is not initialized!', in_exception=True)
                raise Exception('Button back right is not initialized!')
            return True

        def check_instances_buttons_front(self) -> bool:
            '''
            inspect the existance of the front buttons

            Args:
                None

           Returns:
                if there is an instance of the front buttons in existance
            '''
            if not isinstance(self.button_fl, Digital):
                log('Button front left is not initialized!', in_exception=True)
                raise Exception('Button front left is not initialized!')

            if not isinstance(self.button_fr, Digital):
                log('Button front right is not initialized!', in_exception=True)
                raise Exception('Button front right is not initialized!')

            return True

        def check_instances_buttons_back(self) -> bool:
            '''
            inspect the existance of the back buttons

            Args:
                None

           Returns:
                if there is an instance of the back buttons in existance
            '''
            if not isinstance(self.button_bl, Digital):
                log('Button back left is not initialized!', in_exception=True)
                raise Exception('Button back left is not initialized!')

            if not isinstance(self.button_br, Digital):
                log('Button back right is not initialized!', in_exception=True)
                raise Exception('Button back right is not initialized!')

            return True

        def check_instances_buttons(self) -> bool:
            '''
            inspect the existance of all buttons

            Args:
                None

           Returns:
                if there is an instance of all buttons in existance
            '''
            if not isinstance(self.button_fl, Digital):
                log('Button front left is not initialized!', in_exception=True)
                raise Exception('Button front left is not initialized!')

            if not isinstance(self.button_fr, Digital):
                log('Button front right is not initialized!', in_exception=True)
                raise Exception('Button front right is not initialized!')

            if not isinstance(self.button_bl, Digital):
                log('Button back left is not initialized!', in_exception=True)
                raise Exception('Button back left is not initialized!')

            if not isinstance(self.button_br, Digital):
                log('Button back right is not initialized!', in_exception=True)
                raise Exception('Button back right is not initialized!')

            return True

    # ===================== CALIBRATE BIAS =====================

    def calibrate_gyro_z(self, counter: int, max: int) -> None:
        '''
        calibrates the bias from the gyro to be able to drive straight, since the bias is for telling us how far off from driving straight the wombat is

        Args:
            counter (int): the number where it is at the moment
            max (int): how many caLibrations there are (to show it on the screen and for debugging usage)

        Returns:
            None
        '''
        i: int = 0
        avg: float = 0
        time: int = 8000
        while i < time:
            avg += k.gyro_z()
            k.msleep(1)
            i += 1
        self.bias_gyro_z = avg / time
        log(f'{counter}/{max} - GYRO Z CALIBRATED')

    def calibrate_gyro_y(self, counter: int, max: int) -> None:
        '''
        calibrates the bias from the gyro to be able to drive straight, since the bias is for telling us how far off from driving straight the wombat is (theoretically it is for driving sideways)

        Args:
            counter (int): the number where it is at the moment
            max (int): how many caLibrations there are (to show it on the screen and for debugging usage)

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
        log(f'{counter}/{max} - GYRO Y CALIBRATED')

    def calibrate_accel_x(self, counter: int, max: int) -> None:
        '''
        calibrates the bias from the accelerometer to know how fast the wombat is going towards the x-axis(accelerometer is not yet in use though)

        Args:
            counter (int): the number where it is at the moment
            max (int): how many caLibrations there are (to show it on the screen and for debugging usage)

        Returns:
            None
        '''
        i: int = 0
        avg: float = 0
        time: int = 8000
        while i < time:
            avg += k.accel_x()
            k.msleep(1)
            i += 1
        self.bias_accel_x = avg / time
        log(f'{counter}/{max} - ACCEL X CALIBRATED')

    def calibrate_accel_y(self, counter: int, max: int) -> None:
        '''
        calibrates the bias from the accelerometer to know how fast the wombat is going towards the y-axis(accelerometer is not yet in use though)

        Args:
            counter (int): the number where it is at the moment
            max (int): how many caLibrations there are (to show it on the screen and for debugging usage)

        Returns:
            None
        '''
        i: int = 0
        avg: float = 0
        time: int = 8000
        while i < time:
            avg += k.accel_y()
            k.msleep(1)
            i += 1
        self.bias_accel_y = avg / time
        log(f'{counter}/{max} - ACCEL Y CALIBRATED')

    def calibrate_degrees(self) -> None:
        '''
        ==== NEEDS IMPROVEMENT ====
        The wombat has to be aligned on the black line. Afterwards it turns 180 degrees to see how long it takes for a full 180 degrees turn
        Improvement: Drives straight and after it recognises a black line it turns right (or left) to be aligned with the line. Afterwards doing a full 180 degrees turn to know how long it takes for a 180B0 turn

        Args:
            None

       Returns:
            None (but sets a class variable)
        '''
        self.check_instance_light_sensors_middle()
        startTime = k.seconds()
        while k.seconds() - startTime < (1200) / 1000:
            k.mav(self.port_wheel_left, self.ds_speed // 3)
            k.mav(self.port_wheel_right, -self.ds_speed // 3)
        while not self.light_sensor_front.sees_Black():
            k.mav(self.port_wheel_left, self.ds_speed // 3)
            k.mav(self.port_wheel_right, -self.ds_speed // 3)
        while not self.light_sensor_back.sees_Black():
            k.mav(self.port_wheel_left, self.ds_speed // 3)
            k.mav(self.port_wheel_right, -self.ds_speed // 3)
        self.break_all_motors()
        endTime = k.seconds()
        self.ONEEIGHTY_DEGREES_SECS = (endTime - startTime) / 1.5
        self.NINETY_DEGREES_SECS = self.ONEEIGHTY_DEGREES_SECS / 2
        log('DEGREES CALIBRATED')

    # ================== GET / OVERWRITE BIAS ==================

    def get_bias_gyro_z(self, calibrated: bool = False) -> float:
        '''
        Getting the average bias from the bias_gyro_z.txt file

        Args:
            calibrated (bool, optional): Writing to the file bias_gyro_z.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            Average of the bias_gyro_z.txt file (optionally with the recent calibrated bias as well)
        '''
        avg = 0
        file_name = 'bias_gyro_z.txt'
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
        file_name = 'bias_gyro_y.txt'
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

    def get_bias_accel_x(self, calibrated: bool = False) -> float:
        '''
        Getting the average bias from the bias_accel_x.txt file

        Args:
            calibrated (bool, optional): Writing to the file bias_accel_x.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            Average of the bias_accel_x.txt file (optionally with the recent calibrated bias as well)
        '''
        avg = 0
        file_name = 'bias_accel_x.txt'
        try:
            with open(file_name, "r") as f:
                temp_bias = f.read()
                if calibrated:
                    avg = (float(temp_bias) + self.bias_accel_x) / 2
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
        file_name = 'bias_accel_y.txt'
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

    # ======================== PUBLIC METHODS =======================

    def break_motor(self, *args) -> None:
        '''
        immediately stop the motor(s) of the given port

        Args:
            *args (int): All of the desired (motor) ports which should be stopped

        Returns:
            None
        '''
        try:
            for port in args:
                k.freeze(port)
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def break_all_motors(self) -> None:
        '''
        immediately stop all motors

        Args:
            None

        Returns:
            None
        '''
        k.freeze(self.port_wheel_left)
        k.freeze(self.port_wheel_right)

    def wait_motor_done(self, *args) -> bool:
        '''
        Waits until all specified motors have completed their rotations.

        Args:
            *args (int): Ports of the motors to wait for.

        Returns:
            bool: True when all specified motors are done.
        '''
        try:
            pending = set(args)

            while pending:
                for motor in list(pending):
                    if k.get_motor_done(motor):
                        pending.remove(motor)

            return True

        except Exception as e:
            log(str(e), important=True, in_exception=True)
            return False

    def align_drive_side(self, speed: int, drive_dir: bool = True, millis: int = 5000) -> None:
        '''
        Drives (forwards or backwards, depending if the speed is positive or negative) until it bumps into something, but it won't readjust with the other wheel, resulting in aligning as far away as possible

        Args:
            speed (int): If >= 0, then it will drive forward, otherwise it will drive backward
            drive_dir (bool, optional): If (True) it should drive the other direction to be able to turn again, without bumping (default: True) -> sometimes you want to be as close to an object as possible
            millis (int): The maximum amount of time (in milliseconds) it is allowed to try to align itself (default: 5000)

        Returns:
            bool: True when all specified motors are done.
        '''
        self.check_instances_buttons()
        ports = self.port_wheel_right, self.port_wheel_left, self.button_fl, self.button_fr
        velocity = 3600
        if speed < 0:
            ports = self.port_wheel_left, self.port_wheel_right, self.button_bl, self.button_br
            velocity = -3600

        startTime: float = k.seconds()
        while k.seconds() - startTime < (millis) / 1000:
            if ports[2].is_Pressed() and ports[3].is_Pressed():
                break
            elif ports[2].is_Pressed():
                k.mav(ports[1], 0)
                k.mav(ports[0], velocity)
            elif ports[3].is_Pressed():
                k.mav(ports[0], 0)
                k.mav(ports[1], velocity)
            else:
                k.mav(ports[0], velocity)
                k.mav(ports[1], velocity)
        k.ao()
        if drive_dir:
            self.drive_straight(200, -speed)
        self.break_all_motors()

    def align_drive_front(self, drive_bw: bool = True) -> None:
        '''
        aligning front by bumping into something, so both buttons on the front will be pressed. If there's an error by pressing the buttons, a fail save will occur. If at will it also drive backwards a little bit to be able to turn after it bumped into something

        Args:
            drive_bw (bool, optional): If you desire to drive backward a little bit (default: True) -> (but sometimes you want to stay aligned at the object)

        Returns:
            None
        '''
        self.check_instances_buttons_front()
        startTime: float = k.seconds()
        while k.seconds() - startTime < (1500) / 1000:
            if self.button_fl.is_Pressed() and self.button_fr.is_Pressed():
                break
            elif self.button_fl.is_Pressed():
                k.mav(self.port_wheel_left, -2000)
                k.mav(self.port_wheel_right, 3600)
            elif self.button_fr.is_Pressed():
                k.mav(self.port_wheel_right, -2000)
                k.mav(self.port_wheel_left, 3600)
            else:
                k.mav(self.port_wheel_right, 2000)
                k.mav(self.port_wheel_left, 2000)
        k.ao()
        if drive_bw:
            self.drive_straight(200, -500)
        self.break_all_motors()

    def align_drive_back(self, drive_fw: bool = True) -> None:
        '''
        aligning back by bumping into something, so both buttons on the back will be pressed. If there's an error by pressing the buttons, a fail save will occur. If at will it also drive forwards a little bit to be able to turn after it bumped into something

        Args:
            drive_fw (bool, optional): If you desire to drive forward a little bit (default: True) -> (but sometimes you want to stay aligned at the object)

        Returns:
            None
        '''
        self.check_instances_buttons_back()
        startTime: float = k.seconds()
        while k.seconds() - startTime < (2000) / 1000:
            if self.button_br.is_Pressed() and self.button_bl.is_Pressed():
                break
            elif self.button_br.is_Pressed():
                k.mav(self.port_wheel_left, -500)
                k.mav(self.port_wheel_right, 3600)
            elif self.button_bl.is_Pressed():
                k.mav(self.port_wheel_right, -500)
                k.mav(self.port_wheel_left, 3600)
            else:
                k.mav(self.port_wheel_right, -2000)
                k.mav(self.port_wheel_left, -2000)
        if drive_fw:
            self.drive_straight(200, -500)
        self.break_all_motors()

    def turn_wheel(self, direction: str, speed: int, millis: int) -> None:
        '''
        turning with only one wheel

        Args:
            direction (str): "left" or "right" - depends on where you want to go
            speed (int): how fast (and direction) it should drive
            millis (int): how long it should perform this task

        Returns:
            None
        '''
        if direction == 'left':
            k.mav(self.port_wheel_right, speed)
        elif direction == 'right':
            k.mav(self.port_wheel_left, speed)
        k.msleep(millis)

    def drive_straight_condition_analog(self, Instance, condition: str, value: int, millis: int = 9999999,
                                        speed: int = self.ds_speed) -> None:
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
        self.check_instances_buttons()
        theta = 0.0
        startTime = k.seconds()
        adjuster = round(speed / 1.8)
        ports = self.port_wheel_right, self.port_wheel_left, self.button_fl, self.button_fr
        if speed < 0:
            ports = self.port_wheel_left, self.port_wheel_right, self.button_bl, self.button_br

        if condition == 'let' or condition == '<=':  # let -> less or equal than
            while Instance.current_value() <= value and (not ports[2].is_Pressed() and not ports[
                3].is_Pressed()) and k.seconds() - startTime < millis / 1000:
                if theta < 1000 and theta > -1000:  # left
                    k.mav(ports[0], speed)
                    k.mav(ports[1], speed)
                elif theta < 1000:  # right
                    k.mav(ports[0], speed - adjuster)
                    k.mav(ports[1], speed + adjuster)
                else:
                    k.mav(ports[0], speed + adjuster)
                    k.mav(ports[1], speed - adjuster)
                k.msleep(10)
                theta += (k.gyro_z() - bias) * 2

        elif condition == 'het' or condition == '>=':  # het -> higher or equal than
            while Instance.current_value() >= value and (not ports[2].is_Pressed() and not ports[
                3].is_Pressed()) and k.seconds() - startTime < millis / 1000:
                if theta < 1000 and theta > -1000:  # left
                    k.mav(ports[0], speed)
                    k.mav(ports[1], speed)
                elif theta < 1000:  # right
                    k.mav(ports[0], speed - adjuster)
                    k.mav(ports[1], speed + adjuster)
                else:
                    k.mav(ports[0], speed + adjuster)
                    k.mav(ports[1], speed - adjuster)
                k.msleep(10)
                theta += (k.gyro_z() - bias) * 2

        elif condition == 'ht' or condition == '>':  # ht -> higher than
            while Instance.current_value() > value and (not ports[2].is_Pressed() and not ports[
                3].is_Pressed()) and k.seconds() - startTime < millis / 1000:
                if theta < 1000 and theta > -1000:  # left
                    k.mav(ports[0], speed)
                    k.mav(ports[1], speed)
                elif theta < 1000:  # right
                    k.mav(ports[0], speed - adjuster)
                    k.mav(ports[1], speed + adjuster)
                else:
                    k.mav(ports[0], speed + adjuster)
                    k.mav(ports[1], speed - adjuster)
                k.msleep(10)
                theta += (k.gyro_z() - bias) * 2

        elif condition == 'lt' or condition == '<':  # lt -> less than
            while Instance.current_value() < value and (not ports[2].is_Pressed() and not ports[
                3].is_Pressed()) and k.seconds() - startTime < millis / 1000:
                if theta < 1000 and theta > -1000:  # left
                    k.mav(ports[0], speed)
                    k.mav(ports[1], speed)
                elif theta < 1000:  # right
                    k.mav(ports[0], speed - adjuster)
                    k.mav(ports[1], speed + adjuster)
                else:
                    k.mav(ports[0], speed + adjuster)
                    k.mav(ports[1], speed - adjuster)
                k.msleep(10)
                theta += (k.gyro_z() - bias) * 2

    def drive_straight_side_checker(self, follow: bool, speed: int, millis: int) -> None:
        # you rather not try to make it drive backwards...
        '''
        Either (try) to align yourself on the black line with the side light sensor and follow the line OR drive until the side light sensor detects black

        Args:
           follow (bool): If you want to stay on the black line with the side light sensor (True and experimental) or drive until the side light sensor detects black (False - in this case just do the drive_straight_condition_analog function to be honest)
           speed (int, optional): how fast it should drive (forwards or backwards) (default: ds_speed)
           millis (int, optional): how long it is allowed to be in the function (roughly)

        Returns:
           None
        '''
        self.check_instances_buttons()
        self.check_instance_light_sensors()
        startTime: float = k.seconds()
        theta = 0.0
        adjuster = round(speed / 1.8)
        ports = self.button_fl, self.button_fr, self.light_sensor_front, self.light_sensor_back, self.port_wheel_right, self.port_wheel_left
        if speed < 0:
            ports = self.button_bl, self.button_br, self.light_sensor_back, self.light_sensor_front, self.port_wheel_left, self.port_wheel_right
            adjuster = -adjuster

        def scenario1():
            while not self.light_sensor_side.sees_Black():
                k.mav(ports[4], speed)
                k.mav(ports[5], -speed)
            k.ao()
            while ports[2].sees_White():
                k.mav(ports[4], -speed)
            k.ao()
            while ports[2].sees_Black():
                k.mav(ports[4], -speed)
            k.msleep(100)

        def scenario2():
            while not self.light_sensor_side.sees_Black():
                k.mav(ports[4], speed)  # right
                k.mav(ports[5], -speed)  # left
            while ports[2].sees_White():  # Front -> 1200
                k.mav(ports[4], speed)

        def scenario3():
            while not self.light_sensor_side.sees_Black():
                k.mav(ports[5], speed)
            while ports[2].sees_Black():
                k.mav(ports[4], -speed)
            k.msleep(10)

        if not follow:
            self.break_all_motors()
            while k.seconds() - startTime < (millis) / 1000 and not self.light_sensor_side.sees_Black():
                if theta < 1000 and theta > -1000:  # left
                    k.mav(ports[4], speed)
                    k.mav(ports[5], speed)
                elif theta < 1000:  # right
                    k.mav(ports[4], speed - adjuster)
                    k.mav(ports[5], speed + adjuster)
                else:
                    k.mav(ports[4], speed + adjuster)
                    k.mav(ports[5], speed - adjuster)
                k.msleep(10)
                theta += (k.gyro_z() - bias) * 1.5
            k.ao()
            k.msleep(1)
        else:
            while k.seconds() - startTime < (millis) / 1000 and (
                    not ports[0].is_Pressed() and not ports[1].is_Pressed()):
                theta = 0.0
                adjuster = 1600
                if speed < 0:
                    adjuster = -adjuster
                while self.light_sensor_side.sees_Black() and (not ports[0].is_Pressed() and not ports[1].is_Pressed()):
                    if theta < 1000 and theta > -1000:  # left
                        k.mav(ports[5], speed)
                        k.mav(ports[4], speed)
                    elif theta < 1000:  # right
                        k.mav(ports[4], speed - adjuster)
                        k.mav(ports[5], speed + adjuster)
                    else:
                        k.mav(ports[4], speed + adjuster)
                        k.mav(ports[5], speed - adjuster)
                    k.msleep(10)
                    theta += (k.gyro_z() - bias) * 1.5
                if ports[2].sees_Black():
                    scenario3()
                elif ports[3].sees_Black():
                    scenario2()
                else:
                    while ports[3].sees_White():  # Back -> 2500
                        k.mav(ports[4], -speed)
                    if not ports[2].sees_White():  # Front -> 2000
                        scenario1()
                    else:
                        scenario2()
                k.ao()
                k.msleep(200)

    def turn_to_black_line(self, direction: str, millis: str = 80, speed: int = self.ds_speed) -> None:
        '''
       Turn as long as the light sensor (front or back, depends if the speed is positive or negative) sees the black line

       Args:
           direction (str): "right" or "left" - depends on where you want to go
           millis (int, optional): how long (in milliseconds) to drive until the sensor gets checked (no threading is used) (default: 80)
           speed (int, optional): how fast it should turn (default: ds_speed)

       Returns:
           None
       '''
        self.check_instance_light_sensors_middle()
        ports = self.port_wheel_right, self.port_wheel_left, self.light_sensor_front
        if speed < 0:
            ports = self.port_wheel_left, self.port_wheel_right, self.light_sensor_back

        if direction == 'right':
            while not ports[2].sees_Black():  # Front -> 3500
                k.mav(ports[1], speed)
                k.mav(ports[0], -speed)
                k.msleep(millis)
        elif direction == 'left':
            while not ports[2].sees_Black():  # Front -> 3500
                k.mav(ports[0], speed)
                k.mav(ports[1], -speed)
                k.msleep(millis)
        else:
            log('Only "right" and "left" are valid commands for the direction!', in_exception=True)
            raise Exception(
                'turn_black_line() Exception: Only "right" and "left" are valid commands for the direction!')
        k.ao()

    def align_line(self, onLine: bool, direction: str = None, speed: int = self.ds_speed) -> None:
        '''
        ==== NEEDS IMPROVEMENT ====
        If you are anywhere on the black line, you can align yourself on the black line. If you are not on the line, it drives (forwards or backwards, depends if the speed is positive or negative) until the line was found and then aligns as desired.
        Improvement: align backwards, so there is no need to make a 180B0 turn. Would spare you some time.

        Args:
           onLine (bool): Are you already on the black line (True), or do you need to get onto it (False)? If you are not on the line, you need to write the direction you want to face to!
           direction (str): "right" or "left" - depends on where you want to go
           speed (int, optional): how fast it should drive (default: ds_speed)
           maxDuration  (int, optional): the time (in milliseconds) it is allowed to turn in one direction until a failsave gets executed to turn to the other direction (default: 100)

        Returns:
           None
        '''
        self.check_instances_buttons()
        self.check_instance_light_sensors_middle()
        if not onLine:
            if direction != 'left' and direction != 'right':
                log('If the Wombat is not on the line, please tell it which direction it should face when it is on the line ("right" or "left")', in_exception=True)
                raise Exception(
                    'align_line() Exception: If the Wombat is not on the line, please tell it which direction it should face when it is on the line ("right" or "left")')

            ports = self.light_sensor_back, self.light_sensor_front
            if speed < 0:
                ports = self.light_sensor_front, self.light_sensor_back

            self.drive_straight_condition_analog(ports[1], '<=', ports[1].get_value_black(),
                                                 speed=speed)  # Front -> 3500
            start_time = k.seconds()
            self.drive_straight_condition_analog(ports[0], '<=', ports[0].get_value_black(),
                                                 speed=speed)  # Front -> 3300
            end_time = k.seconds()
            k.ao()

            seconds = end_time - start_time

            self.drive_straight((seconds // 2) * 1000, -speed)
            self.turn_to_black_line(direction, speed=speed)
        else:
            startTime = k.seconds()
            maxDuration = 100  # only 0.1 second to turn
            ports = self.port_wheel_right, self.port_wheel_left, self.button_fl, self.button_fr, self.light_sensor_front
            direction = 'right', 'left'
            if speed < 0:
                ports = self.port_wheel_left, self.port_wheel_right, self.button_bl, self.button_br, self.light_sensor_back
                direction = 'left', 'right'

            while True:
                k.mav(ports[0], speed)
                k.mav(ports[1], -speed)
                if (k.seconds() - startTime > maxDuration / 1000):
                    self.turn_to_black_line(direction[0], 15)
                    break
                if ports[4].sees_Black():  # Front -> 3500
                    self.turn_to_black_line(direction[1], 20)
                    break
                if ports[2].is_Pressed() or ports[3].is_Pressed():
                    break

    def black_line(self, millis: int, speed: int = self.ds_speed) -> None:
        '''
       drive on the black line as long as wished

       Args:
           millis (int): how long you want to follow the black line (in milliseconds)
           speed (int, optional): how fast it should drive straight (default: ds_speed)

       Returns:
           None
       '''
        self.check_instances_buttons()
        self.check_instance_light_sensors_middle()
        startTime: float = k.seconds()
        theta = 0.0
        adjuster = round(speed / 1.8)
        ports = self.button_fl, self.button_fr, self.light_sensor_front
        if speed < 0:
            ports = self.button_bl, self.button_br, self.light_sensor_back

        while k.seconds() - startTime < (millis) / 1000 and (not ports[0].is_Pressed() and not ports[1].is_Pressed()):
            self.drive_straight_condition_analog(ports[2], '>=', ports[2].get_value_black(), speed=speed,
                                                 millis=100)  # Front -> 3500

            if not ports[2].sees_Black():
                self.align_line(True, speed=speed)

    def drive_straight(self, millis: int, speed: int = self.ds_speed) -> None:
        '''
        drive straight for as long as you want to (in millis)

        Args:
            millis (int): for how long you want to drive straight
            speed (int, optional): the speed it is going to drive straight (default: ds_speed)

        Returns:
            None
        '''
        startTime: float = k.seconds()
        theta = 0.0
        adjuster = round(speed / 1.8)
        ports = self.port_wheel_right, self.port_wheel_left
        if speed < 0:
            ports = self.port_wheel_left, self.port_wheel_right
        # adjuster = -adjuster
        while k.seconds() - startTime < (millis) / 1000:
            if theta < 1000 and theta > -1000:  # left
                k.mav(ports[0], speed)
                k.mav(ports[1], speed)
            elif theta < 1000:  # right
                k.mav(ports[0], speed - adjuster)
                k.mav(ports[1], speed + adjuster)
            else:
                k.mav(ports[0], speed + adjuster)
                k.mav(ports[1], speed - adjuster)
            k.msleep(10)
            theta += (k.gyro_z() - self.bias_gyro_z) * 1.5
        k.ao()
        k.msleep(1)

    def next_to_onto_line(self, leaning_side: str = None) -> None:
        '''
        If you are next to a black line, you can get onto it and be aligned

        Args:
            leaning_side (str, optional): the side ("right" or "left") where the wombat has to get to (default: None)

        Returns:
            None
        '''
        self.check_instance_light_sensors_middle()
        if not leaning_side or leaning_side == 'right':
            ports = self.port_wheel_left, self.port_wheel_right
        else:
            ports = self.port_wheel_right, self.port_wheel_left
        startTime = k.seconds()
        while self.light_sensor_back.sees_White() and self.light_sensor_front.sees_White():
            if k.seconds() - startTime < self.NINETY_DEGREES_SECS:
                k.mav(ports[0], self.ds_speed)
                k.mav(ports[1], -self.ds_speed)
            else:
                k.mav(ports[0], -self.ds_speed)
                k.mav(ports[1], self.ds_speed // 2)
                k.msleep(1)

            self.break_all_motors()

        if not self.light_sensor_back.sees_White():  # hinten ist oben
            while not self.light_sensor_front.sees_Black():
                k.mav(ports[0], -self.ds_speed)
                k.mav(ports[1], -self.ds_speed)
            self.break_all_motors()
            while self.light_sensor_front.sees_Black():
                k.mav(ports[0], 1500)
            self.break_all_motors()
            while not self.light_sensor_front.sees_Black():
                k.mav(ports[1], 1500)
            self.break_all_motors()
            while self.light_sensor_front.sees_Black():
                k.mav(ports[1], 1500)
            self.break_all_motors()
            while not self.light_sensor_front.sees_Black():
                k.mav(ports[1], -1500)
                k.mav(ports[0], -200)
            self.break_all_motors()

        elif not self.light_sensor_front.sees_White():  # vorne ist oben
            while not self.light_sensor_back.sees_Black():
                k.mav(ports[0], self.ds_speed)
                k.mav(ports[1], self.ds_speed)
            while not self.light_sensor_front.sees_Black():
                k.mav(ports[0], -1500)
                k.mav(ports[1], 1500)

            self.break_all_motors()

            if not self.light_sensor_front.sees_Black():
                self.break_all_motors()
                while not self.light_sensor_front.sees_White():
                    k.mav(ports[1], 1500)
                while not self.light_sensor_front.sees_Black():
                    k.mav(ports[1], 1500)

            if not self.light_sensor_back.sees_Black():
                while self.light_sensor_front.sees_Black():
                    k.mav(ports[1], 1500)
                while self.light_sensor_back.sees_White():
                    k.mav(ports[1], -1500)
                    k.mav(ports[0], 1500)
            self.break_all_motors()

    def align_on_black_line(self, crossing: bool, direction: str = 'vertical', leaning_side: str = None) -> None:
        # hint: do not face the black line
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
        try:
            if direction != 'vertical' and direction != 'horizontal':
                log('Only "vertical" or "horizontal" are valid options for the "direction" parameter', in_exception=True)
                raise Exception(
                    'align_on_black_line() Exception: Only "vertical" or "horizontal" are valid options for the "direction" parameter')

            if leaning_side != None and leaning_side != 'right' and leaning_side != 'left':
                log('Only "right", "left" or None / nothing are valid options for the "leaning_side" parameter', in_exception=True)
                raise Exception(
                    'align_on_black_line() Exception: Only "right", "left" or None / nothing are valid options for the "leaning_side" parameter')

            if not crossing:
                log('no crossing')
                if not leaning_side or leaning_side == 'right':
                    ports = self.port_wheel_left, self.port_wheel_right
                else:
                    ports = self.port_wheel_right, self.port_wheel_left
                startTime = k.seconds()
                while self.light_sensor_back.sees_White() and self.light_sensor_front.sees_White():
                    if k.seconds() - startTime < self.NINETY_DEGREES_SECS:
                        k.mav(ports[0], self.ds_speed)
                        k.mav(ports[1], -self.ds_speed)
                    else:
                        k.mav(ports[0], -self.ds_speed)
                        k.mav(ports[1], self.ds_speed // 2)
                        k.msleep(1)

                self.break_all_motors()

                if not self.light_sensor_back.sees_White():  # hinten ist oben
                    while not self.light_sensor_front.sees_Black():
                        k.mav(ports[0], -self.ds_speed)
                        k.mav(ports[1], -self.ds_speed)
                    self.break_all_motors()
                    while self.light_sensor_front.sees_Black():
                        k.mav(ports[0], 1500)
                    self.break_all_motors()
                    while not self.light_sensor_front.sees_Black():
                        k.mav(ports[1], 1500)
                    self.break_all_motors()
                    while self.light_sensor_front.sees_Black():
                        k.mav(ports[1], 1500)
                    self.break_all_motors()
                    while not self.light_sensor_front.sees_Black():
                        k.mav(ports[1], -1500)
                        k.mav(ports[0], -200)
                    self.break_all_motors()

                elif not self.light_sensor_front.sees_White():  # vorne ist oben
                    while not self.light_sensor_back.sees_Black():
                        k.mav(ports[0], self.ds_speed)
                        k.mav(ports[1], self.ds_speed)
                    while not self.light_sensor_front.sees_Black():
                        k.mav(ports[0], -1500)
                        k.mav(ports[1], 1500)

                self.break_all_motors()

                if not self.light_sensor_front.sees_Black():
                    self.break_all_motors()
                    while not self.light_sensor_front.sees_White():
                        k.mav(ports[1], 1500)

                    while not self.light_sensor_front.sees_Black():
                        k.mav(ports[1], 1500)

                if not self.light_sensor_back.sees_Black():
                    while self.light_sensor_front.sees_Black():
                        k.mav(ports[1], 1500)
                    while self.light_sensor_back.sees_White():
                        k.mav(ports[1], -1500)
                        k.mav(ports[0], 1500)

                self.break_all_motors()

            else:
                ports = self.port_wheel_left, self.port_wheel_right
                on_line = False
                first_line_hit = None
                line_counter = 0
                line_timer = 0
                line_timer_collector = []

                startTime_front = k.seconds()
                while k.seconds() - startTime_front < self.ONEEIGHTY_DEGREES_SECS * 2 + 0.2:
                    while self.light_sensor_front.sees_Black():
                        on_line = True
                        line_timer += 1
                        k.mav(ports[0], -self.ds_speed)
                        k.mav(ports[1], self.ds_speed)
                    if on_line:
                        if not first_line_hit:
                            first_line_hit = k.seconds() - startTime_front
                        on_line = False
                        line_counter += 1
                        line_timer_collector.append(line_timer)
                        line_timer = 0
                    k.mav(ports[0], -self.ds_speed)
                    k.mav(ports[1], self.ds_speed)

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
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], -self.ds_speed)
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], -self.ds_speed)
                        self.break_all_motors()
                    else:
                        d = direct[1]
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], -self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                        self.break_all_motors()
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], -self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                        self.break_all_motors()
                    self.drive_side(d, 5)

                elif line_counter == 3:
                    if dir_picker[0] > dir_picker[1]:
                        d = direct[0]
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], -self.ds_speed)
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                        self.break_all_motors()
                        if not self.light_sensor_front.sees_Black():
                            while not self.light_sensor_front.sees_Black():
                                k.mav(ports[0], -self.ds_speed)
                                k.mav(ports[1], self.ds_speed)
                            self.break_all_motors()
                    else:
                        d = direct[1]
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], -self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                        self.break_all_motors()
                        if not self.light_sensor_front.sees_Black():
                            while not self.light_sensor_front.sees_Black():
                                k.mav(ports[0], -self.ds_speed)
                                k.mav(ports[1], self.ds_speed)
                            self.break_all_motors()
                    self.drive_side(d, 5)

                else:  # line_counter == 2
                    if dir_picker[0] < dir_picker[1]:
                        d = direct[0]
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], -self.ds_speed)
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                        self.break_all_motors()
                    else:
                        d = direct[1]
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], -self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                        self.break_all_motors()

                    self.drive_side(d, 5)


        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def drive_til_distance(self, mm_to_object: int, speed: int = self.ds_speed) -> None:
        '''
        drive straight as long as the object in front of the distance sensor (in mm) is not in reach

        Args:
            mm_to_object (int): the distance (in mm) between the distance sensor and the object in front of the sensor
            speed (int, optional): the speed it is going to drive straight (default: ds_speed)

        Returns:
            None
        '''
        self.check_instances_buttons_back()
        self.check_instance_distance_sensor()
        if mm_to_object > 800 or mm_to_object < 10:
            log('You can only put a value in range of 10 - 800 for the distance parameter!', in_exception=True)
            raise Exception(
                'drive_til_distance() Exception: You can only put a value in range of 10 - 800 for the distance parameter!')

        self.isClose = False
        theta = 0.0
        adjuster = 1600
        if self.distance_sensor.current_value() > 1800:
            while self.distance_sensor.current_value() > 1800 and (
                    not self.button_bl.is_Pressed() and not self.button_br.is_Pressed()):
                if theta < 1000 and theta > -1000:
                    k.mav(self.port_wheel_left, -speed)
                    k.mav(self.port_wheel_right, -speed)
                elif theta > 1000:
                    k.mav(self.port_wheel_left, -speed - adjuster)
                    k.mav(self.port_wheel_right, -speed + adjuster)
                else:
                    k.mav(self.port_wheel_left, -speed + adjuster)
                    k.mav(self.port_wheel_right, -speed - adjuster)
                k.msleep(10)
                theta += (k.gyro_z() - self.bias_gyro_z) * 1.5
            if theta != 0.0:
                # break_all_motors()
                k.mav(self.port_wheel_left, speed)
                k.mav(self.port_wheel_right, speed)
                k.msleep(20)
                k.ao()
                k.msleep(100)
        else:
            val = mm_to_object
            if mm_to_object <= 200:
                val = 200

            far_sensor_values = [500, 530, 600, 670, 715, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700,
                                 1800,
                                 1900,
                                 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900]
            far_distances_mm = [800, 700, 600, 580, 540, 480, 400, 360, 320, 285, 260, 235, 220, 205, 190, 180, 170,
                                160, 150, 140, 135, 130, 125, 120, 115, 110, 100]
            combination = dict(zip(far_distances_mm, far_sensor_values))
            next_step = min(combination, key=lambda x: abs(x - val))
            next_value = combination[next_step]

            def distance_stopper():
                tolerance = val / 10
                try:
                    lookup = interp1d(far_sensor_values, far_distances_mm, kind='linear', fill_value="extrapolate")
                except Exception as e:
                    log(str(e), important=True, in_exception=True)

                def get_distance_from_sensor(sensor_value):
                    return float(lookup(sensor_value))

                def is_target_distance_reached():
                    value = self.distance_sensor.current_value()
                    dist = get_distance_from_sensor(value)
                    return dist - val < tolerance

                while True:
                    if is_target_distance_reached():
                        self.isClose = True
                        sys.exit()
                        break

            if self.distance_sensor.current_value() < next_value:
                threading.Thread(target=distance_stopper).start()

                while not self.isClose:
                    if theta < 1000 and theta > -1000:
                        k.mav(self.port_wheel_left, speed)
                        k.mav(self.port_wheel_right, speed)
                    elif theta > 1000:
                        k.mav(self.port_wheel_left, speed - adjuster)
                        k.mav(self.port_wheel_right, speed + adjuster)
                    else:
                        k.mav(self.port_wheel_left, speed + adjuster)
                        k.mav(self.port_wheel_right, speed - adjuster)

                    k.msleep(5)
                    theta += (k.gyro_z() - self.bias_gyro_z) * 1.5

                self.break_all_motors()
                k.ao()

        if mm_to_object <= 200:
            counter = 200
            while counter > mm_to_object:
                counter -= 1
                if theta < 1000 and theta > -1000:
                    k.mav(self.port_wheel_left, speed)
                    k.mav(self.port_wheel_right, speed)
                elif theta > 1000:
                    k.mav(self.port_wheel_left, speed - adjuster)
                    k.mav(self.port_wheel_right, speed + adjuster)
                else:
                    k.mav(self.port_wheel_left, speed + adjuster)
                    k.mav(self.port_wheel_right, speed - adjuster)
                time.sleep(0.0023)
                theta += (k.gyro_z() - self.bias_gyro_z) * 1.5

            self.break_all_motors()

    def turn_degrees_far(self, direction: str, degree: int, speed: int = self.ds_speed) -> None:
        '''
       turn the amount of degrees given, to take a turn with only one wheel, resulting in a turn not on the spot

       Args:
           direction (str): "left" or "right", depending on where you want to go
           degree (int): the amount of degrees (B0) to turn from the current point (only values from 0 - 180 allowed for maximum efficiency)

       Returns:
           None
       '''
        if direction != 'right' and direction != 'left':
            log('Only "right" or "left" are valid options for the "direction" parameter', in_exception=True)
            raise Exception(
                'turn_degrees_far() Exception: Only "right" or "left" are valid options for the "direction" parameter')

        if degree > 180 and degree < 0:
            log('Only values from range 0 - 180 are valid for the "degree" parameter', in_exception=True)
            raise Exception(
                'turn_degrees_far() Exception: Only values from range 0 - 180 are valid for the "degree" parameter')

        div = 180 / degree
        value = self.ONEEIGHTY_DEGREES_SECS / div
        if degree <= 90:
            div = 90 / degree
            value = self.NINETY_DEGREES_SECS / div
        self.break_all_motors()
        if direction == 'right':
            k.mav(self.port_wheel_left, speed)
            time.sleep(2 * value)
        elif direction == 'left':
            k.mav(self.port_wheel_right, speed)
            time.sleep(2 * value)
        self.break_all_motors()

    def turn_degrees(self, direction: str, degree: int, speed: int = self.ds_speed) -> None:
        '''
        turn the amount of degrees given, to take a turn with all wheels, resulting in a turn on the spot

        Args:
            direction (str): "left" or "right", depending on where you want to go
            degree (int): the amount of degrees (B0) to turn from the current point (only values from 0 - 180 allowed for maximum efficiency)

        Returns:
            None
        '''
        if direction != 'right' and direction != 'left':
            log('Only "right" or "left" are valid options for the "direction" parameter', in_exception=True)
            raise Exception(
                'turn_degrees() Exception: Only "right" or "left" are valid options for the "direction" parameter')

        if degree > 180 and degree < 1:
            log('Only values from range 1 - 180 are valid for the "degree" parameter', in_exception=True)
            raise Exception(
                'turn_degrees() Exception: Only values from range 1 - 180 are valid for the "degree" parameter')

        div = 180 / degree
        value = self.ONEEIGHTY_DEGREES_SECS / div
        if degree <= 90:
            div = 90 / degree
            value = self.NINETY_DEGREES_SECS / div

        if direction == 'right':
            k.mav(self.port_wheel_left, self.ds_speed)
            k.mav(self.port_wheel_right, -self.ds_speed)
            time.sleep(value)
        elif direction == 'left':
            k.mav(self.port_wheel_left, -self.ds_speed)
            k.mav(self.port_wheel_right, self.ds_speed)
            time.sleep(value)
        k.ao()


class driveR_four:
    def __init__(self,
                 Port_front_right_wheel: int,
                 Port_back_right_wheel: int,
                 Port_front_left_wheel: int,
                 Port_back_left_wheel: int,
                 DS_SPEED: int = 2160,
                 Instance_button_front_right: Digital = None,
                 Instance_button_front_left: Digital = None,
                 Instance_button_back_right: Digital = None,
                 Instance_button_back_left: Digital = None,
                 Instance_light_sensor_front: LightSensor = None,
                 Instance_light_sensor_back: LightSensor = None,
                 Instance_light_sensor_side: LightSensor = None,
                 Instance_distance_sensor: DistanceSensor = None
                 ):

        self.port_wheel_fl = Port_front_left_wheel
        self.port_wheel_fr = Port_front_right_wheel
        self.port_wheel_bl = Port_back_left_wheel
        self.port_wheel_br = Port_back_right_wheel

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
        self.bias_accel_x = None  # There are no function where you can do anything with the accel x -> you need to invent them by yourself
        self.bias_accel_y = None  # There are no function where you can do anything with the accel y -> you need to invent them by yourself
        self.isClose = False
        self.ONEEIGHTY_DEGREES_SECS = None
        self.NINETY_DEGREES_SECS = None

    # ======================== SET INSTANCES ========================

    def set_instance_distance_sensor(self, Instance_distance_sensor: DistanceSensor) -> None:
        '''
        create or overwrite the existance of the distance_sensor

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
        create or overwrite the existance of all light sensors

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
        create or overwrite the existance of the front light sensors

        Args:
            Instance_light_sensor_front (LightSensor): the instance of the front light sensor

       Returns:
            None
        '''
        self.light_sensor_front = Instance_light_sensor_front

    def set_instance_light_sensor_back(self, Instance_light_sensor_back: LightSensor) -> None:
        '''
        create or overwrite the existance of the back light sensor

        Args:
            Instance_light_sensor_back (LightSensor): the instance of the back light sensor

       Returns:
            None
        '''
        self.light_sensor_back = Instance_light_sensor_back

    def set_instance_light_sensor_side(self, Instance_light_sensor_side: LightSensor) -> None:
        '''
        create or overwrite the existance of the side light sensor

        Args:
            Instance_light_sensor_side (LightSensor):  the instance of the side light sensor

       Returns:
            None
        '''
        self.light_sensor_side = Instance_light_sensor_side

    def set_instances_buttons(self, Instance_button_front_right: Digital, Instance_button_front_left: Digital,
                              Instance_button_back_right: Digital, Instance_button_back_left: Digital) -> None:
        '''
        create or overwrite the existance of all buttons

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
        create or overwrite the existance of the front left button

        Args:
            Instance_button_front_left (Digital): the instance of the front left button

       Returns:
            None
        '''
        self.button_fl = Instance_button_front_left

    def set_instance_button_fr(self, Instance_button_front_right: Digital) -> None:
        '''
        create or overwrite the existance of the front right button

        Args:
            Instance_button_front_right (Digital): the instance of the front right button

       Returns:
            None
        '''
        self.button_fr = Instance_button_front_right

    def set_instance_button_bl(self, Instance_button_back_left: Digital) -> None:
        '''
        create or overwrite the existance of the back left button

        Args:
            Instance_button_back_left (Digital):  the instance of the back left button

       Returns:
            None
        '''
        self.button_bl = Instance_button_back_left

    def set_instance_button_br(self, Instance_button_back_right: Digital) -> None:
        '''
        create or overwrite the existance of the back right button

        Args:
            Instance_button_back_right (Digital):  the instance of the back right button

       Returns:
            None
        '''
        self.button_br = Instance_button_back_right

    # ======================== CHECK INSTANCES ========================

    def check_instance_light_sensors(self) -> bool:
        '''
        inspect the existance of all light sensors

        Args:
            None

       Returns:
            if there is an instance of all light sensor in existance
        '''
        if not isinstance(self.light_sensor_front, LightSensor):
            log('Light sensor front is not initialized!', in_exception=True)
            raise Exception('Light sensor front is not initialized!')

        if not isinstance(self.light_sensor_back, LightSensor):
            log('Light sensor back is not initialized!', in_exception=True)
            raise Exception('Light sensor back is not initialized!')

        if not isinstance(self.light_sensor_side, LightSensor):
            log('Light sensor side is not initialized!', in_exception=True)
            raise Exception('Light sensor side is not initialized!')
        return True

    def check_instance_light_sensors_middle(self) -> bool:
        '''
        inspect the existance of the middle light sensors

        Args:
            None

       Returns:
            if there is an instance of the middle light sensors in existance
        '''
        if not isinstance(self.light_sensor_front, LightSensor):
            log('Light sensor front is not initialized!', in_exception=True)
            raise Exception('Light sensor front is not initialized!')

        if not isinstance(self.light_sensor_back, LightSensor):
            log('Light sensor back is not initialized!', in_exception=True)
            raise Exception('Light sensor back is not initialized!')
        return True

    def check_instance_light_sensor_front(self) -> bool:
        '''
        inspect the existance of the front light sensor

        Args:
            None

       Returns:
            if there is an instance of the front light sensor in existance
        '''
        if not isinstance(self.light_sensor_front, LightSensor):
            log('Light sensor front is not initialized!', in_exception=True)
            raise Exception('Light sensor front is not initialized!')
        return True

    def check_instance_light_sensor_back(self) -> bool:
        '''
        inspect the existance of the back light sensor

        Args:
            None

       Returns:
            if there is an instance of the back light sensor in existance
        '''
        if not isinstance(self.light_sensor_back, LightSensor):
            log('Light sensor back is not initialized!', in_exception=True)
            raise Exception('Light sensor back is not initialized!')
        return True

    def check_instance_light_sensor_side(self) -> bool:
        '''
        inspect the existance of the side light sensor

        Args:
            None

       Returns:
            if there is an instance of the side light sensor in existance
        '''
        if not isinstance(self.light_sensor_side, LightSensor):
            log('Light sensor side is not initialized!', in_exception=True)
            raise Exception('Light sensor side is not initialized!')
        return True

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
            raise Exception('Distance sensor is not initialized!')
        return True

    def check_instance_button_fl(self) -> bool:
        '''
        inspect the existance of the front left button

        Args:
            None

       Returns:
            if there is an instance of the front left button in existance
        '''
        if not isinstance(self.button_fl, Digital):
            log('Button front left is not initialized!', in_exception=True)
            raise Exception('Button front left is not initialized!')
        return True

    def check_instance_button_fr(self) -> bool:
        '''
        inspect the existance of the front right button

        Args:
            None

       Returns:
            if there is an instance of the front right button in existance
        '''
        if not isinstance(self.button_fr, Digital):
            log('Button front right is not initialized!', in_exception=True)
            raise Exception('Button front right is not initialized!')
        return True

    def check_instance_button_bl(self) -> bool:
        '''
        inspect the existance of the back left button

        Args:
            None

       Returns:
            if there is an instance of the back left button in existance
        '''
        if not isinstance(self.button_bl, Digital):
            log('Button back left is not initialized!', in_exception=True)
            raise Exception('Button back left is not initialized!')
        return True

    def check_instance_button_br(self) -> bool:
        '''
        inspect the existance of the back right button

        Args:
            None

       Returns:
            if there is an instance of the back right button in existance
        '''
        if not isinstance(self.button_br, Digital):
            log('Button back right is not initialized!', in_exception=True)
            raise Exception('Button back right is not initialized!')
        return True

    def check_instances_buttons_front(self) -> bool:
        '''
        inspect the existance of the front buttons

        Args:
            None

       Returns:
            if there is an instance of the front buttons in existance
        '''
        if not isinstance(self.button_fl, Digital):
            log('Button front left is not initialized!', in_exception=True)
            raise Exception('Button front left is not initialized!')

        if not isinstance(self.button_fr, Digital):
            log('Button front right is not initialized!', in_exception=True)
            raise Exception('Button front right is not initialized!')

        return True

    def check_instances_buttons_back(self) -> bool:
        '''
        inspect the existance of the back buttons

        Args:
            None

       Returns:
            if there is an instance of the back buttons in existance
        '''
        if not isinstance(self.button_bl, Digital):
            log('Button back left is not initialized!', in_exception=True)
            raise Exception('Button back left is not initialized!')

        if not isinstance(self.button_br, Digital):
            log('Button back right is not initialized!', in_exception=True)
            raise Exception('Button back right is not initialized!')

        return True

    def check_instances_buttons(self) -> bool:
        '''
        inspect the existance of all buttons

        Args:
            None

       Returns:
            if there is an instance of all buttons in existance
        '''
        if not isinstance(self.button_fl, Digital):
            log('Button front left is not initialized!', in_exception=True)
            raise Exception('Button front left is not initialized!')

        if not isinstance(self.button_fr, Digital):
            log('Button front right is not initialized!', in_exception=True)
            raise Exception('Button front right is not initialized!')

        if not isinstance(self.button_bl, Digital):
            log('Button back left is not initialized!', in_exception=True)
            raise Exception('Button back left is not initialized!')

        if not isinstance(self.button_br, Digital):
            log('Button back right is not initialized!', in_exception=True)
            raise Exception('Button back right is not initialized!')

        return True

    # ===================== CALIBRATE BIAS =====================

    def calibrate_degrees(self) -> None:
        '''
        drive to the side until a black line was found and then slowly turn 180B0 to know how long it takes to make one 180B0 turn

        Args:
            None

       Returns:
            None (but sets a class variable)
        '''
        self.check_instance_light_sensors_middle()
        self.drive_side_condition_analog('left', self.light_sensor_front, '<',
                                         self.light_sensor_front.get_value_black(), speed=self.ds_speed // 2)
        k.msleep(1000)
        startTime = k.seconds()
        while k.seconds() - startTime < (1200) / 1000:
            k.mav(self.port_wheel_fl, self.ds_speed // 2)
            k.mav(self.port_wheel_fr, -self.ds_speed // 2)
            k.mav(self.port_wheel_bl, self.ds_speed // 2)
            k.mav(self.port_wheel_br, -self.ds_speed // 2)
        while self.light_sensor_front.sees_White():
            k.mav(self.port_wheel_fl, self.ds_speed // 2)
            k.mav(self.port_wheel_fr, -self.ds_speed // 2)
            k.mav(self.port_wheel_bl, self.ds_speed // 2)
            k.mav(self.port_wheel_br, -self.ds_speed // 2)
        while self.light_sensor_back.sees_White():
            k.mav(self.port_wheel_fl, self.ds_speed // 2)
            k.mav(self.port_wheel_fr, -self.ds_speed // 2)
            k.mav(self.port_wheel_bl, self.ds_speed // 2)
            k.mav(self.port_wheel_br, -self.ds_speed // 2)
        k.ao()
        endTime = k.seconds()
        self.ONEEIGHTY_DEGREES_SECS = (endTime - startTime) / 1.5
        self.NINETY_DEGREES_SECS = self.ONEEIGHTY_DEGREES_SECS / 2
        log('DEGREES CALIBRATED')

    def calibrate_gyro_z(self, counter: int, max: int) -> None:
        '''
        calibrates the bias from the gyro to be able to drive straight, since the bias is for telling us how far off from driving straight the wombat is

        Args:
            counter (int): the number where it is at the moment
            max (int): how many caLibrations there are (to show it on the screen and for debugging usage)

        Returns:
            None
        '''
        i: int = 0
        avg: float = 0
        time: int = 8000
        while i < time:
            avg += k.gyro_z()
            k.msleep(1)
            i += 1
        self.bias_gyro_z = avg / time
        log(f'{counter}/{max} - GYRO Z CALIBRATED')

    def calibrate_gyro_y(self, counter: int, max: int) -> None:
        '''
        calibrates the bias from the gyro to be able to drive straight, since the bias is for telling us how far off from driving straight the wombat is (theoretically it is for driving sideways)

        Args:
            counter (int): the number where it is at the moment
            max (int): how many caLibrations there are (to show it on the screen and for debugging usage)

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
        log(f'{counter}/{max} - GYRO Y CALIBRATED')

    def calibrate_accel_x(self, counter: int, max: int) -> None:
        '''
        calibrates the bias from the accelerometer to know how fast the wombat is going towards the x-axis(accelerometer is not yet in use though)

        Args:
            counter (int): the number where it is at the moment
            max (int): how many caLibrations there are (to show it on the screen and for debugging usage)

        Returns:
            None
        '''
        i: int = 0
        avg: float = 0
        time: int = 8000
        while i < time:
            avg += k.accel_x()
            k.msleep(1)
            i += 1
        self.bias_accel_x = avg / time
        log(f'{counter}/{max} - ACCEL X CALIBRATED')

    def calibrate_accel_y(self, counter: int, max: int) -> None:
        '''
        calibrates the bias from the accelerometer to know how fast the wombat is going towards the y-axis(accelerometer is not yet in use though)

        Args:
            counter (int): the number where it is at the moment
            max (int): how many caLibrations there are (to show it on the screen and for debugging usage)

        Returns:
            None
        '''
        i: int = 0
        avg: float = 0
        time: int = 8000
        while i < time:
            avg += k.accel_y()
            k.msleep(1)
            i += 1
        self.bias_accel_y = avg / time
        log(f'{counter}/{max} - ACCEL Y CALIBRATED')

    # ================== GET / OVERWRITE BIAS ==================

    def get_bias_gyro_z(self, calibrated: bool = False) -> float:
        '''
        Getting the average bias from the bias_gyro_z.txt file

        Args:
            calibrated (bool, optional): Writing to the file bias_gyro_z.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            Average of the bias_gyro_z.txt file (optionally with the recent calibrated bias as well)
        '''
        avg = 0
        file_name = 'bias_gyro_z.txt'
        try:
            with open(file_name, "r") as f:
                temp_bias = f.read()
                if calibrated:
                    avg = (float(temp_bias) + bias_gyro_z) / 2
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
        file_name = 'bias_gyro_y.txt'
        try:
            with open(file_name, "r") as f:
                temp_bias = f.read()
                if calibrated:
                    avg = (float(temp_bias) + bias_gyro_y) / 2
                    file_Manager.writer(file_name, 'w', avg)
                else:
                    avg = float(temp_bias)
            return avg
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def get_bias_accel_x(self, calibrated: bool = False) -> float:
        '''
        Getting the average bias from the bias_accel_x.txt file

        Args:
            calibrated (bool, optional): Writing to the file bias_accel_x.txt and getting the most recent bias with the last average bias (True) or getting the last average bias only (False / optional)


        Returns:
            Average of the bias_accel_x.txt file (optionally with the recent calibrated bias as well)
        '''
        avg = 0
        file_name = 'bias_accel_x.txt'
        try:
            with open(file_name, "r") as f:
                temp_bias = f.read()
                if calibrated:
                    avg = (float(temp_bias) + bias_accel_x) / 2
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
        file_name = 'bias_accel_y.txt'
        try:
            with open(file_name, "r") as f:
                temp_bias = f.read()
                if calibrated:
                    avg = (float(temp_bias) + bias_accel_y) / 2
                    file_Manager.writer(file_name, 'w', avg)
                else:
                    avg = float(temp_bias)
            return avg
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    # ======================== PUBLIC METHODS =======================

    def drive_side(self, direction: str, millis: int, speed: int = self.ds_speed) -> None:
        '''
        drive sideways for as long as you want to (in millis)

        Args:
            direction (str): "left" or "right", depending on where you want to go
            millis (int): for how long you want to drive sideways
            speed (int, optional): the speed it is going to drive sideways (default: ds_speed)

        Returns:
            None
        '''
        startTime: float = k.seconds()
        theta = 0
        t = 10
        adjuster = 100
        lower_theta = 500
        higher_theta = 5000
        speed = abs(speed)
        if direction == 'right':
            while k.seconds() - startTime < (millis) / 1000:
                if theta < lower_theta and theta > -lower_theta:
                    k.mav(self.port_wheel_fl, speed)
                    k.mav(self.port_wheel_fr, -speed)
                    k.mav(self.port_wheel_bl, -speed)
                    k.mav(self.port_wheel_br, speed)
                elif theta < -lower_theta and theta > -higher_theta:
                    k.mav(self.port_wheel_fl, speed + adjuster)
                    k.mav(self.port_wheel_fr, -speed)
                    k.mav(self.port_wheel_bl, -speed + adjuster)
                    k.mav(self.port_wheel_br, speed - adjuster)
                elif theta > lower_theta and theta < higher_theta:
                    k.mav(self.port_wheel_fl, speed - adjuster)
                    k.mav(self.port_wheel_fr, -speed)
                    k.mav(self.port_wheel_bl, -speed + adjuster)
                    k.mav(self.port_wheel_br, speed - adjuster)
                elif theta < -higher_theta:
                    k.ao()
                    k.mav(self.port_wheel_fr, 3600)
                    k.mav(self.port_wheel_br, -3600)
                    theta = 0
                elif theta > higher_theta:
                    k.ao()
                    k.mav(self.port_wheel_fl, -3600)
                    k.mav(self.port_wheel_bl, -3600)
                    theta = 0

                k.msleep(t)
                theta += (k.gyro_y() - self.bias_gyro_y) * 3

        elif direction == 'left':
            while k.seconds() - startTime < (millis) / 1000:
                if theta < lower_theta and theta > -lower_theta:
                    k.mav(self.port_wheel_fl, -speed)
                    k.mav(self.port_wheel_fr, speed)
                    k.mav(self.port_wheel_bl, speed)
                    k.mav(self.port_wheel_br, -speed)
                elif theta < -lower_theta and theta > -higher_theta:
                    k.mav(self.port_wheel_fl, -speed)
                    k.mav(self.port_wheel_fr, speed - adjuster)
                    k.mav(self.port_wheel_bl, speed + adjuster)
                    k.mav(self.port_wheel_br, -speed - adjuster)
                elif theta > lower_theta and theta < higher_theta:
                    k.mav(self.port_wheel_fl, -speed + adjuster)
                    k.mav(self.port_wheel_fr, speed)
                    k.mav(self.port_wheel_bl, speed - adjuster)
                    k.mav(self.port_wheel_br, -speed + adjuster)
                elif theta < -higher_theta:
                    k.ao()
                    k.mav(self.port_wheel_fr, -3600)
                    k.mav(self.port_wheel_br, 3600)
                    theta = 0
                elif theta > higher_theta:
                    k.ao()
                    k.mav(self.port_wheel_fl, 3600)
                    k.mav(self.port_wheel_bl, 3600)
                    theta = 0

                k.msleep(t)
                theta += (k.gyro_y() - self.bias_gyro_y) * 3
        else:
            log('Only "right" and "left" are valid commands for the direction!', in_exception=True)
            raise Exception('drive_side() Exception: Only "right" and "left" are valid commands for the direction!')

        k.ao()

    def drive_straight(self, millis: int, speed: int = self.ds_speed) -> None:
        '''
        drive straight for as long as you want to (in millis)

        Args:
            millis (int): for how long you want to drive straight
            speed (int, optional): the speed it is going to drive straight (default: ds_speed)

        Returns:
            None
        '''
        startTime: float = k.seconds()
        theta = 0
        adjuster = 1600
        self.break_all_motors()
        while k.seconds() - startTime < (millis) / 1000:
            if theta < 1000 and theta > -1000:
                k.mav(self.port_wheel_fl, speed)
                k.mav(self.port_wheel_fr, speed)
                k.mav(self.port_wheel_bl, speed)
                k.mav(self.port_wheel_br, speed)
            elif theta > 1000:
                k.mav(self.port_wheel_fl, speed - adjuster)
                k.mav(self.port_wheel_fr, speed + adjuster)
                k.mav(self.port_wheel_bl, speed - adjuster)
                k.mav(self.port_wheel_br, speed + adjuster)
            else:
                k.mav(self.port_wheel_fl, speed + adjuster)
                k.mav(self.port_wheel_fr, speed - adjuster)
                k.mav(self.port_wheel_bl, speed + adjuster)
                k.mav(self.port_wheel_br, speed - adjuster)
            k.msleep(10)
            theta += (k.gyro_z() - self.bias_gyro_z) * 1.5
        k.ao()

    def drive_diagonal(self, end: str, side: str, millis: int, speed: int = self.ds_speed) -> None:
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
        if end != 'front' and end != 'back':
            log('Only "front" or "back" are valid options for the "end" parameter', in_exception=True)
            raise Exception(
                'drive_diagonal() Exception: Only "front" or "back" are valid options for the "end" parameter')

        if side != 'right' and side != 'left':
            log('Only "right" or "left" are valid options for the "side" parameter', in_exception=True)
            raise Exception(
                'drive_diagonal() Exception: Only "right" or "left" are valid options for the "side" parameter')

        points = 0
        if end == 'front':
            points += 1
        if side == 'right':
            points += 1

        startTime: float = k.seconds()
        theta_z = 0
        adjuster = 1350
        if side == 'left':
            adjuster = -adjuster
        speed = abs(speed)
        ports_left = self.port_wheel_fr, self.port_wheel_bl
        ports_right = self.port_wheel_fl, self.port_wheel_br
        ports = ports_left
        if side == 'right':
            ports = ports_right
        if end == 'back':
            speed = -speed
            if self.port_wheel_fr in ports:  # its associated to the left
                ports = ports_right
            else:
                ports = ports_left

        if points == 2 or points == 0:
            while k.seconds() - startTime < (millis) / 1000:
                if theta_z < -1200:
                    k.mav(ports[0], speed)
                    k.mav(ports[1], speed - adjuster)
                elif theta_z > 1200:
                    k.mav(ports[0], speed)
                    k.mav(ports[1], speed - adjuster)
                else:
                    k.mav(ports[0], speed)
                    k.mav(ports[1], speed)
                k.msleep(10)
                theta_z += (k.gyro_z() - self.bias_gyro_z) * 1.5
        else:
            # p[0] -> fr
            t = 10
            while k.seconds() - startTime < (millis) / 1000:
                if t == 200:
                    t = 10
                    k.ao()
                if theta_z > 4000:
                    t = 200
                    theta_z = 0
                    k.mav(self.port_wheel_br, speed - speed // 2)
                elif theta_z < -4000:
                    t = 200
                    theta_z = 0
                    k.mav(self.port_wheel_fl, -speed + speed // 2)
                elif theta_z < -800:
                    k.mav(ports[0], speed - adjuster)
                    k.mav(ports[1], speed)
                elif theta_z > 800:
                    k.mav(ports[0], speed - adjuster)
                    k.mav(ports[1], speed)
                else:
                    k.mav(ports[0], speed)
                    k.mav(ports[1], speed)
                k.msleep(t)
                theta_z += (k.gyro_z() - self.bias_gyro_z) * 1.5

        k.ao()

    def turn_degrees_far(self, direction: str, degree: int) -> None:
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
            raise Exception(
                'turn_degrees_far() Exception: Only "right" or "left" are valid options for the "direction" parameter')

        if degree > 180 and degree < 0:
            log('Only values from range 0 - 180 are valid for the "degree" parameter', in_exception=True)
            raise Exception(
                'turn_degrees_far() Exception: Only values from range 0 - 180 are valid for the "degree" parameter')

        div = 180 / degree
        value = self.ONEEIGHTY_DEGREES_SECS / div
        if degree <= 90:
            div = 90 / degree
            value = self.NINETY_DEGREES_SECS / div

        if direction == 'right':
            k.mav(self.port_wheel_fl, 3600)
            k.mav(self.port_wheel_bl, 3600)
            time.sleep(2 * value)
        elif direction == 'left':
            k.mav(self.port_wheel_fr, 3600)
            k.mav(self.port_wheel_br, 3600)
            time.sleep(2 * value)

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
            raise Exception(
                'turn_degrees() Exception: Only "right" or "left" are valid options for the "direction" parameter')

        if degree > 180 and degree < 1:
            log('Only values from range 1 - 180 are valid for the "degree" parameter', in_exception=True)
            raise Exception(
                'turn_degrees_far() Exception: Only values from range 1 - 180 are valid for the "degree" parameter')

        div = 180 / degree
        value = self.ONEEIGHTY_DEGREES_SECS / div
        if degree <= 90:
            div = 90 / degree
            value = self.NINETY_DEGREES_SECS / div

        if direction == 'right':
            k.mav(self.port_wheel_fl, 3600)
            k.mav(self.port_wheel_fr, -3600)
            k.mav(self.port_wheel_bl, 3600)
            k.mav(self.port_wheel_br, -3600)
            time.sleep(value)
        elif direction == 'left':
            k.mav(self.port_wheel_fl, -3600)
            k.mav(self.port_wheel_fr, 3600)
            k.mav(self.port_wheel_bl, -3600)
            k.mav(self.port_wheel_br, 3600)
            time.sleep(value)
        k.ao()

    def drive_side_til_mm_found(self, mm_to_object: int, direction: str, speed: int = self.ds_speed) -> None:
        '''
        turn the amount of degrees given, to take a turn with basically only two, resulting in a turn not on the spot

        Args:
            mm_to_object (int): the distance (in mm) between the distance sensor and the object in front of the sensor
            direction (str): "left" or "right", depending on where you want to go
            speed (int, optional): the speed it is going to drive straight (default: ds_speed)

        Returns:
            None
        '''
        if direction != 'right' and direction != 'left':
            log('Only "right" or "left" are valid options for the "direction" parameter', in_exception=True)
            raise Exception(
                'drive_side_til_mm_found() Exception: Only "right" or "left" are valid options for the "direction" parameter')

        th_distance_waiter = threading.Thread(target=wait_til_distance_reached, args=(mm_to_object, True))
        theta = 0
        t = 10
        adjuster = 400
        th_distance_waiter.start()
        if direction == 'right':
            while th_distance_waiter.is_alive():
                if theta < 800 and theta > -800:
                    k.mav(self.port_wheel_fl, speed)
                    k.mav(self.port_wheel_fr, -speed)
                    k.mav(self.port_wheel_bl, -speed)
                    k.mav(self.port_wheel_br, speed)
                elif theta < 10000:
                    k.ao()
                    k.mav(self.port_wheel_fr, 3600)
                    k.mav(self.port_wheel_br, -3600)
                    theta = 0
                elif theta > 10000:
                    k.ao()
                    k.mav(self.port_wheel_fl, -3600)
                    k.mav(self.port_wheel_bl, -3600)
                    theta = 0
                elif theta < 800:
                    k.mav(self.port_wheel_fl, speed + adjuster)
                    k.mav(self.port_wheel_fr, -speed)
                    k.mav(self.port_wheel_bl, -speed + adjuster)
                    k.mav(self.port_wheel_br, speed - adjuster)
                else:
                    k.mav(self.port_wheel_fl, speed - adjuster)
                    k.mav(self.port_wheel_fr, -speed)
                    k.mav(self.port_wheel_bl, -speed + adjuster)
                    k.mav(self.port_wheel_br, speed - adjuster)

                k.msleep(t)
                theta += (k.gyro_y() - self.bias_gyro_y) * 3


        elif direction == 'left':
            while th_distance_waiter.is_alive():
                if theta < 800 and theta > -800:
                    k.mav(self.port_wheel_fl, -speed)
                    k.mav(self.port_wheel_fr, speed)
                    k.mav(self.port_wheel_bl, speed)
                    k.mav(self.port_wheel_br, -speed)
                elif theta < 10000:
                    k.ao()
                    k.mav(self.port_wheel_fr, -3600)
                    k.mav(self.port_wheel_br, 3600)
                    theta = 0
                elif theta > 10000:
                    k.ao()
                    k.mav(self.port_wheel_fl, 3600)
                    k.mav(self.port_wheel_bl, 3600)
                    theta = 0
                elif theta < 800:
                    k.mav(self.port_wheel_fl, -speed)
                    k.mav(self.port_wheel_fr, speed - adjuster)
                    k.mav(self.port_wheel_bl, speed + adjuster)
                    k.mav(self.port_wheel_br, -speed - adjuster)
                else:
                    k.mav(self.port_wheel_fl, -speed + adjuster)
                    k.mav(self.port_wheel_fr, speed)
                    k.mav(self.port_wheel_bl, speed - adjuster)
                    k.mav(self.port_wheel_br, -speed + adjuster)
                k.msleep(t)
                theta += (k.gyro_y() - self.bias_gyro_y) * 3

        self.break_all_motors()

    def drive_til_distance(self, mm_to_object: int, speed: int = self.ds_speed) -> None:
        # distance in mm
        '''
        drive straight as long as the object in front of the distance sensor (in mm) is not in reach

        Args:
            mm_to_object (int): the distance (in mm) between the distance sensor and the object in front of the sensor
            speed (int, optional): the speed it is going to drive straight (default: ds_speed)

        Returns:
            None
        '''
        if mm_to_object > 800 or mm_to_object < 10:
            log('You can only put a value in range of 10 - 800 for the distance parameter!', in_exception=True)
            raise Exception(
                'drive_til_distance() Exception: You can only put a value in range of 10 - 800 for the distance parameter!')

        self.check_instances_buttons_back()

        self.isClose = False
        theta = 0.0
        adjuster = 1600
        if self.distance_sensorcurrent_value() > 1800:
            while self.distance_sensor.current_value() > 1800 and (
                    not self.button_bl.is_Pressed() and not self.button_br.is_Pressed()):
                if theta < 1000 and theta > -1000:  # left
                    k.mav(self.port_wheel_fl, -speed)
                    k.mav(self.port_wheel_fr, -speed)
                    k.mav(self.port_wheel_bl, -speed)
                    k.mav(self.port_wheel_br, -speed)
                elif theta > 1000:  # right
                    k.mav(self.port_wheel_fl, -speed - adjuster)
                    k.mav(self.port_wheel_fr, -speed + adjuster)
                    k.mav(self.port_wheel_bl, -speed - adjuster)
                    k.mav(self.port_wheel_br, -speed + adjuster)
                else:
                    k.mav(self.port_wheel_fl, -speed + adjuster)
                    k.mav(self.port_wheel_fr, -speed - adjuster)
                    k.mav(self.port_wheel_bl, -speed + adjuster)
                    k.mav(self.port_wheel_br, -speed - adjuster)
                k.msleep(10)
                theta += (k.gyro_z() - self.bias_gyro_z) * 1.5
            if theta != 0.0:
                # break_all_motors()
                k.mav(self.port_wheel_fl, speed)
                k.mav(self.port_wheel_fr, speed)
                k.mav(self.port_wheel_bl, speed)
                k.mav(self.port_wheel_br, speed)
                k.msleep(20)
                k.ao()
                k.msleep(100)
        else:
            val = mm_to_object
            if mm_to_object <= 200:
                val = 200

            far_sensor_values = [500, 530, 600, 670, 715, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700,
                                 1800,
                                 1900,
                                 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900]
            far_distances_mm = [800, 700, 600, 580, 540, 480, 400, 360, 320, 285, 260, 235, 220, 205, 190, 180, 170,
                                160, 150, 140, 135, 130, 125, 120, 115, 110, 100]
            combination = dict(zip(far_distances_mm, far_sensor_values))
            next_step = min(combination, key=lambda x: abs(x - val))
            next_value = combination[next_step]

            def distance_stopper():
                tolerance = val / 10
                try:
                    lookup = interp1d(far_sensor_values, far_distances_mm, kind='linear', fill_value="extrapolate")
                except Exception as e:
                    log(str(e), important=True, in_exception=True)

                def get_distance_from_sensor(sensor_value):
                    return float(lookup(sensor_value))

                def is_target_distance_reached():
                    value = self.distance_sensor.current_value()
                    dist = get_distance_from_sensor(value)
                    return dist - val < tolerance

                while True:
                    if is_target_distance_reached():
                        self.isClose = True
                        sys.exit()
                        break

            if self.distance_sensor.current_value() < next_value:
                threading.Thread(target=distance_stopper).start()

                while not self.isClose:
                    if theta < 1000 and theta > -1000:
                        k.mav(self.port_wheel_fl, speed)
                        k.mav(self.port_wheel_fr, speed)
                        k.mav(self.port_wheel_bl, speed)
                        k.mav(self.port_wheel_br, speed)
                    elif theta > 1000:
                        k.mav(self.port_wheel_fl, speed - adjuster)
                        k.mav(self.port_wheel_fr, speed + adjuster)
                        k.mav(self.port_wheel_bl, speed - adjuster)
                        k.mav(self.port_wheel_br, speed + adjuster)
                    else:
                        k.mav(self.port_wheel_fl, speed + adjuster)
                        k.mav(self.port_wheel_fr, speed - adjuster)
                        k.mav(self.port_wheel_bl, speed + adjuster)
                        k.mav(self.port_wheel_br, speed - adjuster)

                    k.msleep(5)
                    theta += (k.gyro_z() - self.bias_gyro_z) * 1.5

                self.break_all_motors()
                k.ao()

        if mm_to_object <= 200:
            counter = 200
            while counter > mm_to_object:
                counter -= 1
                if theta < 1000 and theta > -1000:
                    k.mav(self.port_wheel_fl, speed)
                    k.mav(self.port_wheel_fr, speed)
                    k.mav(self.port_wheel_bl, speed)
                    k.mav(self.port_wheel_br, speed)
                elif theta > 1000:
                    k.mav(self.port_wheel_fl, speed - adjuster)
                    k.mav(self.port_wheel_fr, speed + adjuster)
                    k.mav(self.port_wheel_bl, speed - adjuster)
                    k.mav(self.port_wheel_br, speed + adjuster)
                else:
                    k.mav(self.port_wheel_fl, speed + adjuster)
                    k.mav(self.port_wheel_fr, speed - adjuster)
                    k.mav(self.port_wheel_bl, speed + adjuster)
                    k.mav(self.port_wheel_br, speed - adjuster)
                time.sleep(0.0023)
                theta += (k.gyro_z() - self.bias_gyro_z) * 1.5

            self.break_all_motors()

    def break_motor(self, *args) -> None:
        '''
        immediately stop the motor(s) of the given port

        Args:
            *args (int): All of the desired (motor) ports which should be stopped

        Returns:
            None
        '''
        try:
            for port in args:
                k.freeze(port)
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def break_all_motors(self) -> None:
        '''
        immediately stop all motors

        Args:
            None

        Returns:
            None
        '''
        k.freeze(self.port_wheel_fl)
        k.freeze(self.port_wheel_fr)
        k.freeze(self.port_wheel_bl)
        k.freeze(self.port_wheel_br)

    def wait_motor_done(self, *args) -> bool:
        '''
        Waits until all specified motors have completed their rotations.

        Args:
            *args (int): Ports of the motors to wait for.

        Returns:
            bool: True when all specified motors are done.
        '''
        try:
            pending = set(args)

            while pending:
                for motor in list(pending):
                    if k.get_motor_done(motor):
                        pending.remove(motor)

            return True

        except Exception as e:
            log(str(e), important=True, in_exception=True)
            return False

    def shake_side(self, times: int, millis: int = 90) -> None:
        '''
        drive right and left in small steps

        Args:
            times (int): how often it should shake itself
            millis (int, optional): how long it should drive left and right (default: 90)

        Returns:
            None
        '''
        for i in range(times):
            self.drive_side('right', millis)
            self.wait_motor_done(self.port_wheel_fl, self.port_wheel_fr, self.port_wheel_bl, self.port_wheel_br)
            self.drive_side('left', millis)
            self.wait_motor_done(self.port_wheel_fl, self.port_wheel_fr, self.port_wheel_bl, self.port_wheel_br)
            if i % 2 == 0:  # this is since the robot is driving straight a little bit after some time
                self.drive_straight(50, -self.ds_speed)
                self.break_all_motors()

    def align_drive_front(self, drive_bw: bool = True) -> None:
        '''
        aligning front by bumping into something, so both buttons on the front will be pressed. If there's an error by pressing the buttons, a fail save will occur. If at will it also drive backwards a little bit to be able to turn after it bumped into something

        Args:
            drive_bw (bool, optional): If you desire to drive back a little bit (default: True) -> (but sometimes you want to stay aligned at the object)

        Returns:
            None

        '''
        self.check_instances_buttons_front()
        startTime: float = k.seconds()
        while k.seconds() - startTime < (2000) / 1000:
            if self.button_fl.is_Pressed() and self.button_fr.is_Pressed():
                break
            elif self.button_fl.is_Pressed():
                k.ao()
                k.mav(self.port_wheel_fl, -self.ds_speed // 4)
                k.mav(self.port_wheel_fr, self.ds_speed // 2)
            elif self.button_fr.is_Pressed():
                k.ao()
                k.mav(self.port_wheel_fr, -self.ds_speed // 4)
                k.mav(self.port_wheel_fl, self.ds_speed // 2)
            else:
                k.mav(self.port_wheel_fr, self.ds_speed // 2)
                k.mav(self.port_wheel_fl, self.ds_speed // 2)
                k.mav(self.port_wheel_br, self.ds_speed // 2)
                k.mav(self.port_wheel_bl, self.ds_speed // 2)
        if drive_bw:
            k.mav(self.port_wheel_fr, -self.ds_speed)
            k.mav(self.port_wheel_fl, -self.ds_speed)
            k.mav(self.port_wheel_br, -self.ds_speed)
            k.mav(self.port_wheel_bl, -self.ds_speed)
            k.msleep(100)
        k.ao()

    def align_drive_back(self, drive_fw: bool = True) -> None:
        '''
        aligning back by bumping into something, so both buttons on the back will be pressed. If there's an error by pressing the buttons, a fail save will occur. If at will it also drive forwards a little bit to be able to turn after it bumped into something

        Args:
            drive_fw (bool, optional): If you desire to drive forward a little bit (default: True) -> (but sometimes you want to stay aligned at the object)

        Returns:
            None
        '''
        self.check_instances_buttons_back()
        startTime: float = k.seconds()
        while k.seconds() - startTime < (2000) / 1000:
            if self.button_br.is_Pressed() and self.button_bl.is_Pressed():
                break
            elif self.button_br.is_Pressed():
                k.ao()
                k.mav(self.port_wheel_bl, -self.ds_speed // 2)
                k.mav(self.port_wheel_br, self.ds_speed // 4)
            elif self.button_bl.is_Pressed():
                k.ao()
                k.mav(self.port_wheel_br, -self.ds_speed // 2)
                k.mav(self.port_wheel_bl, self.ds_speed // 4)
            else:
                k.mav(self.port_wheel_fr, -self.ds_speed // 2)
                k.mav(self.port_wheel_fl, -self.ds_speed // 2)
                k.mav(self.port_wheel_br, -self.ds_speed // 2)
                k.mav(self.port_wheel_bl, -self.ds_speed // 2)
        k.ao()
        k.msleep(20)
        if drive_fw:
            k.mav(self.port_wheel_fr, self.ds_speed)
            k.mav(self.port_wheel_fl, self.ds_speed)
            k.mav(self.port_wheel_br, self.ds_speed)
            k.mav(self.port_wheel_bl, self.ds_speed)
            k.msleep(50)
            k.ao()

    def drive_side_condition_analog(self, direction: str, Instance, condition: str, value: int, millis: int = 9999999,
                                    speed: int = self.ds_speed) -> None:
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
        if direction != 'right' and direction != 'left':
            log('Only "right" or "left" are valid arguments for the direction parameter!', in_exception=True)
            raise Exception(
                'drive_side_condition_analog() Exception: Only "right" or "left" are valid arguments for the direction parameter! ')

        startTime: float = k.seconds()
        theta = 0
        t = 10
        adjuster = 100
        lower_theta = 500
        higher_theta = 5000
        speed = abs(speed)
        self.break_all_motors()
        if condition == 'let' or condition == '<=':  # let -> less or equal than
            while (Instance.current_value() <= value) and (k.seconds() - startTime < (millis) / 1000):
                if direction == 'right':
                    if theta < lower_theta and theta > -lower_theta:
                        k.mav(self.port_wheel_fl, speed)
                        k.mav(self.port_wheel_fr, -speed)
                        k.mav(self.port_wheel_bl, -speed)
                        k.mav(self.port_wheel_br, speed)
                    elif theta < -lower_theta and theta > -higher_theta:
                        k.mav(self.port_wheel_fl, speed + adjuster)
                        k.mav(self.port_wheel_fr, -speed)
                        k.mav(self.port_wheel_bl, -speed + adjuster)
                        k.mav(self.port_wheel_br, speed - adjuster)
                    elif theta > lower_theta and theta < higher_theta:
                        k.mav(self.port_wheel_fl, speed - adjuster)
                        k.mav(self.port_wheel_fr, -speed)
                        k.mav(self.port_wheel_bl, -speed + adjuster)
                        k.mav(self.port_wheel_br, speed - adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fr, 3600)
                        k.mav(self.port_wheel_br, -3600)
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fl, -3600)
                        k.mav(self.port_wheel_bl, -3600)
                        theta = 0

                    k.msleep(t)
                    theta += (k.gyro_y() - self.bias_gyro_y) * 3


                elif direction == 'left':
                    if theta < lower_theta and theta > -lower_theta:
                        k.mav(self.port_wheel_fl, -speed)
                        k.mav(self.port_wheel_fr, speed)
                        k.mav(self.port_wheel_bl, speed)
                        k.mav(self.port_wheel_br, -speed)
                    elif theta < -lower_theta and theta > -lower_theta:
                        k.mav(self.port_wheel_fl, -speed)
                        k.mav(self.port_wheel_fr, speed - adjuster)
                        k.mav(self.port_wheel_bl, speed + adjuster)
                        k.mav(self.port_wheel_br, -speed - adjuster)
                    elif theta > lower_theta and theta < higher_theta:
                        k.mav(self.port_wheel_fl, -speed + adjuster)
                        k.mav(self.port_wheel_fr, speed)
                        k.mav(self.port_wheel_bl, speed - adjuster)
                        k.mav(self.port_wheel_br, -speed + adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fr, -3600)
                        k.mav(self.port_wheel_br, 3600)
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fl, 3600)
                        k.mav(self.port_wheel_bl, 3600)
                        theta = 0
                    k.msleep(t)
                    theta += (k.gyro_y() - self.bias_gyro_y) * 3


        elif condition == 'het' or condition == '>=':  # het -> higher or equal than
            while (Instance.current_value() >= value) and (k.seconds() - startTime < (millis) / 1000):
                if direction == 'right':
                    if theta < lower_theta and theta > -lower_theta:
                        k.mav(self.port_wheel_fl, speed)
                        k.mav(self.port_wheel_fr, -speed)
                        k.mav(self.port_wheel_bl, -speed)
                        k.mav(self.port_wheel_br, speed)
                    elif theta < -lower_theta and theta > -higher_theta:
                        k.mav(self.port_wheel_fl, speed + adjuster)
                        k.mav(self.port_wheel_fr, -speed)
                        k.mav(self.port_wheel_bl, -speed + adjuster)
                        k.mav(self.port_wheel_br, speed - adjuster)
                    elif theta > lower_theta and theta < higher_theta:
                        k.mav(self.port_wheel_fl, speed - adjuster)
                        k.mav(self.port_wheel_fr, -speed)
                        k.mav(self.port_wheel_bl, -speed + adjuster)
                        k.mav(self.port_wheel_br, speed - adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fr, 3600)
                        k.mav(self.port_wheel_br, -3600)
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fl, -3600)
                        k.mav(self.port_wheel_bl, -3600)
                        theta = 0

                    k.msleep(t)
                    theta += (k.gyro_y() - self.bias_gyro_y) * 3


                elif direction == 'left':
                    if theta < lower_theta and theta > -lower_theta:
                        k.mav(self.port_wheel_fl, -speed)
                        k.mav(self.port_wheel_fr, speed)
                        k.mav(self.port_wheel_bl, speed)
                        k.mav(self.port_wheel_br, -speed)
                    elif theta < -lower_theta and theta > -higher_theta:
                        k.mav(self.port_wheel_fl, -speed)
                        k.mav(self.port_wheel_fr, speed - adjuster)
                        k.mav(self.port_wheel_bl, speed + adjuster)
                        k.mav(self.port_wheel_br, -speed - adjuster)
                    elif theta > lower_theta and theta < higher_theta:
                        k.mav(self.port_wheel_fl, -speed + adjuster)
                        k.mav(self.port_wheel_fr, speed)
                        k.mav(self.port_wheel_bl, speed - adjuster)
                        k.mav(self.port_wheel_br, -speed + adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fr, -3600)
                        k.mav(self.port_wheel_br, 3600)
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fl, 3600)
                        k.mav(self.port_wheel_bl, 3600)
                        theta = 0
                    k.msleep(t)
                    theta += (k.gyro_y() - self.bias_gyro_y) * 3

        elif condition == 'ht' or condition == '>':  # ht -> higher than
            while (Instance.current_value() > value) and (k.seconds() - startTime < (millis) / 1000):
                if direction == 'right':
                    if theta < lower_theta and theta > -lower_theta:
                        k.mav(self.port_wheel_fl, speed)
                        k.mav(self.port_wheel_fr, -speed)
                        k.mav(self.port_wheel_bl, -speed)
                        k.mav(self.port_wheel_br, speed)
                    elif theta < -lower_theta and theta > -higher_theta:
                        k.mav(self.port_wheel_fl, speed + adjuster)
                        k.mav(self.port_wheel_fr, -speed)
                        k.mav(self.port_wheel_bl, -speed + adjuster)
                        k.mav(self.port_wheel_br, speed - adjuster)
                    elif theta > lower_theta and theta < higher_theta:
                        k.mav(self.port_wheel_fl, speed - adjuster)
                        k.mav(self.port_wheel_fr, -speed)
                        k.mav(self.port_wheel_bl, -speed + adjuster)
                        k.mav(self.port_wheel_br, speed - adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fr, 3600)
                        k.mav(self.port_wheel_br, -3600)
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fl, -3600)
                        k.mav(self.port_wheel_bl, -3600)
                        theta = 0

                    k.msleep(t)
                    theta += (k.gyro_y() - self.bias_gyro_y) * 3


                elif direction == 'left':
                    if theta < lower_theta and theta > -lower_theta:
                        k.mav(self.port_wheel_fl, -speed)
                        k.mav(self.port_wheel_fr, speed)
                        k.mav(self.port_wheel_bl, speed)
                        k.mav(self.port_wheel_br, -speed)
                    elif theta < -lower_theta and theta > -higher_theta:
                        k.mav(self.port_wheel_fl, -speed)
                        k.mav(self.port_wheel_fr, speed - adjuster)
                        k.mav(self.port_wheel_bl, speed + adjuster)
                        k.mav(self.port_wheel_br, -speed - adjuster)
                    elif theta > lower_theta and theta < higher_theta:
                        k.mav(self.port_wheel_fl, -speed + adjuster)
                        k.mav(self.port_wheel_fr, speed)
                        k.mav(self.port_wheel_bl, speed - adjuster)
                        k.mav(self.port_wheel_br, -speed + adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fr, -3600)
                        k.mav(self.port_wheel_br, 3600)
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fl, 3600)
                        k.mav(self.port_wheel_bl, 3600)
                        theta = 0
                    k.msleep(t)
                    theta += (k.gyro_y() - self.bias_gyro_y) * 3

        elif condition == 'lt' or condition == '<':  # lt -> less than
            while (Instance.current_value() < value) and (k.seconds() - startTime < (millis) / 1000):
                if direction == 'right':
                    if theta < lower_theta and theta > -lower_theta:
                        k.mav(self.port_wheel_fl, speed)
                        k.mav(self.port_wheel_fr, -speed)
                        k.mav(self.port_wheel_bl, -speed)
                        k.mav(self.port_wheel_br, speed)
                    elif theta < -lower_theta and theta > -higher_theta:
                        k.mav(self.port_wheel_fl, speed + adjuster)
                        k.mav(self.port_wheel_fr, -speed)
                        k.mav(self.port_wheel_bl, -speed + adjuster)
                        k.mav(self.port_wheel_br, speed - adjuster)
                    elif theta > lower_theta and theta < higher_theta:
                        k.mav(self.port_wheel_fl, speed - adjuster)
                        k.mav(self.port_wheel_fr, -speed)
                        k.mav(self.port_wheel_bl, -speed + adjuster)
                        k.mav(self.port_wheel_br, speed - adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fr, 3600)
                        k.mav(self.port_wheel_br, -3600)
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fl, -3600)
                        k.mav(self.port_wheel_bl, -3600)
                        theta = 0

                    k.msleep(t)
                    theta += (k.gyro_y() - self.bias_gyro_y) * 3


                elif direction == 'left':
                    if theta < lower_theta and theta > -lower_theta:
                        k.mav(self.port_wheel_fl, -speed)
                        k.mav(self.port_wheel_fr, speed)
                        k.mav(self.port_wheel_bl, speed)
                        k.mav(self.port_wheel_br, -speed)
                    elif theta < -lower_theta and theta > -higher_theta:
                        k.mav(self.port_wheel_fl, -speed)
                        k.mav(self.port_wheel_fr, speed - adjuster)
                        k.mav(self.port_wheel_bl, speed + adjuster)
                        k.mav(self.port_wheel_br, -speed - adjuster)
                    elif theta > lower_theta and theta < higher_theta:
                        k.mav(self.port_wheel_fl, -speed + adjuster)
                        k.mav(self.port_wheel_fr, speed)
                        k.mav(self.port_wheel_bl, speed - adjuster)
                        k.mav(self.port_wheel_br, -speed + adjuster)
                    elif theta < -higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fr, -3600)
                        k.mav(self.port_wheel_br, 3600)
                        theta = 0
                    elif theta > higher_theta:
                        k.ao()
                        k.mav(self.port_wheel_fl, 3600)
                        k.mav(self.port_wheel_bl, 3600)
                        theta = 0
                    k.msleep(t)
                    theta += (k.gyro_y() - self.bias_gyro_y) * 3
        k.ao()

    def drive_straight_condition_analog(self, Instance, condition: str, value: int, millis: int = 9999999,
                                        speed: int = self.ds_speed) -> None:
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
        self.check_instances_buttons()
        theta = 0.0
        ports = self.button_fl, self.button_fr
        startTime = k.seconds()
        adjuster = 1600
        if speed < 0:
            ports = self.button_bl, self.button_br

        if condition == 'let' or condition == '<=':  # let -> less or equal than
            while (Instance.current_value() <= value) and (not ports[0].is_Pressed() and not ports[
                1].is_Pressed()) and k.seconds() - startTime < millis / 1000:
                if theta < 1000 and theta > -1000:
                    k.mav(self.port_wheel_fl, speed)
                    k.mav(self.port_wheel_fr, speed)
                    k.mav(self.port_wheel_bl, speed)
                    k.mav(self.port_wheel_br, speed)
                elif theta > 1000:
                    k.mav(self.port_wheel_fl, speed - adjuster)
                    k.mav(self.port_wheel_fr, speed + adjuster)
                    k.mav(self.port_wheel_bl, speed - adjuster)
                    k.mav(self.port_wheel_br, speed + adjuster)
                else:
                    k.mav(self.port_wheel_fl, speed + adjuster)
                    k.mav(self.port_wheel_fr, speed - adjuster)
                    k.mav(self.port_wheel_bl, speed + adjuster)
                    k.mav(self.port_wheel_br, speed - adjuster)
                k.msleep(10)
                theta += (k.gyro_z() - self.bias_gyro_z) * 1.5

        elif condition == 'het' or condition == '>=':  # het -> higher or equal than
            while (Instance.current_value() >= value) and (not ports[0].is_Pressed() and not ports[
                1].is_Pressed()) and k.seconds() - startTime < millis / 1000:
                if theta < 1000 and theta > -1000:
                    k.mav(self.port_wheel_fl, speed)
                    k.mav(self.port_wheel_fr, speed)
                    k.mav(self.port_wheel_bl, speed)
                    k.mav(self.port_wheel_br, speed)
                elif theta > 1000:
                    k.mav(self.port_wheel_fl, speed - adjuster)
                    k.mav(self.port_wheel_fr, speed + adjuster)
                    k.mav(self.port_wheel_bl, speed - adjuster)
                    k.mav(self.port_wheel_br, speed + adjuster)
                else:
                    k.mav(self.port_wheel_fl, speed + adjuster)
                    k.mav(self.port_wheel_fr, speed - adjuster)
                    k.mav(self.port_wheel_bl, speed + adjuster)
                    k.mav(self.port_wheel_br, speed - adjuster)
                k.msleep(10)
                theta += (k.gyro_z() - self.bias_gyro_z) * 1.5

        elif condition == 'ht' or condition == '>':  # ht -> higher than
            while (Instance.current_value() > value) and (not ports[0].is_Pressed() and not ports[
                1].is_Pressed() and k.seconds()) - startTime < millis / 1000:
                if theta < 1000 and theta > -1000:
                    k.mav(self.port_wheel_fl, speed)
                    k.mav(self.port_wheel_fr, speed)
                    k.mav(self.port_wheel_bl, speed)
                    k.mav(self.port_wheel_br, speed)
                elif theta > 1000:
                    k.mav(self.port_wheel_fl, speed - adjuster)
                    k.mav(self.port_wheel_fr, speed + adjuster)
                    k.mav(self.port_wheel_bl, speed - adjuster)
                    k.mav(self.port_wheel_br, speed + adjuster)
                else:
                    k.mav(self.port_wheel_fl, speed + adjuster)
                    k.mav(self.port_wheel_fr, speed - adjuster)
                    k.mav(self.port_wheel_bl, speed + adjuster)
                    k.mav(self.port_wheel_br, speed - adjuster)
                k.msleep(10)
                theta += (k.gyro_z() - self.bias_gyro_z) * 1.5

        elif condition == 'lt' or condition == '<':  # lt -> less than
            while (Instance.current_value() < value) and (not ports[0].is_Pressed() and not ports[
                1].is_Pressed()) and k.seconds() - startTime < millis / 1000:
                if theta < 1000 and theta > -1000:
                    k.mav(self.port_wheel_fl, speed)
                    k.mav(self.port_wheel_fr, speed)
                    k.mav(self.port_wheel_bl, speed)
                    k.mav(self.port_wheel_br, speed)
                elif theta > 1000:
                    k.mav(self.port_wheel_fl, speed - adjuster)
                    k.mav(self.port_wheel_fr, speed + adjuster)
                    k.mav(self.port_wheel_bl, speed - adjuster)
                    k.mav(self.port_wheel_br, speed + adjuster)
                else:
                    k.mav(self.port_wheel_fl, speed + adjuster)
                    k.mav(self.port_wheel_fr, speed - adjuster)
                    k.mav(self.port_wheel_bl, speed + adjuster)
                    k.mav(self.port_wheel_br, speed - adjuster)
                k.msleep(10)
                theta += (k.gyro_z() - self.bias_gyro_z) * 1.5
        k.ao()

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
        try:
            if direction != 'vertical' and direction != 'horizontal':
                log('Only "vertical" or "horizontal" are valid options for the "direction" parameter', in_exception=True)
                raise Exception(
                    'align_on_black_line() Exception: Only "vertical" or "horizontal" are valid options for the "direction" parameter')

            if leaning_side != None and leaning_side != 'right' and leaning_side != 'left':
                log('Only "right", "left" or None / nothing are valid options for the "leaning_side" parameter', in_exception=True)
                raise Exception(
                    'align_on_black_line() Exception: Only "right", "left" or None / nothing are valid options for the "leaning_side" parameter')

            if not crossing:
                if not leaning_side or leaning_side == 'right':
                    ports = self.port_wheel_fl, self.port_wheel_fr, self.port_wheel_bl, self.port_wheel_br
                else:
                    ports = self.port_wheel_fr, self.port_wheel_fl, self.port_wheel_br, self.port_wheel_bl
                adjuster = self.ds_speed
                if precise:
                    adjuster = self.ds_speed
                startTime = k.seconds()

                while self.light_sensor_back.sees_White() and self.light_sensor_front.sees_White():
                    if k.seconds() - startTime < self.NINETY_DEGREES_SECS:
                        k.mav(ports[0], self.ds_speed)
                        k.mav(ports[1], -self.ds_speed)
                        k.mav(ports[2], self.ds_speed)
                        k.mav(ports[3], -self.ds_speed)
                    else:
                        k.mav(ports[0], -self.ds_speed)
                        k.mav(ports[1], self.ds_speed)
                        k.mav(ports[2], -self.ds_speed)
                        k.msleep(1)

                self.break_all_motors()

                if not self.light_sensor_back.sees_White():  # hinten ist oben
                    while self.light_sensor_front.sees_White():
                        k.mav(ports[0], -adjuster)  # -750
                        k.mav(ports[1], adjuster)

                if not self.light_sensor_front.sees_White():  # vorne ist oben
                    while self.light_sensor_back.sees_White():
                        k.mav(ports[2], -adjuster)  # -750
                        k.mav(ports[3], adjuster)

                k.ao()
                k.msleep(50)
                if self.light_sensor_front.sees_White():
                    while self.light_sensor_front.sees_White():
                        k.mav(ports[0], -adjuster)
                        k.mav(ports[1], adjuster)

                k.ao()
                k.msleep(10)
                if not self.light_sensor_back.sees_Black() and not self.light_sensor_front.sees_Black():
                    self.drive_side_condition_analog('left', self.light_sensor_front, '<',
                                                     self.light_sensor_front.get_value_black())

            else:
                ports = self.port_wheel_fl, self.port_wheel_fr, self.port_wheel_bl, self.port_wheel_br
                on_line = False
                first_line_hit = None
                line_counter = 0
                line_timer = 0
                line_timer_collector = []

                startTime_front = k.seconds()
                while k.seconds() - startTime_front < self.ONEEIGHTY_DEGREES_SECS * 2 + 0.2:
                    while self.light_sensor_front.sees_Black():
                        on_line = True
                        line_timer += 1
                        k.mav(ports[0], -self.ds_speed)
                        k.mav(ports[1], self.ds_speed)
                        k.mav(ports[2], -self.ds_speed)
                        k.mav(ports[3], self.ds_speed)
                    if on_line:
                        if not first_line_hit:
                            first_line_hit = k.seconds() - startTime_front
                        on_line = False
                        line_counter += 1
                        line_timer_collector.append(line_timer)
                        line_timer = 0
                    k.mav(ports[0], -self.ds_speed)
                    k.mav(ports[1], self.ds_speed)
                    k.mav(ports[2], -self.ds_speed)
                    k.mav(ports[3], self.ds_speed)

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
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], -self.ds_speed)
                            k.mav(ports[2], self.ds_speed)
                            k.mav(ports[3], -self.ds_speed)
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                            k.mav(ports[2], -self.ds_speed)
                            k.mav(ports[3], self.ds_speed)
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], -self.ds_speed)
                        self.break_all_motors()
                    else:
                        d = direct[1]
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], -self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                            k.mav(ports[2], -self.ds_speed)
                            k.mav(ports[3], self.ds_speed)
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                            k.mav(ports[2], self.ds_speed)
                            k.mav(ports[3], -self.ds_speed)
                        self.break_all_motors()
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], -self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                        self.break_all_motors()
                    self.drive_side(d, 5)

                elif line_counter == 3:
                    if dir_picker[0] > dir_picker[1]:
                        d = direct[0]
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], -self.ds_speed)
                            k.mav(ports[2], self.ds_speed)
                            k.mav(ports[3], -self.ds_speed)
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                            k.mav(ports[2], -self.ds_speed)
                            k.mav(ports[3], self.ds_speed)
                        self.break_all_motors()
                        if not self.light_sensor_front.sees_Black():
                            while not self.light_sensor_front.sees_Black():
                                k.mav(ports[0], -self.ds_speed)
                                k.mav(ports[1], self.ds_speed)
                            self.break_all_motors()
                    else:
                        d = direct[1]
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], -self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                            k.mav(ports[2], -self.ds_speed)
                            k.mav(ports[3], self.ds_speed)
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                            k.mav(ports[2], self.ds_speed)
                            k.mav(ports[3], -self.ds_speed)
                        self.break_all_motors()
                        if not self.light_sensor_front.sees_Black():
                            while not self.light_sensor_front.sees_Black():
                                k.mav(ports[0], -self.ds_speed)
                                k.mav(ports[1], self.ds_speed)
                            self.break_all_motors()
                    self.drive_side(d, 5)

                else:  # line_counter == 2
                    if dir_picker[0] < dir_picker[1]:
                        d = direct[0]
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], -self.ds_speed)
                            k.mav(ports[2], self.ds_speed)
                            k.mav(ports[3], -self.ds_speed)
                        self.break_all_motors()
                        while not self.light_sensor_back.sees_Black():
                            k.mav(ports[0], self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                            k.mav(ports[2], -self.ds_speed)
                            k.mav(ports[3], self.ds_speed)
                        self.break_all_motors()
                    else:
                        d = direct[1]
                        while not self.light_sensor_front.sees_Black():
                            k.mav(ports[0], -self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                            k.mav(ports[2], -self.ds_speed)
                            k.mav(ports[3], self.ds_speed)
                        self.break_all_motors()
                    self.drive_side(d, 5)


        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def turn_to_black_line(self, direction: str, millis: int = 80, speed: int = self.ds_speed) -> None:
        '''
        Turn as long as the light sensor (front or back, depends if the speed is positive or negative) sees the black line

        Args:
           direction (str): "right" or "left" - depends on where you want to go
           millis (int, optional): how long (in milliseconds) to drive until the sensor gets checked (no threading is used) (default: 80)
           speed (int, optional): how fast it should turn (default: ds_speed)

        Returns:
           None
        '''
        self.check_instance_light_sensors_middle()
        ports = self.port_wheel_fl, self.port_wheel_fr, self.port_wheel_bl, self.port_wheel_br, self.light_sensor_front
        if speed < 0:
            ports = self.port_wheel_bl, self.port_wheel_br, self.port_wheel_fl, self.port_wheel_fr, self.light_sensor_back

        if direction == 'right':
            while not ports[4].sees_Black():
                k.mav(ports[0], 3600)
                k.mav(ports[1], -3600)
                k.mav(ports[2], 3600)
                k.mav(ports[3], -3600)
                k.msleep(millis)
        elif direction == 'left':
            while not ports[4].sees_Black():
                k.mav(ports[0], -3600)
                k.mav(ports[1], 3600)
                k.mav(ports[2], -3600)
                k.mav(ports[3], 3600)
                k.msleep(millis)
        else:
            log('Only "right" and "left" are valid commands for the direction!', in_exception=True)
            raise Exception(
                'turn_black_line() Exception: Only "right" and "left" are valid commands for the direction!')
        k.ao()

    def align_line(self, onLine: bool, direction: str = None, speed: int = self.ds_speed,
                   maxDuration: int = 100) -> None:
        '''
         ==== NEEDS IMPROVEMENT ====
         If you are anywhere on the black line, you can align yourself on the black line. If you are not on the line, it drives (forwards or backwards, depends if the speed is positive or negative) until the line was found and then aligns as desired.
         Improvement: align backwards, so there is no need to make a 180B0 turn. Would spare you some time.

        Args:
           onLine (bool): Are you already on the black line (True), or do you need to get onto it (False)? If you are not on the line, you need to write the direction you want to face to!
           direction (str): "right" or "left" - depends on where you want to go
           speed (int, optional): how fast it should drive (default: ds_speed)
           maxDuration  (int, optional): the time (in milliseconds) it is allowed to turn in one direction until a failsave gets executed to turn to the other direction (default: 100)

        Returns:
           None
        '''
        self.check_instances_buttons()
        self.check_instance_light_sensors_middle()
        if not onLine:
            if direction != 'left' and direction != 'right':
                log('If the Wombat is not on the line, please tell it which direction it should face when it is on the line ("right" or "left")', in_exception=True)
                raise Exception(
                    'align_line() Exception: If the Wombat is not on the line, please tell it which direction it should face when it is on the line ("right" or "left")')

            ports = self.light_sensor_front, self.light_sensor_back
            if speed < 0:
                ports = self.light_sensor_back, self.light_sensor_front

            self.drive_straight_condition_analog(ports[0], '<=', ports[0].get_value_black(),
                                                 speed=speed)  # Front -> 3500
            start_time = k.seconds()
            self.drive_straight_condition_analog(ports[1], '<=', ports[1].get_value_black(),
                                                 speed=speed)  # Front -> 3300
            end_time = k.seconds()
            k.ao()

            seconds = end_time - start_time
            self.drive_straight((seconds * 1000) // 2 + 100, -speed)  # 100 just a random constant
            self.turn_to_black_line(direction, speed=speed)
        else:
            startTime = k.seconds()
            ports = self.port_wheel_fl, self.port_wheel_fr, self.port_wheel_bl, self.port_wheel_br, self.button_fl, self.button_fr, self.light_sensor_front
            direction = 'right', 'left'
            if speed < 0:
                ports = self.port_wheel_bl, self.port_wheel_br, self.port_wheel_fl, self.port_wheel_fr, self.button_bl, self.button_br, self.light_sensor_back
                direction = 'left', 'right'

            while True:
                k.mav(ports[0], speed)
                k.mav(ports[1], -speed)
                k.mav(ports[2], speed)
                k.mav(ports[3], -speed)
                if (k.seconds() - startTime > maxDuration / 1000):
                    print('TIME OUT', flush=True)
                    k.ao()
                    self.turn_to_black_line(direction[1], 20, speed=speed)
                    break
                if ports[6].sees_Black():  # Front -> 3500
                    k.ao()
                    self.turn_to_black_line(direction[0], 15, speed=speed)
                    break
                if ports[4].is_Pressed() or ports[5].is_Pressed():
                    if speed < 0:
                        self.align_drive_back()
                    else:
                        self.align_drive_front()
                    break
            k.ao()

    def black_line(self, millis: int, speed: int = self.ds_speed) -> None:
        '''
       drive on the black line as long as wished

       Args:
           millis (int): how long you want to follow the black line (in milliseconds)
           speed (int, optional): how fast it should drive straight (default: ds_speed)

       Returns:
           None
       '''
        self.check_instances_buttons()
        self.check_instance_light_sensors_middle()
        startTime: float = k.seconds()
        ports = self.button_fl, self.button_fr, self.light_sensor_front
        if speed < 0:
            ports = self.button_bl, self.button_br, self.light_sensor_back

        while (k.seconds() - startTime < (millis) / 1000) and (not ports[0].is_Pressed() and not ports[1].is_Pressed()):
            self.drive_straight_condition_analog(ports[2], '>=', ports[0].get_value_black(), millis=200,
                                                 speed=speed)  # Front -> 3500
            self.align_line(True, speed=speed)

        if ports[0].is_Pressed() or ports[1].is_Pressed():
            if speed < 0:
                self.align_drive_back()
            else:
                self.align_drive_front()

    def drive_straight_side_checker(self, follow: bool, millis: int, speed: int) -> None:
        # you rather not try to make it drive backwards...
        '''
        Either (try) to align yourself on the black line with the side light sensor and follow the line OR drive until the side light sensor detects black

        Args:
           follow (bool): If you want to stay on the black line with the side light sensor (True and experimental) or drive until the side light sensor detects black (False - in this case just do the drive_straight_condition_analog function to be honest)
           millis (int, optional): how long it is allowed to be in the function (roughly)
           speed (int, optional): how fast it should drive (forwards or backwards) (default: ds_speed)

        Returns:
           None
        '''
        self.check_instances_buttons()
        self.check_instance_light_sensors()
        startTime: float = k.seconds()
        theta = 0.0
        adjuster = 1600
        direction = 'right'
        ports = self.button_fl, self.button_fr, self.light_sensor_front, self.light_sensor_back, self.port_wheel_fl, self.port_wheel_fr, self.port_wheel_bl, self.port_wheel_br
        if speed < 0:
            direction = 'left'
            ports = self.button_bl, self.button_br, self.light_sensor_back, self.light_sensor_front, self.port_wheel_bl, self.port_wheel_br, self.port_wheel_fl, self.port_wheel_fr

        def scenario1():
            while not self.light_sensor_side.sees_Black():
                k.mav(ports[4], speed)
                k.mav(ports[5], -speed)
                k.mav(ports[6], speed)
                k.mav(ports[7], -speed)
            k.ao()
            while not ports[2].sees_Black():
                k.mav(ports[4], -speed)
                k.mav(ports[6], -speed)
            k.ao()
            while ports[2].sees_Black():
                k.mav(ports[4], -speed)
                k.mav(ports[6], -speed)
            k.msleep(100)

        def scenario2():
            k.ao()
            while not self.light_sensor_side.sees_Black():
                k.mav(ports[4], -speed)
                k.mav(ports[6], speed)
                k.mav(ports[7], speed)
            k.msleep(60)
            k.ao()

        def scenario3():
            k.ao()
            while not self.light_sensor_side.sees_Black():
                k.mav(ports[4], -speed)
                k.mav(ports[6], -speed)
            k.ao()
            while self.light_sensor_side.sees_Black():
                k.mav(ports[4], -speed)
                k.mav(ports[6], -speed)
            k.ao()
            while ports[2].sees_Black():
                k.mav(ports[4], speed)
                k.mav(ports[5], speed)
                k.mav(ports[6], speed)
                k.mav(ports[7], -speed)
            k.ao()
            self.drive_side_condition_analog(direction, self.light_sensor_side, '<=', value_light_sensor)
            self.drive_side(direction, 5)

        if not follow:
            while k.seconds() - startTime < (millis) / 1000 and not self.light_sensor_side.sees_Black():
                if theta < 1000 and theta > -1000:
                    k.mav(ports[4], speed)
                    k.mav(ports[5], speed)
                    k.mav(ports[6], speed)
                    k.mav(ports[7], speed)
                elif theta > 1000:
                    k.mav(ports[4], speed - adjuster)
                    k.mav(ports[5], speed + adjuster)
                    k.mav(ports[6], speed - adjuster)
                    k.mav(ports[7], speed + adjuster)
                else:
                    k.mav(ports[4], speed + adjuster)
                    k.mav(ports[5], speed - adjuster)
                    k.mav(ports[6], speed + adjuster)
                    k.mav(ports[7], speed - adjuster)
                k.msleep(10)
                theta += (k.gyro_z() - self.bias_gyro_z) * 1.5
            k.ao()
            k.msleep(1)
        else:
            if speed < 0:
                adjuster = -adjuster
            while k.seconds() - startTime < (millis) / 1000 and (
                    not ports[0].is_Pressed() and not ports[1].is_Pressed()):
                while self.light_sensor_side.sees_Black() and (not ports[0].is_Pressed() and not ports[1].is_Pressed()):
                    if theta < 1000 and theta > -1000:
                        k.mav(ports[4], speed)
                        k.mav(ports[5], speed)
                        k.mav(ports[6], speed)
                        k.mav(ports[7], speed)
                    elif theta > 1000:
                        k.mav(ports[4], speed - adjuster)
                        k.mav(ports[5], speed + adjuster)
                        k.mav(ports[6], speed - adjuster)
                        k.mav(ports[7], speed + adjuster)
                    else:
                        k.mav(ports[4], speed + adjuster)
                        k.mav(ports[5], speed - adjuster)
                        k.mav(ports[6], speed + adjuster)
                        k.mav(ports[7], speed - adjuster)
                    k.msleep(10)
                    theta += (k.gyro_z() - self.bias_gyro_z) * 1.5
                if ports[2].sees_Black():  # front
                    scenario3()
                elif ports[3].sees_Black():  # back
                    scenario2()
                else:
                    while not ports[3].sees_Black():  # Back
                        k.mav(ports[5], -speed)
                        k.mav(ports[7], -speed)
                    if ports[2].sees_Black():  # Front
                        scenario1()
                    elif ports[3].sees_Black():
                        scenario2()
                    else:
                        print('====== crazy kemal (easter egg found, congrats!)=====', flush=True)
                        scenario1()
                k.ao()
                k.msleep(50)

    def scanner_face_object(self, degree: int) -> None:
        '''
       Scan the location for the nearest object and then face the nearest object

       Args:
           degree (int): how much area the scan should cover

       Returns:
           None
       '''
        if degree > 90:
            log('Only a value under 91 is acceptable for the degree!', in_exception=True)
            raise Exception('scan_front() Exception: Only a value under 91 is acceptable for the degree')

        maxRuns = 2
        div = 90 / degree
        amount = degree
        degree = degree / 2  # @TODO -> mit oder ohne bzw passt das ohne
        value = self.NINETY_DEGREES_SECS / div
        ports = self.port_wheel_fl, self.port_wheel_fr, self.port_wheel_bl, self.port_wheel_br
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
            while i < amount:
                newTime = k.seconds()
                avrg = 0
                while k.seconds() - newTime < portion:
                    avrg += self.distance_sensor.current_value()
                build_avrg(i, (avrg * portion) / amount)
                i += 1

        def adjust():
            p = ports[1], ports[0], ports[3], ports[2]
            index = distance_saver.index(max(distance_saver))
            newTime = k.seconds()
            while k.seconds() - newTime < portion * (amount - index):
                k.mav(p[0], 3600)
                k.mav(p[1], -3600)
                k.mav(p[2], 3600)
                k.mav(p[3], -3600)

            self.break_all_motors()

        for i in range(1, maxRuns + 1):
            if i == 2:
                th1 = threading.Thread(target=slicer)
                th1.start()
                value = value * 2
            k.mav(ports[0], 3600)
            k.mav(ports[1], -3600)
            k.mav(ports[2], 3600)
            k.mav(ports[3], -3600)
            time.sleep(value)
            if i % 2 != 0:
                ports = ports[1], ports[0], ports[3], ports[2]
        self.break_all_motors()
        while th1.is_alive():
            continue
        adjust()
        self.wait_motor_done()
