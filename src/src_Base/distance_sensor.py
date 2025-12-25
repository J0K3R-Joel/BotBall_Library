#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-07-28

try:
    import time
    from scipy.interpolate import interp1d
    from analog import Analog  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


BIAS_FOLDER = '/usr/lib/bias_files'
os.makedirs(BIAS_FOLDER, exist_ok=True)

class DistanceSensor(Analog):
    def __init__(self, port: int):
        '''
        Class for the distance sensor. The distance sensor can only see distances from at least 100mm to at most 800mm. Calibrate the distances inside of the driveR!

        Args:
            port (int): the integer value from where it is plugged in (the hardware). E.g.: 5; 2; 0; 4; 1; 3
        '''
        super().__init__(port)
        self.dist_arr_file_name = BIAS_FOLDER + '/distances_arr.txt'
        self._run_lookup()

    # ===================== PRIVATE METHODS =====================
    def _run_lookup(self) -> None:
        '''
        Method for checking if there is already the distance calibrated. If so, then create the lookup for all values

        Args:
            None

        Returns:
            None
        '''
        self.values, self.mm = self.get_distances()

        if not self.values:
            log('If you want to use the distance sensor, then calibrate it inside of the driveR!', important=True)
            return None

        self.lookup = interp1d(self.values, self.mm, kind='linear', fill_value="extrapolate")


    # ===================== GET METHODS =====================
    def get_file_path(self) -> str:
        '''
        Tells you, where the distances are saved at

        Args:
            None

        Returns:
            str: string object of the absolute file path
        '''
        return self.dist_arr_file_name

    def get_distances(self, raises_exception: bool = True) -> tuple:
        '''
        Getting the distances from the distances_arr.txt file

        Args:
            raises_exception (bool, optional): If it should raise an exception, if the file does not exist yet (True) or not (False)

        Returns:
            tuple[list[int], list[int]]:
                (values: list, mm: list)
        '''
        try:
            if not os.path.exists(self.dist_arr_file_name):
                if raises_exception:
                    log(f'{self.dist_arr_file_name} not found. Run calibration first.', in_exception=True)
                    raise FileNotFoundError(f'{self.dist_arr_file_name} not found. Run calibration first.')

            with open(self.dist_arr_file_name, "r") as f:
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
            log(str(e), in_exception=True)

    def get_values(self) -> list:
        '''
        Receive all values which got saved in a file

        Args:
            None

        Returns:
            list[int]: all values which got saved into a file
        '''
        if isinstance(self.values, list):
            return self.values

        self.values, self.mm = self.get_distances()
        return self.values

    def get_mm(self) -> list:
        '''
        Receive all millimeters which got saved in a file

        Args:
            None

        Returns:
            list[int]: every millimeter which got saved into a file
        '''
        if isinstance(self.mm, list):
            return self.mm

        self.values, self.mm = self.get_distances()
        return self.mm

    def get_estimated_mm(self) -> int:
        '''
        Tells you the current estimated distance (in millimeters) from the nearest object in front of the distance sensor. HINT: If you are very very close (<100mm) to the object, then the values become inconsistent. The values reach from at least 100mm to at most (!) 800mm

        Args:
            None

        Returns:
            int: estimated distance in millimeters
        '''
        try:
            return int(self.lookup(self.current_value()))
        except Exception as e:
            log(str(e), important=True, in_exception=True)

    def get_estimated_mm_value(self, millimeters: int) -> int:  # @TODO test this out
        '''
        Receive the estimated value that corresponds to the millimeters

        Args:
            millimeters (int): The millimeters which you want to receive the once remembered value

        Returns:
            int: closest value to the millimeters which got saved
        '''
        if millimeters < self.mm[0] or millimeters > self.mm[-1]:
            log(f'You can only get millimeters between {self.mm[0]} and {self.mm[-1]}!', in_exception=True)
            raise ValueError(f'You can only get millimeters between {self.mm[0]} and {self.mm[-1]}!')

        combination = dict(zip(self.get_mm(), self.get_values()))
        next_step = min(combination, key=lambda x: abs(x - millimeters))
        return combination[next_step]


    # ===================== PUBLIC METHODS =====================
    def higher_lower_distance(self, mm_to_check: int) -> str:
        '''
        Is telling you, if the current (estimated) distance is lower, higher or point on to the parameter you tell this function

        Args:
            mm_to_check (int): the distance (in millimeters) you want to check for farness of the nearest object in front of the sensor

        Returns:
            str:
                1. 'lower' if your distance to check is higher than the (estimated) actual value
                2. 'higher' if your distance to check is lower than the (estimated) actual value
                3. 'point on' if your distance to check matches up with the (estimated) actual value
        '''
        dist = self.get_estimated_mm()

        if dist < mm_to_check:
            return 'lower'
        elif dist > mm_to_check:
            return 'higher'
        return 'point on'

    def distance_in_reach(self, mm_to_check: int, tolerance_percentage: float) -> bool:
        '''
        Tells you, if the current (estimated) distance is in between your desired distance including your tolerance

        Args:
            mm_to_check (int): the distance (in millimeters) you want to check for farness of the nearest object in front of the sensor
            tolerance_percentage (float): value between 0 and 1. It will calculate the higher percentage on its own. (e.g.: 0.9 -> 90%; 0.95 -> 95%)

        Returns:
            bool: If the current (estimated) distance from the nearest object in front of the sensor is inside of the desired value (inclusive tolerance) (True) or not (False)
        '''
        dist = self.get_estimated_mm()

        if tolerance_percentage > 1 or tolerance_percentage <= 0:
            log('tolerance_percentage parameter can only be a value between 0 and 1 (exclusive 0)!', in_exception=True)
            raise ValueError('tolerance_percentage parameter can only be a value between 0 and 1 (exclusive 0)!')

        if mm_to_check * tolerance_percentage < dist < mm_to_check * (tolerance_percentage + (1 - tolerance_percentage) * 2):
            return True
        return False

    def distance_in_reach_one_side(self, mm_to_check: int, tolerance_percentage: float, higher_lower: str) -> bool:
        '''
        Tells you, if the current (estimated) distance is in your desired distance including your tolerance. It will only check one side (if the current estimated distance is higher or lower than the desired value inclusive tolerance)

        Args:
            mm_to_check (int): the distance (in millimeters) you want to check for farness of the nearest object in front of the sensor
            tolerance_percentage (float): value between 0 and 1. It will calculate the higher percentage on its own. (e.g.: 0.9 -> 90%; 0.95 -> 95%)
            higher_lower (str): either "lower" or "higher", meaning that if the current estimated distance is lower (or higher) than your desired distance inclusive tolerance

        Returns:
            bool: If the current estimated value is lower (or higher) than your desired distance inclusive tolerance (True), but only checked on one side (the higher or lower side)
        '''
        dist = self.get_estimated_mm()

        if tolerance_percentage > 1 or tolerance_percentage <= 0:
            log('tolerance_percentage parameter can only be a value between 0 and 1 (exclusive 0)!', in_exception=True)
            raise ValueError('tolerance_percentage parameter can only be a value between 0 and 1 (exclusive 0)!')

        if higher_lower.lower() == 'lower':
            return dist < mm_to_check * (tolerance_percentage + (1 - tolerance_percentage) * 2)
        elif higher_lower.lower() == 'higher':
            return mm_to_check * tolerance_percentage < dist
        else:
            log('higher_lower parameter can only be "higher" or "lower"!', in_exception=True)
            raise ValueError('higher_lower parameter can only be "higher" or "lower"!')
