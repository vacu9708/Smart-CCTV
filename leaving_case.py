import cv2, time, threading
import numpy as np

class Timer:
    def __init__(self, parked_list) -> None:
        self.elapsed_times=[0 for i in range(5)] # 주차완료, 출차완료 후 지난 시간
        self.parked_list=parked_list
        for i in range(len(parked_list)):
            threading.Thread(target=self.timer, args=(i,)).start()

    def timer(self, i):
        while 1:
            time.sleep(1)
            if self.parked_list[i]>=1: # 주차된 상태면
                self.elapsed_times[i]+=1
            else:
                self.elapsed_times[i]=0

class Leaving_case():
    def __init__(self, cam, _led_controller, _parking_spaces, _parked_list):
        self.parked_list=_parked_list
        self.timer=Timer(self.parked_list)
        self.led_controller=_led_controller
        self.head_lights=np.array([[0 for i in range(4)] for i in range(5)]) # xxyy

        if True: # x_width는 60 고정
            self.head_lights[0] = np.array([_parking_spaces[0][0]-40, _parking_spaces[0][1]+20, _parking_spaces[0][2]+30, _parking_spaces[0][3]+40])
            self.head_lights[1] = np.array([_parking_spaces[1][0]-30, _parking_spaces[1][1]+30, _parking_spaces[1][2]+30, _parking_spaces[1][3]+40])
            self.head_lights[2] = np.array([_parking_spaces[2][0]-30, _parking_spaces[2][1]+30, _parking_spaces[2][2]+30, _parking_spaces[2][3]+40])
            self.head_lights[3] = np.array([_parking_spaces[3][0]-20, _parking_spaces[3][1]+40, _parking_spaces[3][2]+30, _parking_spaces[3][3]+40])
            if len(_parking_spaces)==5:
                self.head_lights[4] = np.array([_parking_spaces[4][0]-10, _parking_spaces[4][1]+50, _parking_spaces[4][2]+30, _parking_spaces[4][3]+40])

    def judge_leaving_car_by_YOLO(self, center, class_name, elapsed_time):
        if not(class_name=='bright'):
            return
        # 헤드라이트가 있는 주차면 찾기
        space=99 # space_being_left
        for i in range(len(self.head_lights)):
            if self.head_lights[i][0]<=center[0]<=self.head_lights[i][1] and self.head_lights[i][2]<=center[1]<=self.head_lights[i][3]:
                space=i
                break
        # 헤드라이트 위치가 주차면에 있지 않거나, 주차완료가 아니거나, 주차한지 얼마안됐거나
        if space==99 or self.parked_list[space]<1 or self.timer.elapsed_times[space]<=4 or not 4<=elapsed_time<=5:
            return
        self.parked_list[space] *= -1
        print(self.parked_list,"going out")
        if self.led_controller:
            self.led_controller.parking_state_determiner(space, self.parked_list[space])

    def draw_headlight_boxes(self, ori_img):
        for i in range(len(self.head_lights)):
            cv2.rectangle(ori_img, (self.head_lights[i][0], self.head_lights[i][2]), (self.head_lights[i][1], self.head_lights[i][3]), (255,0,0))