# Parking Lot Information Notifier (University Graduation Project)
![image](https://github.com/user-attachments/assets/0a0629e3-3d1b-4a54-b849-c13489d608f3)

### 📷 Video  
https://youtu.be/ZB2DopuROoM

## Project Overview
This system tracks vehicles in a parking lot and displays real-time parking information using LEDs. Its goal is to reduce the time drivers spend searching for available parking spaces.

## Improving Congestion Efficiency
Traditional parking guidance lights only indicate whether a parking space is available. We enhanced this system by also showing when vehicles are entering or exiting a space.

Benefits:  
- Showing incoming vehicles prevents drivers from heading toward a spot that is already being taken.  
- Showing outgoing vehicles helps drivers quickly identify spaces that will soon become available.

## LED Status Colors
- **Green**: Space available  
- **Red**: Space occupied  
- **Orange**: A vehicle is entering the space  
- **Yellow**: A vehicle is leaving the space  

## Entering Scenario
The LED of the parking space nearest to the approaching vehicle turns **orange**.  
The delay before switching to orange can be adjusted to avoid responding to cars that are simply passing by.

## Exiting Scenario
When a vehicle’s headlights turn on, the LED turns **yellow**.  
The delay before switching to yellow can be adjusted so drivers do not wait too long for the space to become available.

## Technologies Used
- Raspberry Pi and camera module for video capture  
- Arduino for LED control and Bluetooth communication  
- YOLOv5 for object detection  
- DeepSORT for object tracking  

## Video Processing Pipeline (Python)
![image](https://user-images.githubusercontent.com/67142421/199557014-d4a0cc30-5356-413c-bb54-4b832525a188.png)

## Hardware
![image](https://user-images.githubusercontent.com/67142421/199539868-8f2fd9f0-d421-45e3-99ce-8e05fc81f2de.png)
![image](https://user-images.githubusercontent.com/67142421/199559497-c5a9cc73-c009-4ca5-8570-1089452acc06.png)
![image](https://user-images.githubusercontent.com/67142421/199567887-b6c41437-8cea-46c2-967a-4ce99fd23e88.png)

## Flowchart
![image](https://user-images.githubusercontent.com/67142421/199558323-6e1d6e53-c543-4073-bb08-05d97789bbb2.png)

## Team Members and Responsibilities  
(All members contributed equally)
- **양영식**: Raspberry Pi, LED Bluetooth communication, vehicle control, exit-detection algorithm, deep-learning model training  
- **이승종**: Algorithms for green, red, and orange LED states  
- **김성혁**: Hardware design and implementation  
