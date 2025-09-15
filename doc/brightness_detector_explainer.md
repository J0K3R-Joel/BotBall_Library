# CameraBrightnessDetector Class – Explanation & Usage

- **Author:** Joel Kalkusch

- **Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)

- **Creation Date:** 2025-09-15

---

## Overview

The `CameraBrightnessDetector` class provides methods for detecting brightness levels in camera frames.  
It divides frames into configurable tiles, applies threshold-based analysis, and can detect **black** or **white** areas in entire frames, regions (left/right/top/bottom), or centered zones.

Additionally, it supports:

- **Bias calibration** (automatic threshold adjustment based on ambient brightness).

- **Tile-based detection** for fine-grained analysis.

- **Saving and visualizing results** for debugging/test purposes.

This makes it a versatile tool for vision-based robotics projects on the Wombat/Wallaby platform.

---

## Requirements

- Python 3

- OpenCV (`cv2`)

- NumPy (`numpy`)

- Custom `logger` module

- `CameraManager` (custom camera wrapper)

Import into your project:

```python
from camera_brightness_detector import CameraBrightnessDetector
```

---

## Class

### Constructor

```python
detector = CameraBrightnessDetector( camera_manager: CameraManager = None,
                                     tiles_x: int = 1,
                                     tiles_y: int = 1,
                                     threshold_brightness: int = 127,
                                     threshold_black: int = 50,
                                     threshold_white: int = 200, 
                                     test_mode: bool = False, 
                                     use_bias: bool = False )
```

- **camera_manager:** A `CameraManager` instance that provides frames.

- **tiles_x, tiles_y:** Number of tiles (horizontal & vertical).

- **threshold_brightness:** Default brightness threshold for "bright" detection.

- **threshold_black:** Pixel intensity cutoff for "black".

- **threshold_white:** Pixel intensity cutoff for "white".

- **test_mode:** If `True`, shows frames with visual markers.

- **use_bias:** If `True`, thresholds are adjusted dynamically using bias calibration.

---

## Methods

### Configuration

- **`set_x_tiles(n)`** – change number of horizontal tiles.

- **`set_y_tiles(n)`** – change number of vertical tiles.

- **`set_test_mode(flag)`** – enable/disable test mode visualization.

### Frame-wide detection

- **`is_black_in_frame()`** – check if *any black* is present in the whole frame.

- **`is_white_in_frame()`** – check if *any white* is present in the whole frame.

### Regional detection

- **`is_black_left()` / `is_black_right()`** – detect black in left/right half.

- **`is_black_top()` / `is_black_bottom()`** – detect black in top/bottom half.

- **`is_white_left()` / `is_white_right()`** – detect white in left/right half.

- **`is_white_top()` / `is_white_bottom()`** – detect white in top/bottom half.

- **`is_color_centered(color, range_percent, orientation)`** – detect black/white in a centered band (horizontal, vertical, or both).

### Tile-based detection

- **`analyze_frame()`** – return per-tile brightness info (`mean`, `bright`, `black`, `white`).

- **`find_black()`** – return all tile positions containing black.

- **`find_white()`** – return all tile positions containing white.

### Waiting

- **`wait_black(max_secs)`** – block until black is detected (returns tile positions).

- **`wait_white(max_secs)`** – block until white is detected (returns tile positions).

### Calibration

- **`calculate_brightness_bias(frames, delay)`** – calculate and save average brightness bias (uses multiple frames).

- **`get_brightness_bias()`** – load stored bias from file (or return cached value).

---

## Typical Use Cases

### 1. Simple black/white detection in full frame

```python
detector = CameraBrightnessDetector(camera_manager=cam) 
if detector.is_black_in_frame(): 
    print("Black detected!") 

if detector.is_white_in_frame(): 
    print("White detected!")
```

### 2. Regional detection (left/right/top/bottom)

```python
if detector.is_black_top(): 
    print("Black detected at top") 

if detector.is_white_bottom(): 
    print("White detected at bottom")
```

### 3. Tile-based search

```python
detector = CameraBrightnessDetector(camera_manager=cam,
                                    tiles_x=4, 
                                    tiles_y=3) 
black_tiles = detector.find_black() 
print("Black tiles at:", black_tiles)
```

### 4. Waiting for event

```python
print("Waiting for white object...") 
tiles = detector.wait_white(max_secs=10) 

if tiles: 
    print("White detected at:", tiles) 
else: 
    print("Timeout, no white detected.")
```

### 5. Bias calibration

```python
bias = detector.calculate_brightness_bias(frames=100) 
print("New brightness bias:", bias)
```

---

## Tips

- **Bias calibration:** Run `calculate_brightness_bias()` in the actual environment to improve reliability.

- **Tiles:** Use more tiles (e.g., 4x3) for finer granularity, fewer tiles for performance.

- **Test mode:** Activate `test_mode=True` to visualize detection overlays during debugging.

- **Result saving:** All detection results are automatically stored in `/usr/lib/bias_files/brightness_detector/results_brightness/`.

---

## Conclusion

The `CameraBrightnessDetector` class provides powerful brightness-based vision detection with:

- Frame-wide and regional black/white detection

- Fine-grained tile analysis

- Configurable thresholds and auto-bias calibration

- Visualization and result-saving features

This makes it ideal for robotics tasks such as **line detection, contrast tracking, or object presence recognition**.
