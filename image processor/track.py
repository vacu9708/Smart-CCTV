import sys
from typing import Any
sys.path.insert(0, './yolov5')

import base64, socketio, requests
import time, math, keyboard
from pathlib import Path
import numpy as np
import cv2
import torch
import torch.backends.cudnn as cudnn

from yolov5.models.experimental import attempt_load
from yolov5.utils.downloads import attempt_download
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.datasets import LoadImages, LoadStreams, MyStream, VID_FORMATS
from yolov5.utils.general import (check_img_size, non_max_suppression, scale_coords, xyxy2xywh)
from yolov5.utils.torch_utils import select_device, time_sync
from yolov5.utils.plots import Annotator
from deep_sort.utils.parser import get_config
from deep_sort.deep_sort import DeepSort

# Communication
requests.post('http://localhost:3000/process/python_login', json={'id': 'police', 'password':'112'})
socket_io = socketio.Client()
socket_io.connect('http://localhost:3000')

import timer_alarm
timer_alarm.socket_io=socket_io

# Yolo
yolo_model='yolov5/weights/yolov5s.onnx'
device = select_device('')
model = DetectMultiBackend(yolo_model, device=device, dnn='')
stride, names, pt = model.stride, model.names, model.pt
img_size = check_img_size([640, 640], s=stride)  # check image size
names = model.module.names if hasattr(model, 'module') else model.names # Get names and colors
classes=[2,7] # car:2, truck:7, 67: phone

# Colors
np.random.seed(4)
COLORS = np.random.randint(0, 255, size=(len(classes), 3), dtype='uint8')

# Dataloader
cam=False
#source='0'
source="resource/parking_lot2.mp4"
if cam:
    cudnn.benchmark = True  # set True to speed up constant image size inference
    #input = LoadStreams(source, img_size=img_size, stride=stride, auto=pt)
    input = MyStream(img_size=img_size, stride=stride, auto=pt, raspberry=False) # Turn on webcam
else:
    input = LoadImages(source, img_size=img_size, stride=stride, auto=pt)

# initialize deepsort
cfg = get_config()
config_deepsort="deep_sort/configs/deep_sort.yaml"
cfg.merge_from_file(config_deepsort)
deepsort=DeepSort(
                'osnet_x0_50', #cfg.DEEPSORT.MODEL_TYPE,
                device,
                max_dist=0.2,#cfg.DEEPSORT.MAX_DIST,
                max_iou_distance=0.7,#cfg.DEEPSORT.MAX_IOU_DISTANCE,
                max_age=90,#cfg.DEEPSORT.MAX_AGE,
                n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET)

# Run tracking
outputs = []
parked_cars=[]
model.warmup(imgsz=(1, 3, *img_size))
for frame_idx, (path, image, image0s, vid_cap, s) in enumerate(input): # Frames
    image = torch.from_numpy(image).to(device)
    image = image.float()  # uint8 to fp16/32
    image /= 255.0  # 0 - 255 to 0.0 - 1.0
    if len(image.shape) == 3: # If video
        image = image[None]  # expand for batch dim

    # Inference
    pred = model.forward(image, augment=False, visualize=False) # prediction
    pred = non_max_suppression(pred, 0.5, 0.5, classes, False, max_det=1000) # Apply NMS

    # Process detections
    for i, detection in enumerate(pred):  # Detections per frame
        #start_time=time.time() # To measure FPS
        if cam:
            image0= image0s[i] # A frame
        else:
            image0, _ = image0s, getattr(input, 'frame', 0) # A frame

        #s += '%gx%g ' % image.shape[2:]  # print string
        annotator = Annotator(image0, line_width=2, pil=not ascii)

        if detection is not None and len(detection):
            # Rescale boxes from img_size to im0 size
            detection[:, :4] = scale_coords(image.shape[2:], detection[:, :4], image0.shape).round()

            xywhs = xyxy2xywh(detection[:, 0:4])
            confs = detection[:, 4] # confidence
            clss = detection[:, 5] # class

            # Pass a detection to deepsort
            outputs = deepsort.update(xywhs.cpu(), confs.cpu(), clss.cpu(), image0, parked_cars)

            # Draw boxes for visualization
            for j, (output) in enumerate(outputs):
                bbox = output[0:4]
                id = output[4]
                cls = output[5] # class
                #conf = output[6] # confidencce
                elapsed_time=output[7]
                stopped='Stopped' if output[8]==True else ''
                c = int(cls)  # integer class
                label = f'{id:.0f} {names[c]}/{elapsed_time:0.0f}sec/{stopped}'
                color = [ int(c) for c in COLORS[c%len(classes)] ]
                annotator.box_label(bbox, label, color=color)
        else: # No detection
            deepsort.increment_ages()
            #LOGGER.info('No detections')

        image0 = annotator.result()
        for parked_car in parked_cars:
            cv2.putText(image0, f'ILEGAL: {parked_car[2]}', parked_car[0:2], 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

        # Stream results through webcam
        #period=time.time()-start_time
        #fps=math.ceil(1/period if period>0.01 else 0.01)
        #cv2.putText(image0, 'FPS: {}'.format(str(fps)), (0,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)
        '''cv2.imshow('capstone', image0)
        if cv2.waitKey(1)>-1:
            exit'''
        result, encoded_frame = cv2.imencode('.jpg', image0)
        image_as_text = base64.b64encode(encoded_frame)#.decode('utf-8')
        socket_io.emit('frame from python', image_as_text)
        #-----
                
        '''if keyboard.is_pressed('space'): # Turn off if any key pressed
                exit()'''
        if keyboard.is_pressed('esc'): # Enter to reset
            parked_cars.clear()
            deepsort=DeepSort(
                'osnet_x0_50',#cfg.DEEPSORT.MODEL_TYPE,
                device,
                max_dist=0.2,#cfg.DEEPSORT.MAX_DIST,
                max_iou_distance=0.7,#cfg.DEEPSORT.MAX_IOU_DISTANCE,
                max_age=30,#cfg.DEEPSORT.MAX_AGE,
                n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET)