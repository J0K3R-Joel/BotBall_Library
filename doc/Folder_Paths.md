# Important Folder Paths

This file tells you every necessary and good-to-know path which is on the controller. To get to the folders you can follow [./Controller_Guide.md](./Controller_Guide.md). Theoretically you can just plug in a keyboard and type in the terminal to access every path, but for the less experienced user this is a little bit too advanced, so you might just get into the file explorer. 

---

## User

The base folder structure of every user is the following:

#### /home/kipr/Documents/KISS/{user_name}/{project_name}

this path is seperated into 4 other directories:

###### `./bin`: Every file in here is shown inside the KISS IDE

- in here you are able to find the "botball_user_program" (at least when you are executing your source code from the KISS IDE). This file is a link to another file, which setups everything the KISS IDE needs to execute the `main.py` file inside the `./bin` folder of the corresponding user inside the corresponding project 

###### `./src`: If the controller gets executed on the hardware (the controller itself), it will take the files from here

- in here you will most likely find a `__pycache__` folder. This is normal in python due to increasing the performance of the file. For more information you can look at https://stackoverflow.com/questions/16869024/what-is-pycache 

###### `./data`: Uncertain, but i suppose that temp files will get stored in here, afterwards they will get deleted 

###### `./include`: No idea

On the other hand there is another file inside the base folder structure called `project.manifest`. In here you are able to find which programming language is linked to the user's name (`{user_name}`)  

---

Every user that exists is also written down in:

#### /home/kipr/Documents/KISS/users.json

In here you can find the name of every user with the corresponding level of experience (which just changes the functionality of the KISS IDE).  

---



## Overall

If you are using my library, then the following base folder is necessary to know:


#### /usr/lib

in here you can find the following:

###### `./Local_STD_WIFI.conf`: Private network configuration file

- in here you can specify which WIFI (ssid and password) you want to use for you local WIFI. Internet connection is not necssary, except you implement something where you want / need WIFI

###### `./bias_files`: When calibrating, every bias will get stored somewhere in here

- calibrations for e.g.: gyro, accelerometer, camera, distance, light/brightness values, ...

###### `./logger_log`: Everything that has to do with logging gets sent into here

-  log backups and the log file itself (which gets updated when you use the logger.py file using the `log()` function)

---





