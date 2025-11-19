# Known Issues & Solutions

### Issue ID: 001

- **Title:** `driveR` not working correctly  

- **Category:** Hardware / Software  

- **Affected Components:** Motors

- **Description:**  
  every method of `driveR` is not driving correctly where you want to drive to. For example when you want to `drive_straight` it will not drive straight 

- **Symptoms / Indicators:**  
  
  - Spinning, wrong direction, ... -> driving anywhere where it should not go

- **Cause:**  
  Ports not plugged in correctly

- **Solution / Workaround:**  
  Make sure that every Port where the motors for driving are plugged in is getting a positive value when driving straight 

- **Status:** Resolved

---

### Issue ID: 002

- **Title:** `TabError`

- **Category:** Software 

- **Affected Components:** Code (Python)

- **Description:**  
  When compiling your code you get an `TabError` 

- **Symptoms / Indicators:**
  
  - Exception thrown

- **Cause:**  
  incorrect spaces used (either tab or 4 spaces)

- **Solution / Workaround:**  
  You need to write your entire code with the same type of indentation. If the code is prewritten, then you need to use the same indentations. If you get this error, then you need to remove all indentations of the line(s) where this error occures and replace them with the same indentation type, so the entire code has the same spacing type

- **Status:** Resolved

---

### Issue ID: 003

- **Title:** `Cannot assign adress` Error

- **Category:** Software

- **Affected Components:** Communication

- **Description:**  
  When compiling your code you get an `Cannot assign adress` error

- **Symptoms / Indicators:**
  
  - Exception thrown

- **Cause:**  
  incorrect IPv4-Adress usage in the client / server architecture   

- **Solution / Workaround:**  
  Make sure that the IPv4 Adress is right. Also make sure that the robot is in the desired WIFI 

- **Status:** Resolved

---

### Issue ID: 004

- **Title:** `Adress already in use` Error

- **Category:** Software

- **Affected Components:** Communication

- **Description:**  
  When compiling your code you get an `Adress already in use` error

- **Symptoms / Indicators:**
  
  - Exception thrown

- **Cause:**  
  Adress of the server is already existing 

- **Solution / Workaround:**  
  If there are more than one team participating in the competition using the same router, then make sure that every team has their own IP Addresses so two (or more) teams cannot use the same IPv4 Addresses
  
  If this is not the case, then you need to wait for a while, since the IPv4 Address is reserved for a while. After some time, the IPv4 Address will be able for use again.

- **Status:** Resolved

---

### Issue ID: 005

- **Title:** Program won't stop running

- **Category:** Software

- **Affected Components:** KISS IDE

- **Description:**  
  By clicking the `Stop` - Button nothing happens

- **Symptoms / Indicators:**

  - After clicking the `Stop` - Button, the text won't change to `Run`  

- **Cause:**  
  
  There are mainly three reasons:
  
  1. Controller's battery is empty
  2. Controller or the PC is in the wrong WIFI
  3. In a loop that has no waiting time
  
- **Solution / Workaround:**  
  
  1. Controller's battery is empty -> Switch the empty battery with a full battery
  2. Controller or the PC is in the wrong WIFI -> Get in the same WIFI
  3. In a loop that has no waiting time -> The solution to this step is split into steps:
     1. If it won't exit out of the loop and you do not know how it is able to leave the loop, you need to unplug the battery.
     2. Plug in the battery
     3. Detect where it has the issue when leaving the loop
     4. Change the loop accordingly (most of the time a small sleeping time is enough)
     5. Compile and you are good to go! 
     6. If the issue keeps reappearing, then you either got the wrong loop changed or there are multiple problematic loops.  
  
- **Status:** Resolved

---

### Issue ID: 006

- **Title:** Permission denied when running script
- **Category:** Software
- **Affected Components:** entire BotBall_Library 
- **Description:**  
  When running the main script via `sudo bash config.sh` you get tons of `Permission denied` errors. 
- **Symptoms / Indicators:**
  - You are not able to `chmod` a file on the USB-stick
  - Many `Permission denied` errors after running `sudo bash config.sh` in the terminal
- **Cause:**  
  - Unknown, since the error only occurs on some USB-sticks.
- **Solution / Workaround:**  
  1. Plug the USB-Stick containing the BotBall_Library into the controller
  2. Get into the BotBall_Library folder on your USB-stick
  3. Copy (or cut) the folder and paste it into any other directory where you are allowed to paste it
  4. run the script as usual (via `sudo bash config.sh`) 
- **Status:** Resolved

---

### Issue ID: 007

- **Title:** Not booting after installation
- **Category:** Software
- **Affected Components:** controller
- **Description:**  
  After successfully running the main script via `sudo bash config.sh` and shutting off the controller, it will boot but it will not progress after a terminal window
- **Symptoms / Indicators:**
  - empty terminal window will not go away, even after waiting for minutes
  - You can not write into the terminal window
- **Cause:**  
  - Unknown, but it should not be a issue of the BotBall Library
- **Solution / Workaround:**  
  - No solution available
  - The only thing you can do is to wipe out the micro SD card and start all over again
- **Status:** Open

---