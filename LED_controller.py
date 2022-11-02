import socket#, time, threading

class Bluetooth:
    def __init__(self) -> None:
        self.arduino = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        MAC = '98:D3:21:FC:94:10'
        self.arduino.connect((MAC,1))
        for i in range(5):
            self.send(f'{i}1')


    def send(self, msg):
        while 1:
            self.arduino.send(msg.encode())
            if self.arduino.recv(1).decode()=='O':
                break

    def parking_state_determiner(self, parked_space, parking_state):
        if parking_state==0: # Green
            self.send(f'{parked_space}1')
        elif parking_state>=1: # Red
            self.send(f'{parked_space}2')
        elif parking_state==0.5: # 깜빡이는 주황
            self.send(f'{parked_space}3')
        elif parking_state<0: # 깜빡이는 노랑
            self.send(f'{parked_space}4')

    def test(self):
        while 1:
            msg=input()
            self.send(msg)
# bt=Bluetooth()
# bt.test()