#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-09-15

try:
    import cv2
    from typing import Optional
    import numpy as np
    import os
    import time
    import threading
    from camera_manager import CameraManager  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

class CameraBrightnessDetector:
    def __init__(self, camera_manager: CameraManager, tiles_x: int = 1, tiles_y: int = 1,
                 threshold_brightness: int = 127, threshold_black: int = 50,
                 threshold_white: int = 200, test_mode: bool = False, use_bias: bool = False):
        '''
        Class for the camera. This is for detecting if something on the camera is black or white, while being able to segment the camera into many fragments, each seperatly telling you something about the color black or white

        Args:
            camera_manager (CameraManager): The camera manager which gives you frames from the camera
            tiles_x (int, optional): The amount of cachel which the camera should get divided by alongside the x-axis. (default: 1)
            tiles_y (int, optional): the amount of cachel which the camera should get divided by alongside the y-axis. (default: 1)
            threshold_brightness (int, optional): Point of where the black and white detection meets in the center (higher -> leaning more towards white, black gets harder seen) (default:127)
            threshold_black (int, optional): Where the camera should detect if it sees black (default: 50)
            threshold_white (int, optional): Where the camera should detect if it sees white (default: 200)
            test_mode (bool, optional): Use this ONLY on your pc and not the robot, since nothing will happen except using a lot of power and ressources. Will create a window which makes you able to see what the camera sees (default: False)
            use_bias (bool, optional): If the bias should calculate itself (True) or not (False) (default: False)
        '''
        self.tiles_x = tiles_x
        self.tiles_y = tiles_y
        self.test_mode = test_mode
        self.connected = True

        self._default_black = threshold_black
        self._default_white = threshold_white
        self._default_brightness = threshold_brightness

        self.use_bias = use_bias
        self._brightness_bias = None
        self._capture_lock = threading.Lock()
        self._bias_lock = threading.Lock()

        self.camera_manager = camera_manager
        self.save_base_path = "/home/kipr/BotBall-data/bias_files/brightness_detector"
        os.makedirs(self.save_base_path, exist_ok=True)

    # ======================== SETTER ========================
    def set_x_tiles(self, n:int) -> None:
        '''
        change the tiles count in the horizontal

        Args:
            n (int): number of wanted tiles

        Returns:
            None
        '''
        self.tiles_x = n

    def set_y_tiles(self, n) -> None:
        '''
        change the tiles count in the vertical

        Args:
            n (int): number of wanted tiles

        Returns:
            None
        '''
        self.tiles_y = n

    def set_test_mode(self, flag: bool) -> None:
        '''
        change to the test mode, so you are able to see what is going on

        Args:
            flag (bool): Should the test mode be active (True) or inactive (False)

        Returns:
            None
        '''
        self.test_mode = flag

    # ======================== PRIVATE METHODS ========================
    def _apply_bias(self):
        '''
        sets the bias for internal calibration of the thresholds

        Args:
            None

        Returns:
            None
        '''
        if not self.use_bias:
            self.threshold_black = self._default_black
            self.threshold_white = self._default_white
            self.threshold_brightness = self._default_brightness
            return

        bias = self.get_brightness_bias()
        if bias is None:
            self.threshold_black = self._default_black
            self.threshold_white = self._default_white
            self.threshold_brightness = self._default_brightness
        else:
            self.threshold_black = int(bias * 0.05)
            self.threshold_white = int(bias * 0.95)
            self.threshold_brightness = int(bias * 0.5)

    def _visualize(self, frame, results) -> None:
        '''
        lets you see the frame if you are in test mode

        Args:
            frame: the current frame
            results: the frames in which the desired

        Returns:
            None
        '''
        h, w, _ = frame.shape
        tile_h = h // self.tiles_y
        tile_w = w // self.tiles_x

        for y, row in enumerate(results):
            for x, data in enumerate(row):
                x1, y1 = x*tile_w, y*tile_h
                x2, y2 = (x+1)*tile_w, (y+1)*tile_h
                color = (0, 255, 0) if data["bright"] else (0, 0, 255)
                if data["black"]:
                    color = (255, 0, 0)
                if data["white"]:
                    color = (255, 255, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        if self.test_mode:
            cv2.imshow("Test Mode - Camera Feedback", frame)
        return frame

    def _capture_frame(self) -> tuple:
        '''
        gets the frame and the grayscale

        Args:
            None

        Returns:
            tuple:
                frame -> the current frame
                gray -> the current grayscale
        '''
        self._apply_bias()

        frame = self.camera_manager.get_frame()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        return frame, gray

    def _get_tiles(self, frame) -> list:
        '''
        create every tile

        Args:
            frame: the current frame

        Returns:
            list:
                tiles -> the entire screen but separated into the wanted tile amount
        '''
        h, w = frame.shape
        tile_h = h // self.tiles_y
        tile_w = w // self.tiles_x

        tiles = []
        for ty in range(self.tiles_y):
            row = []
            for tx in range(self.tiles_x):
                tile = frame[ty*tile_h:(ty+1)*tile_h, tx*tile_w:(tx+1)*tile_w]
                row.append(tile)
            tiles.append(row)
        return tiles

    def _analyze_tile(self, tile) -> dict:
        '''
        analyse a single tile for different reasons

        Args:
            tile: one tile of the entire frame

        Returns:
            dict:
                mean -> the average color (in grayscale) of the entire tile
                bright -> if there is something bright (True) or not (False)
                black -> if there is black inside the tile (True) or not (False)
                white -> if there is white inside the tile (True) or not (False)
        '''
        mean_val = np.mean(tile)
        is_bright = mean_val > self.threshold_brightness
        contains_black = np.any(tile < self.threshold_black)
        contains_white = np.any(tile > self.threshold_white)
        return {
            "mean": mean_val,
            "bright": is_bright,
            "black": contains_black,
            "white": contains_white
        }

    def _save_result(self, frame, func_name, status, mode) -> None:
        '''
        saves a frame (marked or unmarked) in a folder, so you can see what the function saw or what it didn't see.

        Args:
            frame: the frame, where something was found (a marked frame) or if nothing was found just the normal frame
            func_name: the function name, which calls this function
            status: was something found ("FOUND") or not ("NOTFOUND")
            mode: the type of function where it got called from (e.g. "is", "find" or "wait"

        Returns:
            None
        '''
        folder = os.path.join(self.save_base_path, f"results_brightness/{mode}")
        os.makedirs(folder, exist_ok=True)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{func_name}_{status}_{timestamp}.png"
        path = os.path.join(folder, filename)
        cv2.imwrite(path, frame)
        log(f"{func_name} has the status {status}")

    # ======================== PUBLIC METHODS ========================

    # ---------- Frame-wide detection ----------
    def is_black_in_frame(self) -> bool:
        '''
        searches one entire frame for something black

        Args:
            None

        Returns:
            bool: if something black was found (True) or not (False)
        '''
        frame, gray = self._capture_frame()
        found = np.any(gray < self.threshold_black)
        self._save_result(frame, "is_black_in_frame", "FOUND" if found else "NOTFOUND", mode="is")
        return found

    def is_white_in_frame(self):
        '''
        searches one entire frame for something white

        Args:
            None

        Returns:
            bool: if something white was found (True) or not (False)
        '''
        frame, gray = self._capture_frame()
        found = np.any(gray > self.threshold_white)
        self._save_result(frame, "is_white_in_frame", "FOUND" if found else "NOTFOUND", mode="is")
        return found

    # ---------- Regional detection ----------
    def is_black_left(self):
        '''
        searches the left side (from the center) of a frame for something black

        Args:
            None

        Returns:
            bool: if something black was found (True) or not (False)
        '''
        frame, gray = self._capture_frame()
        w = gray.shape[1]
        left_region = gray[:, :w // 2]
        found = np.any(left_region < self.threshold_black)
        self._save_result(frame, "is_black_left", "FOUND" if found else "NOT_FOUND", mode="is")
        return found

    def is_black_right(self):
        '''
        searches the right side (from the center) of a frame for something black

        Args:
            None

        Returns:
            bool: if something black was found (True) or not (False)
        '''
        frame, gray = self._capture_frame()
        w = gray.shape[1]
        right_region = gray[:, w // 2:]
        found = np.any(right_region < self.threshold_black)
        self._save_result(frame, "is_black_right", "FOUND" if found else "NOT_FOUND", mode="is")
        return found

    def is_black_top(self):
        '''
        searches the top (from the center) of a frame for something black

        Args:
            None

        Returns:
            bool: if something black was found (True) or not (False)
        '''
        frame, gray = self._capture_frame()
        h = gray.shape[0]
        top_region = gray[:h // 2, :]
        found = np.any(top_region < self.threshold_black)
        self._save_result(frame, "is_black_top", "FOUND" if found else "NOT_FOUND", mode="is")
        return found

    def is_black_bottom(self):
        '''
        searches the bottom (from the center) of a frame for something black

        Args:
            None

        Returns:
            bool: if something black was found (True) or not (False)
        '''
        frame, gray = self._capture_frame()
        h = gray.shape[0]
        bottom_region = gray[h // 2:, :]
        found = np.any(bottom_region < self.threshold_black)
        self._save_result(frame, "is_black_bottom", "FOUND" if found else "NOT_FOUND", mode="is")
        return found

    def is_white_left(self):
        '''
        searches the left side (from the center) of a frame for something white

        Args:
            None

        Returns:
            bool: if something white was found (True) or not (False)
        '''
        frame, gray = self._capture_frame()
        w = gray.shape[1]
        left_region = gray[:, :w // 2]
        found = np.any(left_region > self.threshold_white)
        self._save_result(frame, "is_white_left", "FOUND" if found else "NOT_FOUND", mode="is")
        return found

    def is_white_right(self):
        '''
        searches the right side (from the center) of a frame for something white

        Args:
            None

        Returns:
            bool: if something white was found (True) or not (False)
        '''
        frame, gray = self._capture_frame()
        w = gray.shape[1]
        right_region = gray[:, w // 2:]
        found = np.any(right_region > self.threshold_white)
        self._save_result(frame, "is_white_right", "FOUND" if found else "NOTFOUND", mode="is")
        return found

    def is_white_top(self):
        '''
        searches the top (from the center) of a frame for something white

        Args:
            None

        Returns:
            bool: if something white was found (True) or not (False)
        '''
        frame, gray = self._capture_frame()
        h = gray.shape[0]
        top_region = gray[:h // 2, :]
        found = np.any(top_region > self.threshold_white)
        self._save_result(frame, "is_white_top", "FOUND" if found else "NOTFOUND", mode="is")
        return found

    def is_white_bottom(self):
        '''
        searches the bottom (from the center) of a frame for something white

        Args:
            None

        Returns:
            bool: if something white was found (True) or not (False)
        '''
        frame, gray = self._capture_frame()
        h = gray.shape[0]
        bottom_region = gray[h // 2:, :]
        found = np.any(bottom_region > self.threshold_white)
        self._save_result(frame, "is_white_bottom", "FOUND" if found else "NOT_FOUND", mode="is")
        return found

    def is_color_centered(self, color="black", range_percent=0.2, orientation="vertical") -> bool:
        '''
        searches in the middle of the screen for the desired color (black or white). This only for one frame

        Args:
            color (str): either "black" or "white", so the color that should be searched after
            range_percent (float): how much percentage of the screen should be read, so the corresponding color does not need to be exactly in the center (it is like a bias)
            orientation (str) either "vertical", "horizontal" or "both". This is for creating the line in the kind of center line you desire

        Returns:
            bool: if the color was found (True) or not (False)
        '''
        frame, gray = self._capture_frame()
        h, w = gray.shape

        if orientation.lower() == "horizontal":
            if range_percent <= 0:
                y1 = h // 2
                y2 = y1 + 1
            else:
                band_half = int(h * range_percent)
                y1 = max(h // 2 - band_half, 0)
                y2 = min(h // 2 + band_half, h)
            region = gray[y1:y2, :]
        elif orientation.lower() == "vertical":
            if range_percent <= 0:
                x1 = w // 2
                x2 = x1 + 1
            else:
                band_half = int(w * range_percent)
                x1 = max(w // 2 - band_half, 0)
                x2 = min(w // 2 + band_half, w)
            region = gray[:, x1:x2]
        elif orientation.lower() == "both":
            if range_percent <= 0:
                y1 = h // 2
                y2 = y1 + 1
                x1 = w // 2
                x2 = x1 + 1
            else:
                band_h = int(h * range_percent)
                band_w = int(w * range_percent)
                y1 = max(h // 2 - band_h, 0)
                y2 = min(h // 2 + band_h, h)
                x1 = max(w // 2 - band_w, 0)
                x2 = min(w // 2 + band_w, w)
            region = gray[y1:y2, x1:x2]

        else:
            raise ValueError("orientation must be 'horizontal', 'vertical', or 'both'")

        if color.lower() == "black":
            found = np.any(region < self.threshold_black)
        elif color.lower() == "white":
            found = np.any(region > self.threshold_white)
        else:
            raise ValueError("color must be 'black' or 'white'")

        func_name = f"is_color_centered_{color}_{orientation}"
        self._save_result(frame, func_name, "FOUND" if found else "NOTFOUND", mode="is")

        return found

    # ---------- Find methods ---------- #

    def find_black(self):
        '''
        find all the tiles where something black was found

        Args:
            None

        Returns:
            list: All positions (x, y in a tuple) of every tile where black was found
        '''
        frame, results = self.analyze_frame()
        black_positions = [(x, y) for y, row in enumerate(results) for x, data in enumerate(row) if data["black"]]
        marked = self._visualize(frame.copy(), results)
        status = "FOUND" if black_positions else "NOTFOUND"
        self._save_result(marked, "find_black", status, "find")
        return black_positions

    def find_white(self):
        '''
        find all the tiles where something white was found

        Args:
            None

        Returns:
            list: All positions (x, y in a tuple) of every tile where white was found
        '''
        frame, results = self.analyze_frame()
        white_positions = [(x, y) for y, row in enumerate(results) for x, data in enumerate(row) if data["white"]]
        marked = self._visualize(frame.copy(), results)
        status = "FOUND" if white_positions else "NOTFOUND"
        self._save_result(marked, "find_white", status, "find")
        return white_positions

    # ---------- Wait methods ---------- #

    def wait_black(self, max_secs:float=9999999.0) -> list:
        '''
        wait until something black is found and if there is something black, get all the black positions

        Args:
            max_secs (float): The maximum amount of time in seconds which it is allowed to search for the color black (default: 9999999.0). This is a fail save


        Returns:
            list: All positions (x, y in a tuple) of every tile where black was found
        '''
        start_time = time.time()
        while time.time() - start_time < max_secs:
            frame, results = self.analyze_frame()
            black_positions = [(x, y) for y, row in enumerate(results) for x, data in enumerate(row) if data["black"]]
            if black_positions:
                marked = self._visualize(frame.copy(), results)
                self._save_result(marked, "wait_black", "FOUND", "wait")
                return black_positions
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return []
        return []

    def wait_white(self, max_secs:float=9999999.0) -> list:
        '''
        wait until something white is found and if there is something white, get all the white positions

        Args:
            max_secs (float): The maximum amount of time in seconds which it is allowed to search for the color white (default: 9999999.0). This is a fail save


        Returns:
            list: All positions (x, y in a tuple) of every tile where white was found
        '''
        start_time = time.time()
        while time.time() - start_time < max_secs:
            frame, results = self.analyze_frame()
            white_positions = [(x, y) for y, row in enumerate(results) for x, data in enumerate(row) if data["white"]]
            if white_positions:
                marked = self._visualize(frame.copy(), results)
                self._save_result(marked, "wait_white", "FOUND", "wait")
                return white_positions
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return []
        return []

    # ---------- Other methods ---------- #

    def calculate_brightness_bias(self, frames=50, delay=0.05) -> float:
        '''
        calculates the brightness bias via holding something white in front of the camera. Saves the bias and if there is already a bias in the file, then adds the new bias to the old bias and divides by 2, to get the average.
        If this function won't be called, but if you still want a bias, then if there is a bias file of the brightness, then it will just take the old bias.

        Args:
            frames (int): how many pictures should be taken to calculate the average (default: 50)
            delay (float): time in seconds between each frame (default: 0.05)

        Returns:
            float: the calibrated bias (if there was already a bias calibrated once,
                   it will add it to the newly calibrated one and divide it by 2 to get the average bias)
        '''
        bias_values = []

        for i in range(frames):
            _, gray = self._capture_frame()
            bias_values.append(np.mean(gray))
            time.sleep(delay)

        current_bias = float(np.mean(bias_values))

        self._brightness_bias = current_bias
        return self.get_brightness_bias(calibrated=True)

    def get_brightness_bias(self, calibrated: bool = False) -> Optional[float]:
        '''
        Gives you the opportunity to see the calibrated bias from the file.
        Optionally updates the stored bias with a new calibration.

        Args:
            calibrated (bool, optional):
                If True, combines the current brightness measurement with the stored bias and writes the average back.
                If False, only reads the stored bias (default: False).

        Returns:
            float: The bias from the brightness bias file (optionally updated with a new calibration)
        '''
        file_path = os.path.join(self.save_base_path, "brightness_bias.txt")

        with self._bias_lock:
            try:
                new_bias = None
                if calibrated and self._brightness_bias is not None:
                    new_bias = self._brightness_bias
                elif calibrated:
                    _, gray = self._capture_frame()
                    new_bias = float(np.mean(gray))

                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        old_bias = float(f.read().strip())
                else:
                    old_bias = None

                if calibrated:
                    if old_bias is not None:
                        avg_bias = (old_bias + new_bias) / 2
                    else:
                        avg_bias = new_bias
                    with open(file_path, "w") as f:
                        f.write(str(avg_bias))
                    self._brightness_bias = avg_bias
                    return avg_bias
                else:
                    if old_bias is not None:
                        self._brightness_bias = old_bias
                        return old_bias
                    else:
                        log("Bias not calculated yet and file not found.", important=True)
                        return None

            except Exception as e:
                log(f"Could not read/write bias from file: {e}", important=True, in_exception=True)
                return None

    def analyze_frame(self) -> list:
        '''
        the newly edited frame (with the tiles set up)

        Args:
            None

        Returns:
            list: All positions (x, y in a tuple) of every tile and if something was found in any tile or not
        '''
        frame, gray = self._capture_frame()
        tiles = self._get_tiles(gray)

        results = []
        for row in tiles:
            result_row = []
            for tile in row:
                result_row.append(self._analyze_tile(tile))
            results.append(result_row)

        if self.test_mode:
            self._visualize(frame, results)

        return frame, results


# Example usage:
if __name__ == "__main__":
    cam = CameraManager(cam_index=0)
    sensor = CameraBrightnessDetector(camera_manager=cam, tiles_x=4, tiles_y=3, test_mode=False)

    try:
        black_tiles = sensor.find_black()
        print("Black tiles at positions:", black_tiles)

        white_tiles = sensor.find_white()
        print("White tiles at positions:", white_tiles)

        if sensor.is_black_top():
            print("Black detected on top!")
        if sensor.is_white_bottom():
            print("White detected on bottom!")

    finally:
        cam.release()

