# Controller Explainer

This file acts as a guide for every necessary information given on the controller and how to get to the information (step-by-step).

## Starting page

Every headline from now on will begin on the starting page, which looks like this:

![](.\img\controller_starting_page.jpg)

You are able to see this page when 

- turning the controller on

- if you already clicked on a button, you can

  - click a button called `Home` 
  - click an `Exit` / `Back` button until you reach this page again

**Hint**: In the bottom right corner you can see two symbols. The left symbol is to see the current battery charge. The right symbol shows you (if it is green) that it is connected to a wifi and (if it is orange) it tells you that it is not connected to any network

  

  ## Shutting down

##### Reason

It is recommended to always safely shut down the controller this way. It will close everything safely.

##### Navigation

1. Click the `Shut Down` button in the top center of the screen ![](./img/shut_down_page.png)
   Afterwards you need to accept or decline your choice

  ## Rebooting



##### Reason

Sometimes some problems will be fixed when rebooting the controller

##### Navigation

1. Click the `Reboot` button ![](./img/reboot_page.png)Afterwards you need to accept or decline your choice

## Exiting GUI

##### Reason

Sometimes you want to get to the home-screen of the controller. If you are using my library, you can access the logger file (located in the file explorer in `/usr/lib/logger_log`) this way for example. Another example would be to access the bias files (located in the file explorer in `/usr/lib/bias_file`).

##### Navigation

1. Click the `Settings` button ![](./img/hide_page.png)

2. Click the `Hide UI` button ![](./img/hide_interface_page.png)

## Viewing WIFI settings

##### Reason

If you want communication or simply connect to the controller to edit your code, you need to establish a connection with the controller. If you do not know how to connect to the robot, go visit [./Introduction.md](./Introduction.md).

##### Navigation

You got two choices:

1. Only look up the current configuration:

   1. Click the `About` button ![](./img/about_page.png)

      Here you can see every important information regarding the current router connection ![](./img/about_interface_page.png)

      - **Name of the controller**: Given by the institution kipr for each controller
      - **Wifi Name**: Name of the Wifi the controller is currently connected to
      - **Wifi Password**: Passoword of the Wifi the controller is currently connected to
      - **IPv4 Address**: The IPv4 Address of the controller given by the Wifi router
      - (Event Mode): Conncetion with the robot is disabled here. You should just leave it on `disabled` since there are no pros of using it

2. Look at the current configuration and change of the configuration:

   1. Click the `Settings` button ![](./img/wifi_page.png)
   
   2. Click the `Advanced` button ![](./img/wifi_advanced_page.png)
   
   3. Click the `Network` button ![](./img/wifi_network_page.png)
   
      Here you can see every important information regarding Wifi ![](./img/wifi_network_interface_page.png)
   
      - **Frequency**: Band width the controller has to look at for the desired Wifi
      - **Current Wifis**: Every wifi with the same frequency will be shown here (you are able to connect to them)
      - **Old Wifis**: Every wifi you were connected
      - **Wifi Mode**: Three different modes you can set the controller
        - _Client Mode_: Controller is able to connect to a different wifi
        - _AP Mode_: Controller creates it's own wifi (you are able to connect to it)
        - _Event Mode_: No connection whatsoever is allowed
      - **Wifi Name**: Name of the Wifi the controller is currently connected to
      - **Wifi Password**: Passoword of the Wifi the controller is currently connected to
      - **IPv4 Address**: The IPv4 Address of the controller given by the Wifi router

## Run local Programs

##### Reason

When you are at the BotBall (ECER / GCER) event you HAVE TO execute all your programs on the controller and not on the PC!

##### Navigation

1. Click the `Programs` button ![img](./img/programs_page.png)

2. Click on the User and Project file. This makes it, so the `main.py` file gets executed.![](./img/programs_user_page.png)

3. Click the `Run` button to execute the code ![](./img/programs_run_page.png)



## Viewing Sensor / Motor / Servo values

##### Reason

1. **Motor**: You can test out, where a motor drives (forward, backward) when changing the value (positive, negative). You can also see the motor counter
2. **Servo**: You can enable / disable servos while also seeing the current value and changing the value / position
3. **Sensors**: You can see every analog, digital and inbuilt sensor values to test the values out

##### Navigation

1. Click on the `Motors and Sensors` button![](./img/values_page.png)

2. From here on, there are 5 options:

   1. ###### Motors:

       Click the `Motors` button ![](./img/values_motors_page.png)

       Here you can see every important information regarding motors.

       ![](./img/values_motors_interface_page.png)

       - **Port**: The physical location where the motor is plugged in. You can switch the port on the interface by clicking on it, if you want to access another port.
       - **Pointer of movement**: The visualization of the "Value of movement". Turn the pointer to one direction to make the motor go forward. Turn it the other way for going backward
       - **Value of movement**: Shows you where it is going (positive -> forward; negative -> backward)
       - **Position counter**: Values of movement added together 
   
   
   
   2. ######  Servos:
   
       Click the `Servos` button![](./img/values_servo_page.png)
   
       Here you can see every important information regarding servos.
   
       ![](./img/values_servo_interface_page.png)
   
       - **Port**: The physical location where the servo is plugged in. You can switch the port on the interface by clicking on it, if you want to access another port.
       - **Pointer of movement**: The visualization of the "Value of movement". Turn the pointer to one direction to make the servo go one way and turn it the other way to change it to the other way.
       - **Value of movement**: Shows you the current value it is set to
       - **On / Off**: Being able to change the value (Enable) or not being able to change the value (Disable)
   
  
   3. ###### Sensor Graph: 
   
       Click the `Sensor Graph` button 
   
       ![](./img/graph_page.png)
   
       Here you can see every important information regarding the visual difference between two sensors ![](./img/graph_interface_page.png)
   
       - **Port 1**: Sensor 1 with the corresponding port number
       - **Port 2**: Sensor 2 with the corresponding port number
       - **Value Port 1**: Value of Sensor 1
       - **Value Port 2**: Value of Sensor 2
       - **Graph Values**: Both values shown on a graph (they got different colors to differentiate)
   
   4. ###### Sensor List:
   
       Click the `Sensor List` button ![](./img/list_page.png)
   
       Here you can see every important information regarding every sensor on the controller ![](./img/list_interface_page.png)
   
       - **Sensors / Ports**: Every single sensor on the controller 
       - **Values**: The current value of the corresponding sensor
       - **Slider**: Being able to see every Port and value
   
   5. ###### Camera: 
   
       Click the `Camera` button ![](./img/camera_page.png)Here you are able to see what the camera sees (if it is plugged into the controller). It might be helpful for debugging, but besides that it really is unnecessary.

