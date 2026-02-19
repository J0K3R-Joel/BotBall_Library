# Reasons of Choice

In this document I will cover some reasons of choice in Hardware or Software, why I chose to do things the way I did. Everything that I did not include in this file is either because I frankly forgot or I did not consider something else. You can always write me an E-Mail to asks for my reasons of some choices, so I can add them in here. 

## Software



### KIPR Library

#### move_at_velocity

In my library you will find that the base "moving" function of kipr that I use is `move_at_velocity` or `mav`. Reason being that the intervals for movement is between -1500 and +1500. Other "base moving functions" like `motor` only have a range from -100% to +100%. While this does not sound like an issue at all, I just prefered the `mav` function, since I feel that it is a little bit better to calculate a kind of bias, which is used to countersteer if the gyroscope value increases in a direction, indicating that you do not drive straight (enough). In conclusion, this is basically the only reason: Convenience. 



---

## Hardware



### Brightness Sensor

#### Positioning

I positioned the brightness sensors in the standard build ([./Controller_Guide.md](./Controller_Guide.md)) in the middle of the metal chasis (one in the front and one at the rear). This is simply for following the line or seeing the black line at all. Placing them in the middle of the robot is the most consistent place for line detection. I chose to use two since this saves time (e.g. no need for driving backwards for too long), is more consistent and see the line faster and easier and you know which way you got off the line. It also makes it easier and better for aligning on the line as well. 