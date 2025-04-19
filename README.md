# Parking lot information notifier(university graduation project)
![image](https://github.com/user-attachments/assets/0a0629e3-3d1b-4a54-b849-c13489d608f3)

### 📷[Video](https://youtu.be/ZB2DopuROoM)

# What this system is
This system tracks cars and shows parking information with LEDs in a parking lot.
It aims to reduce the time spent searching for a parking space.

# How to decrease the wasted time when a parking lot is congested
We improved the existing parking guidance lights, which previously only showed the availability of parking spaces, by also displaying when cars are entering and leaving.
- Notifying drivers of incoming cars can prevent them from heading toward a space that's already being taken.
- Notifying drivers of cars that are leaving can guide them to a space that will soon be available

# 4 LED colors according to the situation
- Green: available parking space
- Red: unavailable parking space
- Orange: entering this space
- Yellow: leaving this space

# Situations
## Cars entering
![image](https://user-images.githubusercontent.com/67142421/199556685-d66c4c98-d992-4467-af05-c06ce614fa1f.png)
The LED of the parking space closest to the car becomes orange.<br>
The time taken for the LED to be orange when the car approaches a parking space can be adjusted to exclude cars that are just passing. 

## Cars going out
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

# Team members and roles (All of the team members made an equal contribution)
- 양영식: Rapsberry pi / Bluetooth communication for LEDs / car controlling / algorithm for cars going out / image training for deep learning
- 이승종: Developed algorithm for the situations of green, red, and orange LED
- 김성혁: In charge of hardware
