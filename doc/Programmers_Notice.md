# Considerations for the programmer

This file tells you, as the programmer, things you have to consider. This is only necessary if you are using my library (would help you out a lot.).

You do not have to use my library, but I would suggest to use it, since it already includes logic you do not need to think about. Also, if something does not work on the library, it is easier to figure out what's wrong and tell (if you are not competing alone) the other team about a solution to a problem that might occurred. It would also help future generations of having a better and easier time.

# Advanced

## Considerations about using motors in threads

### The threadsafe-time problem

##### Explanation

Maybe you find a way to fix this, but as of now, if you are getting inside a thread or use the `high priority` / `new main` priorities in communication, then you need to stay inside the new thread for at least 500 milliseconds. This is due to how the motor_scheduler (inside the `motor_scheduler.py` file) works, more specifically the ID generation. This is because it is hard to predict whether you are just waiting for 500 milliseconds inside the same thread and another thread gets ended very fast. Another reason that you need to stay inside the same thread (if you use the motor inside the short-lasting thread) for (at least) 500 milliseconds is, because starting a thread is very inconsistent. Sometimes the thread starts 200 milliseconds later other times the thread starts after only a few milliseconds later and in the worst case it can take longer than 200 milliseconds. As a baseline I took 500 milliseconds since I found it the most consistent to work.

##### Example

###### TRY TO AVOID THINGS LIKE THESE (every new picture is another way of how to not to do it):

---

![](./img/avoid_wrong_usage_motor.png)

Reason: When entering the thread there is a small chance that the button is already pressed (time in thread < 500 milliseconds) 

---

![](./img/avoid_wrong_usage_motor2.png)

Reason: When entering the thread it will immediately get out of the thread, even though inside of the thread you are telling the `drive_straight` function to be inside of the function for 1000 milliseconds. Threads in python start the function immediately and afterwards it will get into the `drive_straight` of the `driveR_instance` for 5000 milliseconds (in less than 500 milliseconds) -> too short

---

![](./img/avoid_wrong_usage_motor3.png)

Reason: Same as the above, even though you tell it to stay in it for 10000 milliseconds inside the thread and even after 450 milliseconds of waiting, there is still a chance of it taking less than 500 milliseconds. This is because the thread immediately exits itself and runs in the background (this is how threads work)

---

![](./img/avoid_wrong_usage_motor4.png)

Reason: Creating an entire new function and calling it inside of the thread does not change anything. This is just like the above, you could so to say just write this inside the same line instead of creating a new function. In a nutshell: It get's into the function and exits immediately, even though `turn_degrees` is not even finished. This results in the thread getting switched in less than 500 milliseconds. 

---

![](./img/avoid_wrong_usage_motor5.png)

Reason: Even if the function is very long, this never means that it takes long to execute. Also there is a chance that the condition is already met in the same second. This could lead to the thread taking less than 500 milliseconds (even though you specifically say to wait for 300 milliseconds)

---

##### Conclusion

Try to use one of these ways when you want to use threading and there is a chance of leaving the thread early / too early:

{TODO: ADD IMAGES}



##### Why this works

All of these ways work because of the way I wrote my library (`motor_scheduler.py`):

- It will generate a new ID if 500 milliseconds are between DRIVING (using the `driveR.py` file and / or `wheelR.py`) in two different threads. If you do something in a thread which is not driving, then those 500 milliseconds **can be ignored**
- You can use the `.join()` method of the `threading` module to wait for the thread to finish
- You can implement a time counter so you definitely stay inside the function for at least 500 milliseconds

---

### The no-drive-command problem

##### Explanation

Sometimes you are driving in a thread and want to exit it earlier (you were still longer inside of the thread than 500 milliseconds) than you told the driver to return to the main thread. Afterwards you need to keep care about the very next function after you exit the thread. If there is no call of a drive function (or for stopping the motor), then the function will keep running in the background until either the time gets reached when you told it to end or until the next call of another driving function. 

##### Example



##### Conclusion



##### Why this occurs



