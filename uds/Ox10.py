import queue

class Ox10:
    START_SESSION = (0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00)

    def __init__(self, uds):
        self.uds = uds
        self.buffer = queue.Queue()

    async def send_start_session_request(self):
        self.uds.queue_frame(Ox10.START_SESSION)

    def buffer_frame(self, frame):
        self.buffer.put(frame)
