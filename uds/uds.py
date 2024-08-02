import time
import queue
import threading

class UDS:
    def __init__(self):
        self.main_queue = queue.Queue()

        event_thread = threading.Thread(target=self.event_loop)
        event_thread.start()
        
    def event_loop(self):
        while True:
            print(self.main_queue.get())
            time.sleep(1)

    def push_frame(self, frame):
        self.main_queue.put(frame)

uds = UDS()
time.sleep(3)
uds.push_frame(2)