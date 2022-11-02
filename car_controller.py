import socket, threading, keyboard
import multiprocessing as mp

class Manual_control:
    def __init__(self) -> None:
        self.arduino = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        MAC = '98:d3:31:f6:0b:4b'
        self.arduino.connect((MAC,1))
        threading.Thread(target=self.drive).start()
    
    def send(self, msg):
        while 1:
            try:
                self.arduino.send(f'{msg}'.encode())
                if self.arduino.recv(1).decode()=='O':
                        break
            except:
                self.arduino.connect((self.MAC,1))
    
    def drive(self):
        print(mp.current_process().name)
        print('Manual drive')
        msg=''
        while 1:
            if keyboard.is_pressed('w'):
                msg='wha'
            elif keyboard.is_pressed('s'):
                msg='sha'
            elif keyboard.is_pressed('d'):
                msg='lqz'
            elif keyboard.is_pressed('a'):
                msg='rqz'
            elif keyboard.is_pressed('q'):
                msg='Q'
            elif keyboard.is_pressed('e'):
                msg='W'
            else:
                msg=''
                while 1:
                    self.arduino.send(f'Ppp'.encode())
                    if self.arduino.recv(1).decode()=='O':
                        break
                while 1:
                    self.arduino.send(f'ppp'.encode())
                    if self.arduino.recv(1).decode()=='O':
                        break
            if not msg=='':
                while 1:
                    self.arduino.send(f'{msg}'.encode())
                    if self.arduino.recv(1).decode()=='O':
                        break
#Manual_control()
# if __name__ == "__main__":
#     print('hi')
#     mp.Process(name="SubProcess", target=Manual_control).start()