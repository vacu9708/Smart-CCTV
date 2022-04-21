# opencv-python==4.4.0.46 numpy==1.19.3
import socket
import time
from imutils.video import VideoStream
import imagezmq

sender = imagezmq.ImageSender(connect_to='tcp://192.168.0.1:5555')

rpi_name = socket.gethostname() # send RPi hostname with each image

picam = VideoStream(usePiCamera=True).start()
time.sleep(2.0)  # allow camera sensor to warm up

while True:
  image = picam.read()
  sender.send_image(rpi_name, image)