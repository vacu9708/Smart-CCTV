# Parking space information notifier(university graduation project)
![image](https://user-images.githubusercontent.com/67142421/199539868-8f2fd9f0-d421-45e3-99ce-8e05fc81f2de.png)

## What is this system
This system tracks cars and shows information for parking with LEDs in a parking lot.
It aims to decrease the time waste when looking for a parking space.

## 4 LED colors according to the situation
- Green: empty parking space
- Red: unavailable parking space
- Orange: parking at this space
- Yellow: going out of this space

## Images
![image](https://user-images.githubusercontent.com/67142421/199556685-d66c4c98-d992-4467-af05-c06ce614fa1f.png)
### A situation where a car is parking (the LED of the parking space closest to the car becomes orange)

![image](https://user-images.githubusercontent.com/67142421/199558068-28ba0193-6c84-4904-af59-bae415942bb6.png)
### A situation where a car is going out (when the headlight is turned on, the LED becomes yellow)

## Main things used in this project
* Raspberry pi, Camera module to take the video of the parking lot
* Arduino to control LEDs
* YOLOv5 object detection algorithm to detect objects
* [Deepsort](https://github.com/mikel-brostrom/Yolov5_StrongSORT_OSNet) algorithm to track detected objects

## Video processing performed in python
![image](https://user-images.githubusercontent.com/67142421/199557014-d4a0cc30-5356-413c-bb54-4b832525a188.png)

## Flow chart
![image](https://user-images.githubusercontent.com/67142421/199558323-6e1d6e53-c543-4073-bb08-05d97789bbb2.png)
