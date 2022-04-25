#import cv2
import socket
import time
from imutils.video import VideoStream
import imagezmq

sender = imagezmq.ImageSender(connect_to='tcp://192.168.102.27:5555')

rpi_name = socket.gethostname() # send RPi hostname with each image

picam = VideoStream(usePiCamera=True,
                    resolution=(640, 480),
                    framerate=30).start()
time.sleep(2.0)  # allow camera sensor to warm up

while True:
    image = picam.read()
    sender.send_image(rpi_name, image)
    #cv2.imshow('image', image)

