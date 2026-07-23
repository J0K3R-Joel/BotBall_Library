# Ideas for the future

This file has ideas for future use or methods that can be programmed at some point in the future. 

You can try to create implementations for those ideas and send them to me alongside proof and afterwards I will implement it so every user can use your own method. (Feel free to add your name inside the docstring inside of the function ;) ) 

You can also send me your own ideas so I can implement them in here as well for future generations to create an implementation of the idea.

---

## Servo-like Motor

Implement support for servo-like motors that combine the simplicity of servo positioning with the flexibility of DC motors. The goal is to provide an intuitive API for precise position control while remaining compatible with the existing motor architecture.

#### Notes

- Evaluate whether this should be implemented as a separate motor class or integrated into the existing motor API.

------

## Magnetometer Support

Document that the KIPR firmware currently provides non-functional magnetometer functions because they appear to access incorrect memory locations. Investigate whether this issue can be resolved within the library. If a fix is not possible, clearly document the limitation and describe the intended functionality and potential use cases.

#### Notes

- Verify whether the issue originates from the firmware or the Python bindings.
- Document possible workarounds if available.

------

## Camera-Based Object Size Estimation

Combine camera object detection with distance sensor measurements to estimate the physical size of detected objects on the standard competition field.

#### Notes

- Useful for distinguishing between similar objects at different distances.
- Evaluate calibration requirements.

------

## RobotCommunicator Thread Support

Verify that the `RobotCommunicator` functions correctly when executed inside a separate thread.

#### Notes

- Ensure communication remains reliable under concurrent execution.

------

## High Priority Execution

Verify whether high-priority tasks are executed outside the thread as intended and ensure the current implementation behaves consistently.

#### Notes

- Review the interaction between the scheduler and threading.

------

## Basic Setup Video

Create an introductory video demonstrating the assembly of the standard robot construction used with the library.

#### Notes

- Focus on hardware assembly rather than software configuration.

------

## Generic Sensor Wait Helper

Implement a generic helper function for methods that accept a `millis` parameter. The helper should repeatedly execute a given method until a specified sensor reaches a target value. The monitored sensor, target value, and all remaining method arguments should be passed to the helper.

#### Notes

- Forward remaining parameters using `*args` and `**kwargs`.
- Reduce duplicated waiting logic across the library.

------

## Dynamic Straight Driving Using GMPC

Investigate whether reliable straight-line driving can be achieved using `gmpc()` without requiring manual calibration or motor adjustment values.

#### Notes

- Compare accuracy against the current calibration-based approach.

------

## Automatic Motor Speed Calibration

Research and implement a mechanism that compensates for differences in motor performance by automatically adjusting individual `default_speed` or `max_speed` values.

#### Notes

- Consider integrating automatic motor adjusters.
- Ensure all motors achieve similar real-world speeds.

------

## Automatic Communication Instance Detection

Remove the requirement that communication instances must share the same variable name across an entire file when using High Priority or New Main. Investigate whether `FakeR` can automatically detect and manage the correct communication instance.

#### Notes

- Detect communication instances by type rather than variable name.
- Introduce a wrapper class if necessary.
- Automatically restore the correct instance after `stop_manager.check_stopped()`.

------

## Button Long Press API

Extend the `Button` class with a long-press API that accepts a dictionary mapping press durations (in milliseconds) to callback functions. Optionally return the press duration when no callbacks are provided.

#### Notes

- Support multiple duration thresholds.
- Add an optional mode that waits until the button is pressed before beginning duration tracking.

------

## Improved Motor Scheduler Timing

Improve thread synchronization in the motor scheduler by tracking the start time of the latest scheduled function for each motor port. When a new function replaces the current one, wait only for the remaining portion of the required delay instead of restarting it.

#### Notes

- Compare this approach against always waiting a fixed 500 ms after replacement.
- Choose the implementation that provides the most predictable behavior.

------

## Library Explainers

Write additional documentation explaining important concepts, design decisions, and internal mechanisms of the library.

#### Notes

- Focus on frequently misunderstood features.
- Include practical examples where appropriate.

------

## Bias File Persistence

Ensure that all modules responsible for loading or creating bias files raise an exception when the required file is missing. This helps preserve calibration data across library reinstalls.

#### Notes

- Verify that the installation script does not overwrite existing bias files.

------

## Rename "Mechanum" to "Mecanum"

Replace every occurrence of the incorrect spelling **"mechanum wheel"** with the correct term **"mecanum wheel"** throughout the library.

#### Notes

- Update both documentation and source code where applicable.

------

## Documentation Terminology Update

Replace the term **"rubber wheels"** with **"Solarbotics wheels"** throughout the documentation.

#### Notes

- Ensure terminology remains consistent across all guides.

------

## Spiderweb Autonomous Navigation

Develop a Q-learning-based navigation system ("Spiderweb") that allows users to specify only target coordinates while the robot automatically determines and follows an optimal path.

#### Notes

- Investigate reinforcement learning approaches.
- Design the API to remain simple for end users.

------

## Turn Alignment Functions

Implement helper functions such as `turn_by_corner()`, `turn_by_front()`, `turn_by_back()`, and potentially `turn_by_side()` for alignment-based turning.

#### Notes

- Document these functions in the **"How Motors Work"** section.

------

## Battery Usage Tracker

Implement a battery monitoring system that estimates the energy required to execute a program and prevents execution if the remaining battery capacity falls below a configurable threshold.

#### Notes

- Investigate methods for estimating energy consumption accurately.

------

## Brightness Sensor Terminology

Replace all occurrences of `light_sensor` with `brightness_sensor` throughout the library and update all dependent APIs accordingly.

#### Notes

- Preserve backwards compatibility where possible.

------

## BotBall Platform Notes

Create a dedicated documentation section summarizing important platform-specific observations, limitations, and best practices for Botball development. This section should serve as a central reference for issues that affect robot behavior but are not directly caused by the library.

#### Notes

- Battery voltage affects motor performance, causing motors to run at different speeds.
- The KIPR magnetometer implementation currently appears to access incorrect memory locations.
- Reimplementing motor control from scratch introduces excessive delays.
- Continuously expand this section as additional platform-specific behaviors and limitations are discovered.

