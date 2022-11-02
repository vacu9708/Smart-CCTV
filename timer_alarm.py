import threading
import time

timers=[]
socket_io=None

class Timer:
    def __init__(self, slow_object) -> None:
        thread = threading.Thread(target=self.timer, args=(slow_object,))
        thread.start()

    elapsed_time=0
    timer_ended=False
    signal=False
    def timer(self, slow_object):
        while not self.timer_ended:
            '''if self.slow_object==True:
                self.how_long_slow+=1
            else:
                self.how_long_slow-=0'''

            #if self.elapsed_time>500: # Time limit
                #self.timer_ended=True
                #self.signal=True

            time.sleep(1)
            self.elapsed_time+=1

    def notice(self, message):
        print(message)
        #socket_io.emit("message from python", message)

    '''def start_timer(self):
        thread = threading.Thread(target=self.timer)
        thread.start()'''