import threading
import time

timers=[]
socket_io=None

class Timer:
    def __init__(self, secs) -> None:
        thread = threading.Thread(target=self.timer, args=(secs,))
        thread.start()

    elapsed_time=0
    timer_ended=False
    how_long_stopped=0
    stopped_object=False
    def timer(self, secs):
        for i in range(secs):
            '''if self.stopped_object==True:
                self.how_long_stopped+=1
            if self.how_long_stopped>0.1*secs:
                self.timer_ended=True'''
            if self.timer_ended==True:
                return
            time.sleep(1)
            self.elapsed_time=i
        self.timer_ended=True
    def alarm(self):
        message="Ilegal parking detected"
        socket_io.emit("message from python", message)
        self.timer_ended=False