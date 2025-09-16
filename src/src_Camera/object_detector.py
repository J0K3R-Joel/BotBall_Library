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
    import os
    import numpy as np
    from datetime import datetime
    import time
    from threading import Lock
    from camera_manager import CameraManager  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

class CameraObjectDetector:
    def __init__(self, camera_manager: CameraManager=None, test_mode=False):
        base_path = "/usr/lib/bias_files/object_detector"
        os.makedirs(base_path, exist_ok=True)

        self.object_dir = os.path.join(base_path, "objects")
        self.results_dir = os.path.join(base_path, "results")
        self.lighting_dir = os.path.join(base_path, "lighting_ref")
        os.makedirs(self.object_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.lighting_dir, exist_ok=True)

        self.test_mode = test_mode
        self.object_dict = {}
        self.camera_manager = camera_manager

        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_run_dir = os.path.join(self.results_dir, f"run_{run_id}")
        os.makedirs(self.current_run_dir, exist_ok=True)

        self._capture_white_real()

        self.bias = self._compute_lighting_bias()
        self.save_lock = Lock()

        self._save_corrected_background()
        self._build_object_dict()


    # ======================== PRIVATE METHODS ========================
    def _capture_white_real(self):
        '''
        creates a picture of the current background, to later analyze the bias between the ideal and the real background (hint: take a piece of paper, so something white that fills up the entire screen)

        Args:
            None

        Returns:
            None
        '''
        os.makedirs(self.lighting_dir, exist_ok=True)
        white_path = os.path.join(self.lighting_dir, "white_real.png")

        frame = self.camera_manager.get_frame()
        time.sleep(5)
        cv2.imwrite(white_path, frame)



    def _compute_lighting_bias(self) -> np.float32:
        '''
        calibrates the bias between the ideal and the real background

        Args:
            None

        Returns:
            np.float32: float of the difference between the ideal and real median
        '''
        ideal_path = os.path.join(self.lighting_dir, "white_ideal.png")
        real_path = os.path.join(self.lighting_dir, "white_real.png")

        if not os.path.exists(ideal_path) or not os.path.exists(real_path):
            log("No lightning ref found, bias=0", important=True)
            return np.array([0,0,0], dtype=np.float32)

        ideal = cv2.imread(ideal_path)
        real = cv2.imread(real_path)
        if ideal is None or real is None:
            log("Lightning ref could not be loaded, Bias=0", important=True)
            return np.array([0,0,0], dtype=np.float32)

        ideal_hsv = cv2.cvtColor(ideal, cv2.COLOR_BGR2HSV)
        real_hsv = cv2.cvtColor(real, cv2.COLOR_BGR2HSV)
        ideal_median = np.median(ideal_hsv.reshape(-1,3), axis=0)
        real_median = np.median(real_hsv.reshape(-1,3), axis=0)
        return (ideal_median - real_median).astype(np.float32)

    def _apply_bias(self, image) -> np.ndarray:
        '''
        applies the bias to an image, so the image is almost as the ideal background

        Args:
            image: the desired image you want to apply the bias onto

        Returns:
            np.ndarray: the same image but with the bias onto it
        '''
        ideal_path = os.path.join(self.lighting_dir, "white_ideal.png")
        real_path = os.path.join(self.lighting_dir, "white_real.png")

        ideal = cv2.imread(ideal_path)
        real = cv2.imread(real_path)

        if ideal is None or real is None:
            return image

        h, w = image.shape[:2]
        ideal = cv2.resize(ideal, (w, h))
        real = cv2.resize(real, (w, h))

        image_f = image.astype(np.float32) + 1
        real_f = real.astype(np.float32) + 1
        ideal_f = ideal.astype(np.float32) + 1

        corrected = (image_f / real_f) * ideal_f
        corrected = np.clip(corrected, 0, 255).astype(np.uint8)
        return corrected

    def _extract_largest_object(self, frame, is_ideal=False):
        '''
        searches for the largest object iun the frame and returns the contour of the object

        Args:
            frame: the frame (or image) that should be looked at for the largest object
            is_ideal (bool, optional): If it is a picture with ideal settings (True), or a normal picture

        Returns:
            The frame and the contour of the largest object
        '''
        if is_ideal:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        else:
            ideal_path = os.path.join(self.lighting_dir, "white_ideal.png")
            ideal = cv2.imread(ideal_path)
            if ideal is None:
                return None, None
            ideal_resized = cv2.resize(ideal, (frame.shape[1], frame.shape[0]))
            corrected = self._apply_bias(frame)
            diff = cv2.absdiff(corrected, ideal_resized)
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray_diff, 40, 255, cv2.THRESH_BINARY)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None, None

        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) < 200:
            return None, None

        x, y, w, h = cv2.boundingRect(largest_contour)
        roi = frame[y:y + h, x:x + w]

        if self.test_mode:
            debug_frame = frame.copy()
            cv2.drawContours(debug_frame, [largest_contour], -1, (0, 255, 0), 2)
            cv2.imshow("Detected Object", debug_frame)
            cv2.imshow("Object Mask", mask)
            cv2.waitKey(1)

        cv2.destroyAllWindows()
        return roi, largest_contour

    def _mark_detected_object(self, frame, contour):
        '''
        draws a circle or rectangle around the object

        Args:
            frame: the frame which should be drawn onto
            contour: the circumference of the object

        Returns:
            the frame with the circle or rectangle around the object
        '''
        if contour is None:
            return frame

        (x_center, y_center), radius = cv2.minEnclosingCircle(contour)
        center = (int(x_center), int(y_center))
        radius = int(radius)
        cv2.circle(frame, center, radius, (0, 255, 0), 2)

        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        return frame

    def _build_object_dict(self):
        '''
        creates a dictionary of every object with every single picture of every object.

        Args:
            None

        Returns:
            None
        '''
        for obj_name in os.listdir(self.object_dir):
            obj_path = os.path.join(self.object_dir, obj_name)
            if not os.path.isdir(obj_path):
                continue
            self.object_dict[obj_name] = []
            for f in os.listdir(obj_path):
                if not f.endswith((".jpg", ".png")):
                    continue
                img_path = os.path.join(obj_path, f)
                img = cv2.imread(img_path)
                if img is None:
                    log(f"Picture could not be loaded: {img_path}", important=True)
                    continue
                roi, _ = self._extract_largest_object(img, is_ideal=True)
                if roi is not None:
                    self.object_dict[obj_name].append(roi)
                else:
                    self.object_dict[obj_name].append(img)

    def _get_hsv_from_roi(self, roi) -> tuple:
        '''
        getting the HSV value from the roi (region of interest)

        Args:
            roi: The region which is important

        Returns:
           tuple:
                the lower and higher HSV values of the roi
        '''
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        s = hsv[:, :, 1]
        v = hsv[:, :, 2]
        mask = (s > 50) & (v > 50)
        filtered_pixels = hsv[mask]

        if filtered_pixels.size == 0:
            filtered_pixels = hsv.reshape(-1, 3)

        median = np.median(filtered_pixels, axis=0)

        error_range = np.array([10, 50, 50])
        lower_hsv = np.maximum(median - error_range, [0, 0, 0]).astype(int)
        upper_hsv = np.minimum(median + error_range, [179, 255, 255]).astype(int)

        return tuple(lower_hsv), tuple(upper_hsv)

    def _get_hsv_stats(self, roi) -> np.median:
        '''
        getting the HSV median from the roi (region of interest)

        Args:
            roi: The region which is important

        Returns:
            np.median: the HSV median values
        '''
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        s = hsv[:, :, 1]
        v = hsv[:, :, 2]
        mask = (s > 40) & (v > 40)

        filtered = hsv[mask]
        if filtered.size == 0:
            filtered = hsv.reshape(-1, 3)

        median = np.median(filtered, axis=0)
        return median  # (H, S, V)

    def _save_result(self, frame, label:str, mode:str="find", status:str="FOUND"):
        '''
        saves the image if something was found or not, so you can later analyse what went wrong / good

        Args:
            frame: The desired frame to save
            label (str): The text of the frame name (typically the function name)
            mode (str, optional): The kind of function which it belongs to (this is for creating the folder or adding into a folder). (default: "find")
            status (str, optional): Was something found ("FOUND") or nothing important ("NOT_FOUND")

        Returns:
           None
        '''

        with self.save_lock:
            if not isinstance(self.current_run_dir, str):
                run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.current_run_dir = os.path.join(self.results_dir, f"run_{run_id}")
                os.makedirs(self.current_run_dir, exist_ok=True)

            target_dir = os.path.join(self.current_run_dir, mode)
            os.makedirs(target_dir, exist_ok=True)

            filename = os.path.join(target_dir, f"{label}_{status}.jpg")
            cv2.imwrite(filename, frame)

    def _draw_circle_on_contour(self, frame, contour):
        '''
        draws a circle around the object

        Args:
            frame: the frame which should be drawn onto
            contour: the circumference of the object

        Returns:
            the frame with the circle around the object
        '''
        if contour is not None:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            cv2.circle(frame, center, radius, (0, 255, 0), 2)
        return frame

    def _save_corrected_background(self) -> None:
        '''
        saves the real background with the bias added to it into a new image

        Args:
            None

        Returns:
            None, but creates the image, so you can look at it
        '''
        frame = self.camera_manager.get_frame()

        corrected = self._apply_bias(frame)

        os.makedirs(self.results_dir, exist_ok=True)
        path = os.path.join(self.results_dir, "background_corrected.jpg")
        cv2.imwrite(path, corrected)

    def _detect_shape(self, contour) -> str:
        '''
        ==== NEEDS IMPROVEMENT ====
        detect the shape of the object with the contour

        Args:
            contour: the circumference of the object

        Returns:
            str: the shape of the object
        '''
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
        vertices = len(approx)

        if vertices == 3:
            return "triangle"
        elif vertices == 4:
            return "rectangle"
        elif vertices == 5:
            return "pentagon"
        else:
            return "circle" if cv2.isContourConvex(approx) else "other"

    def _get_color_ranges(self) -> dict:
        '''
        creates and return the dict with the color ranges (HSV values)

        Args:
           None

        Returns:
            dict: every color with the lowest and highest HSV
        '''
        return {
            "red": [(0, 100, 100), (10, 255, 255)],
            "green": [(40, 50, 50), (80, 255, 255)],
            "blue": [(100, 150, 50), (140, 255, 255)],
            "yellow": [(20, 100, 100), (30, 255, 255)],
            "orange": [(10, 100, 100), (20, 255, 255)],
            "purple": [(140, 100, 100), (160, 255, 255)],
            "black": [(0, 0, 0), (179, 255, 50)],
            "white": [(0, 0, 200), (179, 40, 255)],
        }

    def _capture_good_frame(self, min_brightness: int = 100, timeout: float = 5.0):
        '''
        creates images as long as the timeout limit is not hit or a good picture with enough brightness is shot

        Args:
            min_brightness (int, optional): the least amount of brightness the image HAS TO get (default: 100)
            timeout (float, optional): the amount of seconds it is allowed to take for a single good frame (default: 5.0)

        Returns:
            the last valid frame
        '''
        start_time = time.time()

        while True:
            frame = self.camera_manager.get_frame()

            last_frame = frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mean_brightness = np.mean(gray)

            if mean_brightness >= min_brightness:
                break

            if time.time() - start_time > timeout:
                log("Timout reached - using last picture", important=True)
                break

            time.sleep(0.1)

        return last_frame

    # ======================== PUBLIC METHODS ========================
    # x----------x find methods x------------x

    def find_by_shape(self, shape_name: str) -> bool:
        '''
        ==== NEEDS IMPROVEMENT ====
        takes one picture and analyzes, if the desired shape name is found

        Args:
            shape_name (str): the name of the shape (see all available shape names in _detect_shape())

        Returns:
            If the shape was found (True) or not (False)
        '''
        frame = self._capture_good_frame(min_brightness=100, timeout=8)
        if frame is None:
            log("Could not create a solid picture", important=True)
            return False

        corrected = self._apply_bias(frame)
        roi, contour = self._extract_largest_object(corrected)

        found = False
        if contour is not None:
            approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
            vertices = len(approx)

            if shape_name == "triangle" and vertices == 3:
                found = True
            elif shape_name == "rectangle" and vertices == 4:
                found = True
            elif shape_name == "circle" and vertices > 5:
                found = True

        if found:
            frame_marked = self._draw_circle_on_contour(frame, contour)
            self._save_result(frame_marked, f"shape_{shape_name}", mode="find", status="FOUND")
        else:
            self._save_result(frame, f"shape_{shape_name}", mode="find", status="NOT_FOUND")


        return found

    def find_by_color(self, color_name: str) -> bool:
        '''
        takes one picture and analyzes, if the desired color name is found

        Args:
            color_name (str): the name of the color (see all available colors in _get_color_ranges())

        Returns:
            If the color was found (True) or not (False)
        '''
        hsv_ranges = self._get_color_ranges()

        if color_name not in hsv_ranges:
            log(f"Color '{color_name}' is not supported.")
            return False

        frame = self._capture_good_frame(min_brightness=100, timeout=8)
        if frame is None:
            log("No solid picture could be made", important=True)
            return False

        corrected = self._apply_bias(frame)
        hsv = cv2.cvtColor(corrected, cv2.COLOR_BGR2HSV)
        lower, upper = hsv_ranges[color_name]
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        found = False
        contour = None
        if contours:
            contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(contour) > 200:
                found = True

        if found:
            frame_marked = self._draw_circle_on_contour(frame, contour)
            self._save_result(frame_marked, f"color_{color_name}", mode="find", status="FOUND")
        else:
            self._save_result(frame, f"color_{color_name}", mode="find", status="NOT_FOUND")

        return found

    def find_by_object(self, object_name: str, min_matches: int = 30, max_hue_diff: int = 10) -> bool:
        '''
        takes one picture and analyzes, if the desired object is found

        Args:
            object_name (str): the name of the object (the folder name of the object)
            min_matches (int, optional): the least amount of shape matches to be able to see if its the same object by shape. Higher value -> more strict (default: 30)
            max_hue_diff (int, optional): the forgiveness of color. Lower value -> more strict (less forgiving by having a different color (default: 10)

        Returns:
            If the object was found (True) or not (False)
        '''
        if object_name not in self.object_dict:
            log(f"Object '{object_name}' not found in the existing folder.")
            return False

        frame = self._capture_good_frame(min_brightness=100, timeout=5)
        if frame is None:
            log("No solid picture could be made", important=True)
            return False

        corrected = self._apply_bias(frame)
        roi_frame, contour_frame = self._extract_largest_object(corrected)
        if roi_frame is None:
            self._save_result(frame, f"object_{object_name}", mode="find", status="NOT_FOUND")
            return False

        template = self.object_dict[object_name][0]
        roi_template, _ = self._extract_largest_object(template, is_ideal=True)
        if roi_template is None:
            log("Template could not be extracted!", important=True)
            return False

        orb = cv2.ORB_create()
        kp_template, des_template = orb.detectAndCompute(roi_template, None)
        kp_frame, des_frame = orb.detectAndCompute(roi_frame, None)

        found = False
        if des_template is not None and des_frame is not None:
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = matcher.match(des_frame, des_template)
            good_matches = len(matches)

            lower_template, upper_template = self._get_hsv_from_roi(roi_template)
            hue_template = (lower_template[0] + upper_template[0]) // 2
            lower_frame, upper_frame = self._get_hsv_from_roi(roi_frame)
            hue_frame = (lower_frame[0] + upper_frame[0]) // 2
            hue_diff = abs(int(hue_frame) - int(hue_template))

            if good_matches >= min_matches and hue_diff <= max_hue_diff:
                found = True


        if found:
            frame_marked = self._draw_circle_on_contour(frame, contour_frame)
            self._save_result(frame_marked, f"object_{object_name}", mode="find", status="FOUND")
        else:
            self._save_result(frame, f"object_{object_name}", mode="find", status="NOT_FOUND")

        return found

    def find_by_shape_and_color(self, shape_name: str, color_name: str) -> bool:
        '''
        ==== NEEDS IMPROVEMENT ====
        takes one picture and analyzes, if the desired color name AND shape name on the same object is found

        Args:
            shape_name (str): the name of the shape (see all available shape names in _detect_shape())
            color_name (str): the name of the color (see all available colors in _get_color_ranges())

        Returns:
            If the color with the desired shape was found (True) or not (False)
        '''
        hsv_ranges = self._get_color_ranges()

        if color_name not in hsv_ranges:
            log(f"Color'{color_name}' not supported.", important=True)
            return False

        frame = self._capture_good_frame(min_brightness=100, timeout=8)
        if frame is None:
            log("No solid picture could be made.", important=True)
            return False

        corrected = self._apply_bias(frame)
        hsv = cv2.cvtColor(corrected, cv2.COLOR_BGR2HSV)

        lower, upper = hsv_ranges[color_name]
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        found = False
        contour = None
        if contours:
            contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(contour) > 200:
                approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
                vertices = len(approx)

                if shape_name == "triangle" and vertices == 3:
                    found = True
                elif shape_name == "rectangle" and vertices == 4:
                    found = True
                elif shape_name == "circle" and vertices > 6:
                    found = True

        if found:
            frame_marked = self._draw_circle_on_contour(frame, contour)
            self._save_result(frame_marked, f"shape_{shape_name}_color_{color_name}", mode="find", status="FOUND")
        else:
            self._save_result(frame, f"shape_{shape_name}_color_{color_name}", mode="find", status="NOT_FOUND")

        return found

    # x----------x wait methods x------------x
    def wait_for_object(self, object_name: str, interval: float=0.25, min_matches: int =35, max_hue_diff: int=10, max_secs: float=999999.0) -> bool:
        '''
        takes multiple images for as long as the timeout limit is not hit or the object is not found. If the object is found within the limit, it exits this function

        Args:
            object_name (str): the name of the object (the folder name of the object)
            interval (float, optional): the time in seconds between two pictures (default: 0.25)
            min_matches (int, optional): the least amount of shape matches to be able to see if its the same object by shape. Higher value -> more strict (default: 35)
            max_hue_diff (int, optional): the forgiveness of color. Lower value -> more strict (less forgiving by having a different color (default: 10)
            max_secs (float, optional): The most amount of time in seconds, which it is allowed to wait for the object to be found (default: 999999.0)

        Returns:
            If the object was found (True) or not (False)
        '''
        if object_name not in self.object_dict:
            log(f"Object '{object_name}' does not exist in the ideal folder.")
            return False

        template = self.object_dict[object_name][0]
        roi_template, contour_template = self._extract_largest_object(template, is_ideal=True)
        if roi_template is None:
            log("Template could not be extracted!", important=True)
            return False

        gray_template = cv2.cvtColor(roi_template, cv2.COLOR_BGR2GRAY)
        _, mask_template = cv2.threshold(gray_template, 10, 255, cv2.THRESH_BINARY)

        orb = cv2.ORB_create()
        kp_template, des_template = orb.detectAndCompute(roi_template, None)
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        lower_template, upper_template = self._get_hsv_from_roi(roi_template)
        hue_template = (lower_template[0] + upper_template[0]) // 2

        frame = None

        log("waiting for object")
        start_time = time.time()
        while time.time() - start_time < max_secs:
            frame = self.camera_manager.get_frame()

            corrected = self._apply_bias(frame)

            roi_frame, contour_frame = self._extract_largest_object(corrected, is_ideal=False)
            if roi_frame is None or contour_frame is None:
                time.sleep(interval)
                continue

            gray_frame = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
            _, mask_frame = cv2.threshold(gray_frame, 10, 255, cv2.THRESH_BINARY)
            masked_roi = cv2.bitwise_and(roi_frame, roi_frame, mask=mask_frame)

            kp_frame, des_frame = orb.detectAndCompute(masked_roi, None)
            if des_frame is None:
                time.sleep(interval)
                continue

            matches = matcher.match(des_frame, des_template)
            good_matches = len(matches)

            lower_frame, upper_frame = self._get_hsv_from_roi(roi_frame)
            hue_frame = (lower_frame[0] + upper_frame[0]) // 2
            hue_diff = abs(int(hue_frame) - int(hue_template))

            if good_matches >= min_matches and hue_diff <= max_hue_diff:
                frame_marked = frame.copy()
                self._mark_detected_object(frame_marked, contour_frame)

                self._save_result(frame_marked, object_name, mode="wait", status="FOUND")

                if self.test_mode:
                    cv2.imshow("Detection", frame_marked)
                    cv2.waitKey(1000)
                cv2.destroyAllWindows()
                return True

            if self.test_mode:
                debug_frame = frame.copy()
                cv2.drawContours(debug_frame, [contour_frame], -1, (255, 0, 0), 2)
                cv2.putText(debug_frame, f"Matches: {good_matches}, Hue diff: {hue_diff}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow("Detection", debug_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            time.sleep(interval)
        else:
            self._save_result(frame, object_name, mode="wait", status="TIME_NOT_FOUND")

        cv2.destroyAllWindows()
        return False

    def wait_for_shape(self, shape_name:str, interval:float=0.25, max_secs: float=999999.0) -> bool:
        '''
        ==== NEEDS IMPROVEMENT ====
       takes multiple images for as long as the timeout limit is not hit or the shape is not found. If the shape is found within the limit, it exits this function

        Args:
            shape_name (str): the name of the shape (see all available shape names in _detect_shape())
            interval (float, optional): the time in seconds between two pictures (default: 0.25)
            max_secs (float, optional): The most amount of time in seconds, which it is allowed to wait for the shape to be found (default: 999999.0)


        Returns:
            If the shape was found (True) or not (False)
        '''
        frame = None
        log("waiting for shape")
        start_time = time.time()
        while time.time() - start_time < max_secs:
            frame = self.camera_manager.get_frame()

            corrected = self._apply_bias(frame)
            roi, contour = self._extract_largest_object(corrected)
            if contour is None:
                time.sleep(interval)
                continue

            found = False
            approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
            vertices = len(approx)

            if shape_name == "triangle" and vertices == 3:
                found = True
            elif shape_name == "rectangle" and vertices == 4:
                found = True
            elif shape_name == "circle" and vertices > 6:
                found = True

            if found:
                frame_marked = self._draw_circle_on_contour(frame, contour)
                self._save_result(frame_marked, f"shape_{shape_name}", mode="wait", status="FOUND")
                if self.test_mode:
                    cv2.imshow("Detection", frame_marked)
                    cv2.waitKey(1000)
                cv2.destroyAllWindows()
                return True

            if self.test_mode:
                debug_frame = frame.copy()
                cv2.drawContours(debug_frame, [contour], -1, (255, 0, 0), 2)
                cv2.imshow("Detection", debug_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            time.sleep(interval)
        else:
            self._save_result(frame, shape_name, mode="wait", status="TIME_NOT_FOUND")

        cv2.destroyAllWindows()
        return False

    def wait_for_color(self, color_name:str, interval:float=0.25, max_secs:float=999999.0) -> bool:
        '''
        takes multiple images for as long as the timeout limit is not hit or the color is not found. If the color is found within the limit, it exits this function

        Args:
            color_name (str): the name of the color (see all available colors in _get_color_ranges())
            interval (float, optional): the time in seconds between two pictures (default: 0.25)
            max_secs (float, optional): The most amount of time in seconds, which it is allowed to wait for the color to be found (default: 999999.0)

        Returns:
            If the color was found (True) or not (False)
        '''
        hsv_ranges = self._get_color_ranges()

        if color_name not in hsv_ranges:
            log(f"Color '{color_name}' is not supported.")
            return False

        lower, upper = hsv_ranges[color_name]
        frame = None

        log("waiting for color")
        start_time = time.time()
        while time.time() - start_time < max_secs:
            frame = self.camera_manager.get_frame()

            corrected = self._apply_bias(frame)
            hsv = cv2.cvtColor(corrected, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                contour = max(contours, key=cv2.contourArea)
                if cv2.contourArea(contour) > 200:
                    frame_marked = self._draw_circle_on_contour(frame, contour)
                    self._save_result(frame_marked, f"color_{color_name}", mode="wait", status="FOUND")
                    if self.test_mode:
                        cv2.imshow("Detection", frame_marked)
                        cv2.waitKey(1000)
                    cv2.destroyAllWindows()
                    return True

            if self.test_mode:
                cv2.imshow("Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            time.sleep(interval)
        else:
            self._save_result(frame, color_name, mode="wait", status="TIME_NOT_FOUND")

        cv2.destroyAllWindows()
        return False

    def wait_for_shape_and_color(self, shape_name:str, color_name:str, interval:float=0.25, max_secs:float=999999.0) -> bool:
        '''
        ==== NEEDS IMPROVEMENT ====
        takes multiple images for as long as the timeout limit is not hit or the color with the corresponding shape is not found. If the color with the corresponding shape is found within the limit, it exits this function

        Args:
            shape_name (str): the name of the shape (see all available shape names in _detect_shape())
            color_name (str): the name of the color (see all available colors in _get_color_ranges())
            interval (float, optional): the time in seconds between two pictures (default: 0.25)
            max_secs (float, optional): The most amount of time in seconds, which it is allowed to wait for the color with the corresponding shape to be found (default: 999999.0)

        Returns:
            If the color with the desired shape was found (True) or not (False)
        '''
        hsv_ranges = self._get_color_ranges()

        if color_name not in hsv_ranges:
            log(f"Color '{color_name}' is not supported.")
            return False

        lower, upper = hsv_ranges[color_name]

        frame = None
        log("searching for shape and color...")
        start_time = time.time()
        while time.time() - start_time < max_secs:
            frame = self.camera_manager.get_frame()

            corrected = self._apply_bias(frame)
            hsv = cv2.cvtColor(corrected, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            found = False
            contour = None
            if contours:
                contour = max(contours, key=cv2.contourArea)
                if cv2.contourArea(contour) > 200:
                    approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
                    vertices = len(approx)

                    if shape_name == "triangle" and vertices == 3:
                        found = True
                    elif shape_name == "rectangle" and vertices == 4:
                        found = True
                    elif shape_name == "circle" and vertices > 6:
                        found = True

            if found:
                frame_marked = self._draw_circle_on_contour(frame, contour)
                self._save_result(frame_marked, f"shape_{shape_name}_color_{color_name}", mode="wait", status="FOUND")
                if self.test_mode:
                    cv2.imshow("Detection", frame_marked)
                    cv2.waitKey(1000)
                cv2.destroyAllWindows()
                return True

            if self.test_mode:
                debug_frame = frame.copy()
                if contour is not None:
                    cv2.drawContours(debug_frame, [contour], -1, (255, 0, 0), 2)
                cv2.putText(debug_frame, f"Waiting for {shape_name} + {color_name}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow("Wait Detection", debug_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            time.sleep(interval)
        else:
            self._save_result(frame, f"shape_{shape_name}_color_{color_name}", mode="wait", status="TIME_NOT_FOUND")

        cv2.destroyAllWindows()
        return False
