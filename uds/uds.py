import time
import queue
import threading
from .pcan import PCAN

class UDS:
    def __init__(self):
        self.pcan = PCAN("PCAN_USBBUS1", "PCAN_BAUD_500K", "PCAN_MESSAGE_STANDARD", 0x743)

        self.main_queue = queue.Queue()

        event_thread = threading.Thread(target=self.event_loop)
        event_thread.start()
        
    def event_loop(self):
        while True:
            if not self.main_queue.empty():
                frame = self.main_queue.get()
                self.pcan.send_frame(frame)
                print(frame)

            time.sleep(1)

    def push_frame(self, frame):
        self.main_queue.put(frame)



