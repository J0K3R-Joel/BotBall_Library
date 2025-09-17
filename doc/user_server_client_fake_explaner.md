# User, Server, and Client – Explanation

This document explains why two users are required for a single purpose, what the overall goal of the system is, and how to set up both the server and the client. It also outlines the hardware requirements needed to run the setup.

---

## 1. Why Two Users for One Purpose?

- **Reasoning**:
  - You can run tests on a single PC using two controllers, without the need for a second person.
  - The system still supports testing with another person on two separate PCs if desired.
  - You don’t need to create example files from scratch, which makes it easier to understand the `FakeR` class.

---

## 1.5 Preparation

asd

---

## 2. Client and Server Usage

### Server Side

You have two options for running the server:

- **Option A: Run via `main.py`**
  
  - Simply follow the steps inside the `main.py` file within the `main` function. The print statement guides you through the process.

- **Option B: Manual Setup**
  
  1. Uncomment everything in the `main` function.
  2. Comment out the `main(None, None)` call.
  3. Uncomment the `fake_main_setup()` line.
  4. Inside the `end_main` function, uncomment the line `communication_instance.disconnect()`.
  5. In the `Comm_Setup` function, replace `"XX"` with the correct IP address of the controller/robot.
  6. Locate the line `PORT_BUTTON = XX` and replace `"XX"` with the port where the (digital) button is connected.

---

### Client Side

You also have two options for running the client:

- **Option A: Run via `main.py`**
  
  - Simply follow the steps inside the `main.py` file within the `main` function. The print statement guides you through the process.

- **Option B: Manual Setup**
  
  1. Uncomment everything in the `main` function.
  2. Comment out the `main(None, None)` call.
  3. Uncomment the `fake_main_setup()` line.
  4. Inside the `end_main` function, uncomment the line `communication_instance.disconnect()`.
  5. In the `Comm_Setup` function, replace `"XX"` with the server’s IP address.
  6. In the `Instancer_Setup` function, locate the parameter `controller_standing=XX` and replace `"XX"` with:
     - `True` if the controller is standing upright.
     - `False` if the controller is lying flat.
  7. Look for the `PORT_MOTOR_**` lines (where `**` is FR, FL, etc.) and replace `"XX"` with the correct port for each motor.
     - **Hint:** Each motor should drive forward (clockwise) when given a positive value.

---

### Interaction

Once both server and client are set up, you can run the programs. The client will:

- Drive forward in a straight line for a while.
- Perform a (rough) 180° turn.
- Repeat this sequence continuously.

At any time, you can press the button on the server to make the client drive backward. This simulates the usage and capabilities of the `FakeR` class. You can also pause the main program whenever you wish.

---

## 3. Hardware Requirements

- **Server Hardware**:
  
  - Network connection
  - (Digital) button

- **Client Hardware**:
  
  - Robot chassis with 4 mecanum wheels
    - (Alternative: 2 rubber wheels or another setup — in this case, adapt the class and update the ports)
  - Motors with correct port mappings
  - Network connection

---

## 4. Summary

- Two users are provided to allow flexible testing (single PC with two controllers or two PCs with two people).
- The system demonstrates and tests the functionality of the `FakeR` class.
- Both client and server can be run either directly via `main.py` or through manual setup.
- Minimal hardware is required: a server with a button and a client with a robot platform.

---

## 5. Things to consider

- You will need the original instance from the `main` method for `communication` everywhere, where you want to send or check for messages. You will need the original instance of `p_event` everywhere, where you want to be able to pause, when a `high` priority message arrives. For example:
  - If you write a new main function and tell the `{RoboCommunicator_instance}.on_new_main` function the function which should be executed on a `new_main` priority message and you want to use communication inside of the new main you just defined, then add the parameter. This will look (e.g.) something like this: `communication.on_new_main(this_will_be_the_new_main_name, communication)`
  - If you are creating a function which should respond to a `high` priority message and tell the `{RoboCommunicator_instance}.on_high_priority` function the high priority function which you just should be executed on a `high` priority message and you want to be able to pause inside of main (function) you are in, then add the parameter. This will look (e.g.) something like this: `communication.on_high_priority(this_will_be_the_high_priority_function_name)`
  - If you want both (a new main with `high` priority functionality (to be able to pause at any time)), then you should implement both. This will look something like this: `communication.on_new_main(this_will_be_the_new_main_name, p_event, communication)`
  - If your new main function needs more than those parameters, then you are free to do so by just adding the paramets after the function name.
