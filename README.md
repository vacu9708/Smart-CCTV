# Parking lot information notifier(university graduation project)
![image](https://user-images.githubusercontent.com/67142421/203692196-6da73870-6f47-4937-bd90-6341ae2ac4bf.png)

### 📷[Video](https://youtu.be/ZB2DopuROoM)

# What this system is
This system tracks cars and shows parking information with LEDs in a parking lot.
It aims to decrease the time wasted when looking for a parking space.

# How to decrease the wasted time when a parking lot is congested
We improved the existing system that only shows the availability of parking spaces.<br>
In addition to its exisiting functionalities, our system also shows when cars are entering and leaving.<br>
Notifying of incoming cars can prevent other cars from going to an occupied space. Notifying of leaving cars can guide other cars to available spots.

# 4 LED colors according to the situation
- Green: empty parking space
- Red: unavailable parking space
- Orange: parking at this space
- Yellow: going out of this space

# Situations
## A situation where a car is parking
![image](https://user-images.githubusercontent.com/67142421/199556685-d66c4c98-d992-4467-af05-c06ce614fa1f.png)
The LED of the parking space closest to the car becomes orange.<br>
The time taken for the LED to be orange when the car approaches a parking space can be adjusted to exclude cars that are just passing. 

## A situation where a car is going out
![image](https://user-images.githubusercontent.com/67142421/199558068-28ba0193-6c84-4904-af59-bae415942bb6.png)
When the headlight is turned on, the LED becomes yellow.<br>
The time taken for the LED to be yellow after the headlight is turned on can be adjusted to prevent cars from waiting for the parking space to be available for too long. 

# Main things used in this project
* Raspberry pi, Camera module to take the video of the parking lot
* Arduino to control LEDs and a bluetooth module to receive LED signals from the image processing server
* YOLOv5 object detection algorithm to detect objects
* [Deepsort](https://github.com/mikel-brostrom/Yolov5_StrongSORT_OSNet) algorithm to track detected objects

# Video processing performed in python
![image](https://user-images.githubusercontent.com/67142421/199557014-d4a0cc30-5356-413c-bb54-4b832525a188.png)

# Hardware
![image](https://user-images.githubusercontent.com/67142421/199539868-8f2fd9f0-d421-45e3-99ce-8e05fc81f2de.png)
![image](https://user-images.githubusercontent.com/67142421/199559497-c5a9cc73-c009-4ca5-8570-1089452acc06.png)
![image](https://user-images.githubusercontent.com/67142421/199567887-b6c41437-8cea-46c2-967a-4ce99fd23e88.png)

# Flow chart
![image](https://user-images.githubusercontent.com/67142421/199558323-6e1d6e53-c543-4073-bb08-05d97789bbb2.png)

# Team members and roles
- 양영식: bluetooth communication for LEDs and car controlling, raspberry pi, algorithm for cars going out, YOLO image training
- 이승종: Algorithm for situations of green, red, and orange LED
- 김성혁: Hardware making
