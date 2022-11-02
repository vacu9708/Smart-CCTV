import socket, cv2, base64, pickle, struct
import numpy as np

class Socket:
    def __init__(self, ip) -> None:
        #self.raspberry = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        #address = 'e4:5f:01:9e:52:d0'
        #port=1
        self.raspberry = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address=ip # 직접 연결
        self.port=9000
        self.raspberry.connect((self.address,self.port))
        self.data_buffer = b""
        self.data_size = struct.calcsize("L")
    
    def recv_image(self):
        while 1:
            try:
                image=self.raspberry.recv(4096)
                self.raspberry.send('O'.encode()) # Send OK
                print('OK')
                return image
            except:
                self.raspberry.close()
                self.raspberry.connect((self.address,self.port))
                print('socket reconnected')
                # self.data_buffer=b''
                # self.data_size=struct.calcsize("L")

    def give_image(self):
        # 설정한 데이터의 크기보다 버퍼에 저장된 데이터의 크기가 작은 경우
        while len(self.data_buffer) < self.data_size:
            self.data_buffer += self.recv_image()

        packed_data_size = self.data_buffer[:self.data_size]
        self.data_buffer = self.data_buffer[self.data_size:] 

        frame_size = struct.unpack(">L", packed_data_size)[0]
        
        # 프레임 데이터의 크기보다 버퍼에 저장된 데이터의 크기가 작은 경우
        while len(self.data_buffer) < frame_size:
            self.data_buffer += self.recv_image()
        
        # 프레임 데이터 분할
        frame_data = self.data_buffer[:frame_size]
        self.data_buffer = self.data_buffer[frame_size:]
        
        #print("수신 프레임 크기 : {} bytes".format(frame_size))
        frame = pickle.loads(frame_data)  
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        return frame

    def test(self):
        while 1:
            cv2.imshow('a', self.give_image())
            cv2.waitKey(1)

# s=Socket('192.168.29.2')
# s.test()