# CameraManager Class – Explanation & Usage

- **Author:** Joel Kalkusch

- **Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)

- **Creation Date:** 2025-09-15

---

## Overview

The `CameraManager` class provides a **thread-safe wrapper around OpenCV’s `VideoCapture`**.  
It ensures:

- Proper **warm-up** of the camera (avoiding initial dark frames).

- Safe **multi-threaded access** via locks.

- Reliable **frame retrieval with retries**.

- Clean **release** of camera resources.

This class acts as the **foundation for higher-level detectors**, such as:

- `CameraBrightnessDetector`

- `CameraObjectDetector`

---

## Requirements

- Python 3

- OpenCV (`cv2`)

- `threading` & `time` (standard library)

- Custom `logger` module

---

## Class

### Constructor

```python
cam = CameraManager(cam_index: int = 1,
                     warmup_frames: int = 30,
                     warmup_delay: float = 0.05 )
```

- **cam_index:** The index of the camera (usually `0` or `1`).

- **warmup_frames:** Number of initial frames to skip during warmup (default: 30).

- **warmup_delay:** Delay in seconds between warmup frames (default: 0.05).

---

## Methods

### `_warmup()`

```python
cam._warmup()
```

- Discards a number of frames at startup.

- Prevents capturing very dark/noisy images.

- Called automatically by `get_frame()`.

---

### `get_frame(retries=5, delay=0.05)`

```python
frame = cam.get_frame()
```

- Captures a single frame.

- Retries up to `retries` times if frame capture fails.

- Waits `delay` seconds between retries.

- Returns: **OpenCV image (`numpy.ndarray`)**.

- Raises: `RuntimeError` if no valid frame could be captured.

---

### `release()`

```python
cam.release()
```

- Releases the camera resource.

- Closes all OpenCV windows.

- Resets warmup state.

- Must be called when finished using the camera.

---

## Example Usage

### 1. Basic frame capture

```python
from camera_manager import CameraManager 
cam = CameraManager(cam_index=0) 

try: 
    frame = cam.get_frame()
    cv2.imshow("Live Frame", frame)
    cv2.waitKey(0) 
finally: 
    cam.release()
```

---

### 2. Integration with Detector

```python
from camera_manager import CameraManager
from camera_brightness_detector import CameraBrightnessDetector

cam = CameraManager(cam_index=0) 
detector = CameraBrightnessDetector(camera_manager=cam)
if detector.is_black_in_frame(): 
    print("Black detected in frame!") 
cam.release()
```

---

## Tips

- Use **`cam_index=0`** for internal webcam, `1` or higher for external USB cameras.

- Increase **`warmup_frames`** if your camera needs more time to stabilize exposure.

- Always call **`release()`** to avoid locked camera devices.

- For multi-threaded applications, `CameraManager` ensures safe access with locks.

---

## Conclusion

The `CameraManager` is a **robust and minimal wrapper** for OpenCV’s `VideoCapture`.  
It takes care of warmup, retries, and resource handling – making it the ideal **base class for vision-based robotics projects**.
