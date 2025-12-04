# User Explainer

This file will tell you everything important about every user. You can find the users inside the KISS IDE. If you are uncertain about what I mean when I talk about "users", then consider reading the [./Introduction.md](./Introduction.md) file.

In every user there will and should be the `logger.py` file, since with this user you are able to get a better error message and even log the error inside a file (check out [./Folder_Paths.md](./Folder_Paths.md)) so you are able to know what went wrong, even after running the program again, rebooting the controller, ... 

---

### Base

In this user every class is included. This makes you able to experiment across every class. Since this user has every (python) file included, you can do everything here that you can do in other users. The only difference is that in this user there is less of a template provided

---

### BIAS

In this user every class that needs some kind of calibration (included with classes that they depend on) is included. In the `main.py` there is a template which you can use for calibration. Note that not everything is included in this template, for example `driveR.{driver_class_name}.calibrate_mm_per_sec()` and `driveR.{driver_class_name}.calibrate_distance()` are not included. Check out the [./Calibrations.md](./Calibrations.md) file to know more about this topic.


---

### Camera

In this user there are only classes which have to do with the camera. This is so you can experiment with the possibly best and most future oriented feature: the camera. With the camera you could make an AI which tells you where you are at and some problems that might have occurred during a run. Unfortunately this does not exist while I am editing this file, but if someone creates this, then it would definitely be the biggest game changer.

---

### COMM

In this user you can find everything related to communication between two controllers with additionally some classes for helping you to test some things out . To experiment with this class you obviously need another controller. Please consider that communication (at least at the time of the creation of this file) is only available between ONE client and ONE server and you need to specify which controller is the server / client. There is not really a difference between who the server or client is. Server and client need to be in the same WIFI, otherwise they cant find the other controller. 

---

### Fake-Client

This user is an example on how communication can look like on the client side. This provides an example of the complex `FakeR` class, which let's you be able to pause the main at any given moment using `high_priority` or `new_main`. For more information get into the [./explainer/user_server_client_fake.md](./explainer/user_server_client_fake.md) file.

---

### Fake-Server

This user is an example on how communication can look like on the server side. This provides an example of the complex FakeR class, which let's you be able to pause the main at any given moment using `high_priority` or `new_main`. For more information get into the [./explainer/user_server_client_fake.md](./explainer/user_server_client_fake.md) file.

---

### WIFI

The WIFI user provides you with the `commU` class and every class that is linked to this class. This provides you necessary functionality concerning the WIFI. 

---