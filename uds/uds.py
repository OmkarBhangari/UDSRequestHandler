import time
import threading

class UDS:
    def __init__(self):
        self.main_queue = []

        event_thread = threading.Thread(target=self.event_loop)
        event_thread.start()
        
    def event_loop(self):
        while True:
            print("Hello")
            time.sleep(1)

uds = UDS()
