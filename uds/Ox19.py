import queue
from . import Colors
from .TP import TP 

class Ox19:
    DTC_REQUEST = (0x03, 0x19, 0x02, 0x09, 0x00, 0x00, 0x00, 0x00)

    def __init__(self, uds):
        self.uds = uds
        self.buffer = queue.Queue()

    async def send_dtc_request(self):
        self.uds.queue_frame(Ox19.DTC_REQUEST)

    def buffer_frame(self, frame):
        self.buffer.put(frame)

    def main(self):
        if not self.buffer.empty():
            data = self.buffer.get()
            DTC_data=TP.extract_data(data)
            print(f"{Colors.green}{DTC_data}{Colors.reset}")