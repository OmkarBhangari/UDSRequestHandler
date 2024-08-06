import time
import queue
import threading
import ttkbootstrap as ttk
import asyncio
from pcan import PCAN  # Ensure the pcan module is correctly installed
from UDSException import *
from frame import Frame

class Tx:
    def __init__(self, pcan, Tx_ID):
        self.pcan = pcan
        self.Tx_ID = Tx_ID

    def transmit(self, data):
        self.pcan.send_frame(self.Tx_ID, data)

class Rx:
    def __init__(self, pcan, Rx_ID):
        self.pcan = pcan
        self.Rx_ID = Rx_ID

    def receive(self):
        data = self.pcan.receive_frame()
        return data

class TP:
    def __init__(self, frame, uds):
        self.block_size = 4
        self.time_between_consecutive_frames = 20
        self.frame = frame
        self.active_transation = None
        self.uds = uds

        self.buffer = queue.Queue()

        self.data = []
        self.data_length = None # will be set later when we require to use the service
        self.remaining_data_length = None # will be set later when we require to use the service

    def push_to_buffer(self, frame, frame_type):
        self.buffer.put({"frame_type": frame_type, "frame": frame})        

    def main(self):
        if self.active_transation:
            if not self.buffer.empty():
                frame_data = self.buffer.get()

                if frame_data['frame_type'] == Frame.FIRST_FRAME:
                    self.data_length, self.data = self.frame.extract_length_and_data(frame_data['frame'])
                    self.uds.push_frame((0x30, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00))


class UDS:
    __Ox19: int = 0x19

    def __init__(self, Tx_ID, Rx_ID):
        self.Tx_ID = Tx_ID
        self.Rx_ID = Rx_ID

        self.pcan = PCAN("PCAN_USBBUS1", "PCAN_BAUD_500K", "PCAN_MESSAGE_STANDARD")
        self.frame = Frame()
        self.tp = TP(self.frame, self)

        self.tx = Tx(self.pcan, self.Tx_ID)
        self.rx = Rx(self.pcan, self.Rx_ID)

        self.active_transation = None # __class__.__Ox19
        self.queue = queue.Queue()
        self.handlers = {
            0x10: Ox10(self),
            0x19: Ox19(self)
            # Add other handlers as needed
        }

        event_thread = threading.Thread(target=self.__event_loop, daemon=True)
        event_thread.start()

    def __event_loop(self):
        while True:
            if not self.queue.empty():
                frame = self.queue.get()
                self.tx.transmit(frame)
                print(f"Frame {frame} transmitted")
            
            received_frame = self.rx.receive()
            print("Received Frame", self.frame.hex(received_frame))
            
            try:
                frame_type = self.frame.validate_frame(received_frame)
            except UDSException as e:
                print(e)
                sid = self.frame.get_sid(received_frame, Frame.ERROR_FRAME)
                self.push_to_buffer(sid, received_frame)
            except Exception as e:
                print(e)
            else:
                if frame_type == Frame.SINGLE_FRAME:
                    sid = self.frame.get_sid(received_frame, Frame.SINGLE_FRAME)
                    self.push_to_buffer(sid, received_frame)

                elif frame_type == Frame.FIRST_FRAME:
                    sid = self.frame.get_sid(frame, Frame.FIRST_FRAME)
                    self.tp.active_transation = sid
                    self.tp.push_to_buffer(received_frame, Frame.FIRST_FRAME)

                elif frame_type == Frame.CONSECUTIVE_FRAME:
                    print("CONNNNSECUTIVE FRAMMMMMMMMMME")
                    self.tp.push_to_buffer(received_frame, Frame.CONSECUTIVE_FRAME)

            self.tp.main()

            time.sleep(1)

    def push_frame(self, frame):
        self.queue.put(frame)

    def push_to_buffer(self, sid, frame):
        handler = self.handlers.get(sid)
        if handler:
            handler.push_frame_to_buffer(frame)
        else:
            print(f"No handler for SID {sid}")

class Ox10:
    START_SESSION = (0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00)

    def __init__(self, uds):
        self.uds = uds
        self.buffer = []

    async def send_start_session_request(self):
        self.uds.push_frame(Ox10.START_SESSION)

    def push_frame_to_buffer(self, frame):
        self.buffer.append(frame)

class Ox19:
    DTC_REQUEST = (0x03, 0x19, 0x02, 0x09, 0x00, 0x00, 0x00, 0x00)

    def __init__(self, uds):
        self.uds = uds
        self.buffer = []

    async def send_dtc_request(self):
        self.uds.push_frame(Ox19.DTC_REQUEST)

    def push_frame_to_buffer(self, frame):
        self.buffer.append(frame)

class GuiInterface:
    def __init__(self, master):
        self.master = master
        master.title("UDS Interface")

        self.uds = UDS(0x743, 0x763)
        self.ox19 = Ox19(self.uds)
        self.ox10 = Ox10(self.uds)

        self.start_session_button = ttk.Button(master, text="Start Session", command=self.run_async_function(self.start_session))
        self.start_session_button.pack()

        self.send_dtc_button = ttk.Button(master, text="Send DTC Request", command=self.run_async_function(self.send_dtc_request))
        self.send_dtc_button.pack()

        self.log = ttk.Text(master)
        self.log.pack()

    async def start_session(self):
        await self.ox10.send_start_session_request()
        self.log.insert(ttk.END, "Session started\n")

    async def send_dtc_request(self):
        await self.ox19.send_dtc_request()
        self.log.insert(ttk.END, "DTC Request sent\n")

    def run_async_function(self, async_func):
        def wrapper():
            asyncio.run_coroutine_threadsafe(async_func(), asyncio_loop)
        return wrapper

# Function to run the asyncio event loop
def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Create an asyncio event loop in a separate thread
asyncio_loop = asyncio.new_event_loop()
t = threading.Thread(target=start_async_loop, args=(asyncio_loop,), daemon=True)
t.start()

# Set up the GUI
root = ttk.Window()
gui = GuiInterface(root)
root.mainloop()
