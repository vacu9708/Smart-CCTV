# Smart-CCTV

![image](https://user-images.githubusercontent.com/67142421/169100092-8fe7e05a-f1f8-46b7-8cac-38f9601638d2.png)
> As you can see, illegal parking causes great convenience.
> The enforcement of all the illegally parked high and low is very difficult given the limited number of officials
> So, automating the enforcement of illegally parked cars is in an great need.

## Things used
* Raspberry pi, Camera module
* YOLOv5 object detection algorithm to detect objects
* Deepsort algorithm to track detected objects
* Node.js server for users

# Structure
## Overal picture of how it works
1. The camera transfers video frames to the image processing computer.
2. The live video streaming is analyzed in python. ( 1st and 2nd processes can be replaced with a recorded video
3. The analyzed result is sent to the Node.js server. (with base64 encoding, socket communication)

## How illegally parked cars are detected
1. Detect a car
2. Put a timer to the detected car
3. If the timer has gone off, notify the ilegal car with the date.

## Cars being tracked with a timer
![image](https://user-images.githubusercontent.com/67142421/169097525-1330b23b-65eb-4002-b261-50ca7443b49b.png)

## Detecting illegally parked cars
![image](https://user-images.githubusercontent.com/67142421/169099054-411c741f-8c61-4bf3-a439-eccaf6463632.png)

## Node.js web page
![image](https://user-images.githubusercontent.com/67142421/169098899-7b85fd9d-0cba-445e-aa91-fa897e9fca13.png)

[Police server to show the CCTV streaming](https://github.com/vacu9708/Smart-CCTV/tree/main/police%20server)
