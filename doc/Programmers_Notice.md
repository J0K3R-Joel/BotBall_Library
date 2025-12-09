# Considerations for the programmer

This file tells you, as the programmer, things you have to consider. This is only necessary if you are using my library (would help you out a lot.).

You do not have to use my library, but I would suggest to use it, since it already includes logic you do not need to think about. Also, if something does not work on the library, it is easier to figure out what's wrong and tell (if you are not competing alone) the other team about a solution to a problem that might occurred. It would also help future generations of having a better and easier time.

## Considerations about using motors

Maybe you find a way to fix this, but as of now, if you are getting inside a thread or use the `high priority` / `new main` priorities in communication, then you need to stay inside the new thread for at least 500 milliseconds. This is due to how the motor_scheduler (inside the `motor_scheduler.py` file) works, more specifically in the ID generation. This is because it is hard to predict whether you are just waiting for 500 milliseconds inside the same thread and another thread  