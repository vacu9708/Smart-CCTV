import sys
sys.path.insert(0, './yolov5')

#import base64, socketio, requests
#import time, math, keyboard
#from pathlib import Path
import numpy as np
import cv2
import torch
import torch.backends.cudnn as cudnn
import operator, threading
from leaving_case import Leaving_case
import LED_controller, raspberry, automated_car, car_controller
import multiprocessing as mp

# from yolov5.models.experimental import attempt_load
# from yolov5.utils.downloads import attempt_download
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.datasets import LoadImages, MyStream, VID_FORMATS
from yolov5.utils.general import (check_img_size, non_max_suppression, scale_coords, xyxy2xywh)
from yolov5.utils.torch_utils import select_device, time_sync
from yolov5.utils.plots import Annotator
from deep_sort.utils.parser import get_config
from deep_sort.deep_sort import DeepSort
import deep_sort.sort.tracker as tracker

# Communication
# requests.post('http://localhost:4000/process/python_login', json={'id': 'police', 'password':'112'})
#socket_io = socketio.Client()
# socket_io.connect('http://localhost:4000')

#import timer_alarm
#timer_alarm.socket_io=socket_io

cam=True
with_led_controller = True
led_controller=LED_controller.Bluetooth() if with_led_controller else False
tracker.led_controller=led_controller
with_auto_parking=False # 자동주차
automated_car=automated_car.Bluetooth() if with_auto_parking and cam else False
address='192.168.137.193' # 직접 연결
#address='192.168.29.2' # 핫스팟
with_socket_streaming=False
socket_streaming=raspberry.Socket(address) if with_socket_streaming else False
pi_ip=True # 웹 스트리밍
pi_ip = address if pi_ip else ''

# Yolo
yolo_model='yolov5/weights/headlightS.onnx'
device = select_device('')
model = DetectMultiBackend(yolo_model, device=device, dnn='')
stride, names, pt = model.stride, model.names, model.pt
img_size = check_img_size([640, 640], s=stride)  # check image size
names = model.module.names if hasattr(model, 'module') else model.names # Get names and colors
classes=[0,1] # car, bright, dark
#classes=[0,2]

# Colors
np.random.seed(4)
COLORS = np.random.randint(0, 255, size=(len(classes), 3), dtype='uint8')

# Dataloader
source="resource/my_video.mp4"
parking_space_center=[[90,200],[200,200],[320,200],[430,190],[520,200]] # 중앙xy
width=40
    
if cam: #165 290 410 510
    top_y=240
    bottom_y=300
    parking_space=[[65,112,top_y,bottom_y],[185,226,top_y,bottom_y],[295,338,top_y,bottom_y],[409,453,top_y,bottom_y],[530,570,top_y,bottom_y]]
    parked_list = [0, 0, 0, 0, 0]
    least = [0, 0, 0, 0, 0]
    # disappeared = [0, 0, 0, 0, 0]
    cudnn.benchmark = True  # set True to speed up constant image size inference
    input = MyStream(img_size=img_size, stride=stride, auto=pt, socket=socket_streaming, pi_ip=pi_ip) # Turn on webcam
elif source == "resource/outcase_4.mp4" or source == "resource/incase_4.mp4":
    parking_space = [[220, 320, 210, 310], [490, 590, 210, 310], [700, 800, 200, 300], [960, 1060, 200, 300]]
    parked_list = [0, 0, 0, 0]
    least = [0, 0, 0, 0]
    # disappeared = [0, 0, 0, 0]
    input = LoadImages(source, img_size=img_size, stride=stride, auto=pt)
elif source=="resource/my_video.mp4":
    parking_space = [[270,300,150,250],[450,480,150,250],[640,670,150,250],[820,850,150,250],[1000,1030,150,250]]
    parked_list = [0, 0, 0, 0, 0]
    least = [0, 0, 0, 0, 0]
    # disappeared = [0, 0, 0, 0, 0]
    input = LoadImages(source, img_size=img_size, stride=stride, auto=pt)
# else:
#     input = LoadImages(source, img_size=img_size, stride=stride, auto=pt)

tracker.parked_list=parked_list
waiting_times = [0]*len(parked_list)
# initialize deepsort
cfg = get_config()
config_deepsort="deep_sort/configs/deep_sort.yaml"
cfg.merge_from_file(config_deepsort)
deepsort=DeepSort(
                'osnet_x0_50', #cfg.DEEPSORT.MODEL_TYPE,
                device,
                max_dist=0.6,#cfg.DEEPSORT.MAX_DIST,
                max_iou_distance=0.7,#cfg.DEEPSORT.MAX_IOU_DISTANCE,
                max_age=30,#cfg.DEEPSORT.MAX_AGE,
                n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET)

# Run tracking
outputs = []
entrance = {}
led_counter = 0
dic_least = {}
min_index = -1
parked_id = []
flag = 0
prev_total_count = 0

leaving_case=Leaving_case(cam, led_controller, parking_space, parked_list)
model.warmup(imgsz=(1, 3, *img_size))
for frame_idx, (path, image, image0s, vid_cap, s) in enumerate(input): # Frames
    total_count = 0
    parked_count = 0
    if cam:
        image0= image0s[0] # A frame
    else:
        image0, _ = image0s, getattr(input, 'frame', 0) # A frame
    #leaving_case.judge_leaving_car(image0) # only 밝기변화로 헤드라이트 빛 감지
    leaving_case.draw_headlight_boxes(image0) # YOLO로 헤드라이트 빛 감지 (output 밑에 한 줄 더있음)
    if automated_car:
        automated_car.target_drawer(image0)


    # Preprocessing for YOLO
    image = torch.from_numpy(image).to(device)
    image = image.float()  # uint8 to fp16/32
    image /= 255.0  # 0 - 255 to 0.0 - 1.0
    if len(image.shape) == 3: # If video
        image = image[None]  # expand for batch dim

    # Inference
    pred = model.forward(image, augment=False, visualize=False) # prediction
    pred = non_max_suppression(pred, 0.6, 0.5, classes, False, max_det=1000) # Apply NMS

    # Process detections
    for i, detection in enumerate(pred):  # Deepsort on detections in this frame
        #start_time=time.time() # To measure FPS

        #s += '%gx%g ' % image.shape[2:]  # print string
        annotator = Annotator(image0, line_width=2, pil=not ascii)

        if detection is not None and len(detection):
            # Rescale boxes from img_size to im0 size
            detection[:, :4] = scale_coords(image.shape[2:], detection[:, :4], image0.shape).round()

            xywhs = xyxy2xywh(detection[:, 0:4])
            confs = detection[:, 4] # confidence
            clss = detection[:, 5] # class

            # Pass a detection to deepsort33
            outputs = deepsort.update(xywhs.cpu(), confs.cpu(), clss.cpu(), image0, parked_list, cam, led_controller)

            # Draw boxes for visualization
            for j, (output) in enumerate(outputs):
                bbox = output[0:4]
                id = output[4]
                cls = output[5] # class
                conf = output[6] # confidencce
                elapsed_time=output[7]
                slow='slow' if output[8] else ''
                c = int(cls)  # integer class
                label = f'{100*conf:0.0f}%/{elapsed_time:0.0f}/{output[10]:0.0f}/{output[11]:0.0f}'
                #label = f'{output[3]}'
                #label = f'{output[10]}/{output[11]}'
                #label = f'{elapsed_time:0.0f}/{output[10]}/{output[11]}'
                color=[1,1,1] if output[9] else [ int(c) for c in COLORS[c%len(classes)] ] # Parked, not parked
                annotator.box_label(bbox, label, color=color)
                cv2.circle(image0, (int(output[10]), int(output[11])), 5, (255,255,0), -1) # 객체의 중앙 좌표
                leaving_case.judge_leaving_car_by_YOLO((output[10], output[11]), names[c], elapsed_time, output[12]) # YOLO로 헤드라이트 빛 감지
                if automated_car:
                    automated_car.update(id, (output[10], output[11]))
                if names[c] == 'car':
                    total_count += 1

                for k in range(len(parked_list)):
                    if names[c] == 'car' and parking_space[k][0] <= output[10] <= parking_space[k][1] and  parking_space[k][2] <= output[11] <= parking_space[k][3] and parked_list[k] >= 0:
                        if int(id) not in parked_list:
                            parked_list[k] = int(id)
                            print(f'{parked_list}parked')
                            if led_controller:
                                led_controller.parking_state_determiner(k, parked_list[k])  
                            if int(id) in entrance:
                                del entrance[(int(id))]                        
                    if names[c] == 'car' and (not (parking_space[k][0] <= output[10] <= parking_space[k][1]) or not( parking_space[k][2] <= output[11] <= parking_space[k][3])):
                        if parked_list[k] == -int(id) or parked_list[k] == int(id):
                            parked_id.append(abs(int(id)))
                            min_index = -1
                            parked_list[k] = 0
                            print(f'{parked_list}parked')
                            if led_controller:
                                led_controller.parking_state_determiner(k, parked_list[k])
                    if  names[c] == 'car' and parking_space[k][0] <= output[10] <= parking_space[k][1] and  parking_space[k][2] <= output[11] <= parking_space[k][3]:
                        if not parked_list[k] < 0:
                            waiting_times[k]=0
                        else:
                            if waiting_times[k] == 0:
                                waiting_times[k] = elapsed_time
                            elif elapsed_time - waiting_times[k] > 10: # 출차예정 timeout 시간
                                waiting_times[k] = 0
                                parked_list[k] = abs(parked_list[k])
                                print(f'{parked_list}parked')
                                if led_controller:
                                    led_controller.parking_state_determiner(k, parked_list[k])  
                            
                             
                    if names[c] == 'car' and int(id) not in parked_list and 3 < int(elapsed_time) and int(id) not in parked_id: # 입차예정 시간     
                        for i in range(len(parked_list)):
                            if output[3] > 420:
                                if i == 0:
                                    cali_val = -80
                                elif i == 1:
                                    cali_val = -50
                                elif i == 2:
                                    cali_val = -10
                                elif i == 3:
                                    cali_val = 30
                                elif i == 4:
                                    cali_val = 80
                            else:
                                cali_val = 0
                            least[i] = abs(((parking_space[i][0] + parking_space[i][1])/2) - output[10] + cali_val)
                        for i, num in enumerate(least):
                            dic_least.setdefault(i,num)
                        sort_least = dict(sorted(dic_least.items(), key=operator.itemgetter(1)))
                        list_sort = list(sort_least.values())
                        for key, value in sort_least.items():
                            if value == list_sort[0] and parked_list[key] == 0:                  
                                if int(id) not in parked_list:
                                    entrance[int(id)] = key        
                                min_index = key
                        if parked_list.count(0.5) > len(entrance):
                            for i in range(len(parked_list)):
                                if i not in list(entrance.values()) and parked_list[i] == 0.5:
                                    parked_list[i] = 0   
                                    print(f'{parked_list}parked')
                                    if led_controller:
                                        led_controller.parking_state_determiner(i, parked_list[i])                       
                        elif parked_list[min_index] == 0:
                            if min_index==-1:
                                continue
                            parked_list[min_index] = 0.5
                            #print(f'min_index = {min_index}')
                            print(f'{parked_list}parked')
                            if led_controller:
                                led_controller.parking_state_determiner(min_index, parked_list[min_index])                       
                    dic_least.clear()
                    # if parked_list.count(0.5) >= len(entrance) and len(entrance) > 0:
                    #     disappeared[parked_list.index(0.5)] += 1
                    #     if sum(disappeared) >= 50000:
                    #         parked_list[parked_list.index(0.5)] = 0
                    #         entrance.clear()                        
                    #         for i in range(len(disappeared)):
                    #             disappeared[i] = 0
                    #         print(f'{parked_list}parked')
                    #         if led_controller:
                    #             led_controller.parking_state_determiner(k, parked_list[k])  
                # if total_count < parked_list.count(0.5) + len(list(entrance.keys())):
                #     entrance.clear()
                #     for i in range(len(parked_list)):
                #         if parked_list[i] == 0.5:
                #             parked_list[i] = 0
            for i in range(len(parked_list)):
                if abs(parked_list[i]) >= 1:
                    parked_count += 1   
            if prev_total_count > total_count and parked_id != []:
                parked_id.clear() 
            if total_count - parked_count < len(entrance.keys()):
                entrance.clear()
                for i in range(len(parked_list)):
                    if parked_list[i] == 0.5:
                        parked_list[i] = 0
                        min_index = -1
                        if led_controller:
                            led_controller.parking_state_determiner(i, parked_list[i])                       
                        print(f'{parked_list}parked')
            # print(f'entrance = {entrance} total_count - parked_count = {total_count - parked_count} parked_id = {parked_id} min_index = {min_index}')  
            
            # 6번째 LED
            if len(parked_id) > 0 and parked_list.count(0) + parked_list.count(0.5) <= total_count - parked_count - len(parked_id):
            # 출차하는 상황, 출차차량이 생겨서 주차면에 빈 자리가 생겼을 때 기다리고 있는 차량이 있으면
                if flag == 0:
                    print('red1')
                    flag = 1
                    if led_controller:
                        led_controller.parking_state_determiner(5, 1)
            elif 0 not in parked_list:
            # 0이 없으면 즉, 빈 자리가 없으면
                parked_sort = sorted(parked_list)
                if parked_sort[0] < 0:
                # 현재 주차면에서 출차예정이 있는지 판단
                    if total_count - parked_count > parked_list.count(0.5):
                    # 출차예정일때 기다리는 차량이 있다면
                        if flag == 0: 
                            print('red2')
                            flag = 1
                            if led_controller:
                                led_controller.parking_state_determiner(5, 1)   
                    # elif total_count == parked_count and flag == 1:
                    elif total_count == parked_count + parked_list.count(0.5):
                    # elif total_count == parked_count + parked_list.count(0.5):
                    # 출차예정일때 기다리는 차량이 없다면
                        if flag == 1:
                            print('green1')
                            flag = 0
                            if led_controller:
                                led_controller.parking_state_determiner(5, 0)
 
                else:
                # 출차예정이 없다면    
                    if flag == 0:
                        print('red3')
                        flag = 1
                        if led_controller:
                            led_controller.parking_state_determiner(5, 1)   
            elif 0 in parked_list:
            # 빈자리가 있으면
                if total_count - parked_count - len(parked_id) >= parked_list.count(0) + parked_list.count(0.5):
                    # print(f'1_red {len(parked_id)}')
                # 기다리는 차량이 있을 때 아직 입차예정으로 판단되지 않았을 때
                    if flag == 0:
                        print('red4')
                        flag = 1
                        if led_controller:
                            led_controller.parking_state_determiner(5, 1)   
                elif total_count - parked_count - len(parked_id) < parked_list.count(0) + parked_list.count(0.5):
                    # print(f'2_green {len(parked_id)}')
                # 빈 주차면이 있다면
                    if flag == 1:
                        print('green2')
                        flag = 0
                        if led_controller:
                            led_controller.parking_state_determiner(5, 0) 
            prev_total_count = total_count

        else: # No detection
            deepsort.increment_ages()
            #LOGGER.info('No detections')

        if led_counter > 20:
            led_counter = 0
        else : led_counter+=1
        
        if cam:
            circle_y = 90
            for i in range(5): 
                cv2.rectangle(image0, (parking_space[i][0], parking_space[i][2]), (parking_space[i][1], parking_space[i][3]), (0,0,255))
                if i == 0:
                    circle_x = parking_space_center[0][0]
                elif i == 1:
                    circle_x = parking_space_center[1][0]
                elif i == 2:
                    circle_x = parking_space_center[2][0]
                elif i == 3:
                    circle_x = parking_space_center[3][0]
                elif i == 4:
                    circle_x = parking_space_center[4][0]
                if parked_list[i] == 0:
                    cv2.circle(image0, (circle_x, circle_y), 10, (0,255,0), -1)
                elif parked_list[i] < 0:
                    cv2.circle(image0, (circle_x, circle_y), 10, (0,127,255), -1)
                elif parked_list[i] >= 1:
                    cv2.circle(image0, (circle_x, circle_y), 10, (0,0,255), -1)
                elif parked_list[i] == 0.5 and led_counter % 2 == 0:
                    cv2.circle(image0, (circle_x, circle_y), 10, (0,255,0), -1)
        elif source == "resource/outcase_4.mp4" or source == "resource/incase_4.mp4":
            circle_y = 100
            for i in range(4):
                cv2.rectangle(image0, (parking_space[i][0], parking_space[i][2]), (parking_space[i][1], parking_space[i][3]), (0,0,255))
                if i == 0:
                    circle_x = 320
                elif i == 1:
                    circle_x = 560
                elif i == 2:
                    circle_x = 770
                elif i == 3:
                    circle_x = 1000
                if parked_list[i] == 0:
                    cv2.circle(image0, (circle_x, circle_y), 10, (0,255,0), -1)
                elif parked_list[i] < 0:
                    cv2.circle(image0, (circle_x, circle_y), 10, (0,127,255), -1)
                elif parked_list[i] >= 1:
                    cv2.circle(image0, (circle_x, circle_y), 10, (0,0,255), -1)
                elif parked_list[i] == 0.5 and led_counter % 2 == 0:
                    cv2.circle(image0, (circle_x, circle_y), 10, (0,255,0), -1)
        else:
            circle_y = 70
            for i in range(5):
                if i == 0:
                    circle_x = 286
                elif i == 1:
                    circle_x = 462
                elif i == 2:
                    circle_x = 655
                elif i == 3:
                    circle_x = 834
                elif i == 4:
                    circle_x = 1017
                if parked_list[i] == 0:
                    cv2.circle(image0, (circle_x, circle_y), 10, (0,255,0), -1)
                elif parked_list[i] < 0:
                    cv2.circle(image0, (circle_x, circle_y), 10, (0,127,255), -1)
                elif parked_list[i] >= 1:
                    cv2.circle(image0, (circle_x, circle_y), 10, (0,0,255), -1)
                elif parked_list[i] == 0.5 and led_counter % 2 == 0:
                    cv2.circle(image0, (circle_x, circle_y), 10, (0,255,0), -1)        
        
        image0 = annotator.result()
        
        # if cv2.waitKey(1)==ord('q'):
        #     x_pos,y_pos,width,height = cv2.selectROI("location", image0, False)
        #     print(f'{x_pos}, {x_pos+width}, {y_pos}, {y_pos+height}')
        # image0=cv2.GaussianBlur(image0, (5,5), 0)
        # image0=cv2.Canny(image0,100,100)
        cv2.imshow('capstone', image0)
        if cv2.waitKey(1)==27:
            exit()

        # Streaming on webpage
        '''result, encoded_frame = cv2.imencode('.jpg', image0)
        image_as_text = base64.b64encode(encoded_frame)#.decode('utf-8')
        socket_io.emit('frame from python', image_as_text)'''
                
        '''if keyboard.is_pressed('etc'):
                exit()'''
        '''if keyboard.is_pressed('space'): # Enter to reset
            deepsort=DeepSort(
                'osnet_x0_50',#cfg.DEEPSORT.MODEL_TYPE,
                device,
                max_dist=0.4,#cfg.DEEPSORT.MAX_DIST,
                max_iou_distance=0.7,#cfg.DEEPSORT.MAX_IOU_DISTANCE,
                max_age=30,#cfg.DEEPSORT.MAX_AGE,
                n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET)'''