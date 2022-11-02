import socket, cv2, time, threading, math
#print(math.atan( (270-370)/(300-299) )*180/math.pi)
class Bluetooth:
    def __init__(self) -> None:
        self.arduino = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        MAC = '98:d3:31:f6:0b:4b'
        self.arduino.connect((MAC,1))
        self.target=(0,0)
        self.target1=(308,330)
        self.target2=(300,400)
        self.target3=(300,360)
        self.target_final=(300,240)
        self.difference=(0,0)
        self.car_id=0
        self.bt_available=True
        threading.Thread(target=self.test).start()
        print('car initiated')

    def target_drawer(self, ori_img):
        cv2.putText(ori_img,'1',self.target1, cv2.FONT_HERSHEY_COMPLEX, 0.5,(255, 255, 0),1,cv2.LINE_AA)
        cv2.putText(ori_img,'2',self.target2, cv2.FONT_HERSHEY_COMPLEX, 0.5,(255, 255, 0),1,cv2.LINE_AA)
        cv2.putText(ori_img,'3',self.target3, cv2.FONT_HERSHEY_COMPLEX, 0.5,(255, 255, 0),1,cv2.LINE_AA)
        cv2.putText(ori_img,'4',self.target_final, cv2.FONT_HERSHEY_COMPLEX, 0.5,(255, 255, 0),1,cv2.LINE_AA)

    def update(self, id, center):
        if id==self.car_id:
            self.difference=(self.target[0]-center[0],self.target[1]-center[1])

    def send_signal(self, signal):
        while 1:
            if not self.bt_available:
                return
            self.arduino.send(f'{signal}'.encode())
            if self.arduino.recv(1).decode()=='O':
                break

    def drive(self):
        time.sleep(1)
        # step1: 빠르게 목표지점으로
        print('step1')
        self.target=self.target1
        while 1:
            if self.car_id==0:
                return
            # 전진
            if self.difference[0]<-30:
                # 방향 조정
                if self.difference[1]>0:
                    self.send_signal('lka')
                elif self.difference[1]<0:
                    self.send_signal('rka')
                self.send_signal('wzb')
                self.send_signal('Paa')
            else: # 정지
                self.send_signal('szb')
                break
            time.sleep(0.1)
        # 미세조정
        print('step1 미세조정')
        reached=0
        while 1:
            if self.car_id==0:
                return

            if self.difference[0]<-10:
                reached=0
                if self.difference[1]>0:
                    self.send_signal('lzz')
                elif self.difference[1]<0:
                    self.send_signal('rzz')
                self.send_signal('woa')
            elif self.difference[0]>10:
                reached=0
                self.send_signal('soa')
            else: # 정지
                reached+=1
                print('reached:',reached)
                if reached>=5:
                    break
            time.sleep(0.3) # 가속 방지

        # 전진, 후진 반복
        for i in range(1):
            #step2: 좌회전 전진
            print('step2')
            self.send_signal('lzz')
            self.target=self.target2
            time.sleep(0.5)
            # 미세조정
            reached=0
            while 1:
                if self.car_id==0:
                    return
                if self.difference[1]>10:
                    reached=0
                    self.send_signal('wzb')
                elif self.difference[1]<-10:
                    reached=0
                    self.send_signal('szb')
                else:
                    reached+=1
                    print('reached:',reached)
                    if reached==5:
                        break
                time.sleep(0.2)

            # step3: 우회전 후진
            print('step3')
            self.send_signal('rzz')
            self.target=self.target3
            time.sleep(0.5)
            # 미세조정
            reached=0
            while 1:
                if self.car_id==0:
                    return
                if self.difference[1]>10:
                    reached=0
                    self.send_signal('wzb')
                elif self.difference[1]<-10:
                    reached=0
                    self.send_signal('szb')
                else: # 정지
                    reached+=1
                    print('reached:',reached)
                    if reached==5:
                        break
                time.sleep(0.2)

        # Final step (미세조정)
        print('final step')
        self.send_signal('rzz')
        self.target=self.target_final
        reached=0
        while 1:
            if self.car_id==0:
                return

            angle=math.atan(self.difference[1]/self.difference[0]+0.1)*180/math.pi
            if abs(angle)>85:
                print(f'angle: {angle}')
                self.send_signal('Paa')

            if self.difference[1]>10:
                reached=0
                self.send_signal('wzb')
            elif self.difference[1]<-10:
                reached=0
                self.send_signal('szb')
            else: # 정지
                reached+=1
                print('reached:',reached)
                if reached>=5:
                    self.send_signal('Paa')
                    break
            time.sleep(0.2)

        self.car_id=0
            
    # Q: LED on / W: LED off
    def test(self):
        while 1:
            msg=input()
            if ord('0')<=ord(msg[0])<=ord('9'):
                self.car_id=int(msg)
                if self.car_id==0:
                    self.bt_available=False
                    self.send_signal('paa')
                    self.send_signal('Paa')
                    self.bt_available=True
                else:
                    threading.Thread(target=self.drive).start()
            else: # 새치기 블루투스
                self.bt_available=False
                while 1:
                    self.arduino.send(f'{msg}'.encode())
                    if self.arduino.recv(1).decode()=='O':
                        break
                self.bt_available=True

class Manual_control:
    def __init__(self) -> None:
        self.arduino = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        MAC = '98:d3:31:f6:0b:4b'
        self.arduino.connect((MAC,1))
        threading.Thread(target=self.drive).start()
    
    def drive(self):
        print('Manual drive')
        control='p'
        while 1:
            control=input()
            if control=='w':
                msg='wzb'
            elif control=='s':
                msg='szb'
            elif control=='a':
                msg='lzz'
            elif control=='d':
                msg='rzz'
            elif control=='p':
                msg='ppp'
            elif control=='P':
                msg='Ppp'
            elif control=='q':
                msg='Q'
            elif control=='e':
                msg='W'
            while 1:
                self.arduino.send(f'{msg}'.encode())
                if self.arduino.recv(1).decode()=='O':
                        break
# bt=Bluetooth()