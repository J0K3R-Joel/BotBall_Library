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

- **Title:** `Indentation Error`

- **Category:** Software 

- **Affected Components:** Code (Python)

- **Description:**  
  When compiling your code you get an `indentation error` 

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
  If there are more than one team participating in the competition using the same router, then make sure that every team has their own IP Adresses so two (or more) teams cannot use the same IPv4 Adresses
  
  If this is not the case, then you need to wait for a while, since the IPv4 Adress is reserved for a while. After some time, the IPv4 Adress will be able for use again.

- **Status:** Resolved

---
