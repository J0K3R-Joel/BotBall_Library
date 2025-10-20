# CameraObjectDetector Class – Explanation & Usage

- **Author:** Joel Kalkusch

- **Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)

- **Date of creation:** 2025-09-15

---

## Overview

The `CameraObjectDetector` class provides **object detection with a camera** based on:

- **Bias correction:** Adjusts images according to lighting conditions.

- **Object extraction:** Finds the largest object in a frame.

- **Detection modes:** By shape, by color, by known object, or by combined criteria.

- **Waiting modes:** Continuously checks until an object/shape/color appears (timeout).

- **Result saving:** Every detection attempt is stored for later analysis.

It is intended for **robotics vision tasks** such as recognizing shapes, detecting colors, or matching known objects in dynamic environments.

---

## Requirements

- Python 3

- OpenCV (`cv2`)

- NumPy (`numpy`)

- Custom `logger` module

- `CameraManager` (selfmade camera wrapper)

---

## Class

### Constructor

```python
detector = CameraObjectDetector(camera_manager: CameraManager = None,
                                 test_mode: bool = False )
```

- **camera_manager:** Instance of `CameraManager` (mandatory for live camera input).

- **test_mode:** Enables debug windows with live visualization.

---

## Features

### Lighting & Bias Handling

- **`_capture_white_real()`** – Captures a reference image of a white surface for calibration.

- **`_compute_lighting_bias()`** – Computes HSV bias between ideal and real lighting.

- **`_apply_bias(image)`** – Applies bias correction to an input frame.

- **`_save_corrected_background()`** – Stores a corrected background image for debugging.

### Object Extraction & Analysis

- **`_extract_largest_object(frame, is_ideal=False)`** – Finds largest object contour and ROI.

- **`_mark_detected_object(frame, contour)`** – Draws bounding shapes around detected object.

- **`_detect_shape(contour)`** – Basic shape classification (triangle, rectangle, circle, …).

- **`_get_hsv_from_roi(roi)`** – Extracts HSV color range from a region of interest.

- **`_get_hsv_stats(roi)`** – Returns HSV median of ROI.

### Object Dictionary

- **`_build_object_dict()`** – Loads all sample objects from `/usr/lib/bias_files/object_detector/objects`.

- Allows recognition of custom trained objects.

### Color Ranges

- **`_get_color_ranges()`** – Predefined HSV ranges for red, green, blue, yellow, orange, purple, black, and white.

---

## Detection Methods (One-Shot)

### Shape

`detector.find_by_shape("triangle")`

Detects if a **triangle**, **rectangle**, or **circle** is visible.

### Color

`detector.find_by_color("blue")`

Detects if a predefined color is present.

### Object

`detector.find_by_object("cup", min_matches=30, max_hue_diff=10)`

Matches current frame with stored object templates using ORB feature matching.

### Shape + Color

`detector.find_by_shape_and_color("circle", "red")`

Detects an object with **both shape and color** constraints.

---

## Waiting Methods (Continuous)

### Object

`detector.wait_for_object("cup", interval=0.25, max_secs=30)`

Waits until the object is seen or timeout occurs.

### Shape

`detector.wait_for_shape("rectangle", max_secs=15)`

Continuously looks for a rectangle.

### Color

`detector.wait_for_color("green", max_secs=20)`

Waits until a green object is found.

### Shape + Color

`detector.wait_for_shape_and_color("triangle", "yellow", max_secs=25)`

Waits for a yellow triangle to appear.

---

## Result Saving

Every detection (found or not found) is **saved automatically** under:

`/usr/lib/bias_files/object_detector/results/run_<timestamp>/`

File naming format:

`<function_label>_<FOUND | NOT_FOUND | TIME_NOT_FOUND>.jpg`

This enables debugging and offline analysis of all detection attempts.

---

## Typical Workflow

1. **Initialize detector:**
   
   ```python
     cam = CameraManager()
     detector = CameraObjectDetector(camera_manager=cam, test_mode=True)
   ```

2. **Calibration:**
   
   - Place a white sheet in front of the camera.
   
   - Run the program
   
   - Ensure you have `white_ideal.png` for comparison.

3. **Detect features:**
   
   - `detector.find_by_color("red")`
   
   - `detector.find_by_object("bottle")`
   
   - `detector.wait_for_shape("circle", max_secs=10)`

4. **Check saved results** in the results directory.

----

## Adding new object examples

1. Take the wanted object and lay it on a white piece of paper

2. Turn off the lights and put the blinds down

3. Take your (phone) camera and place it on a height where the entire object is seen (at least around about 21 cm in the air)

4. Make it that your phone is laying on something so the picture will not be wobbly

5. Turn on the flashlight (of your phone) and take a picture of the object

6. Create a new folder with the name that you want to call the object in [../src/bias/object_detector/objects](../src/bias/object_detector/objects)

7. Add every picture you took inside that folder



## Conclusion

The `CameraObjectDetector` provides a **flexible and modular vision system** for robotics:

- **Shape / Color / Object detection**

- **Bias correction for lighting variations**

- **One-shot detection or continuous waiting**

- **Automatic result saving for debugging**

It is ideal for **autonomous robots, competition tasks, and research projects** where visual feedback is required.
