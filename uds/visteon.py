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
    pass

class UDS:
    def __init__(self, Tx_ID, Rx_ID):
        self.Tx_ID = Tx_ID
        self.Rx_ID = Rx_ID

        self.pcan = PCAN("PCAN_USBBUS1", "PCAN_BAUD_500K", "PCAN_MESSAGE_STANDARD")
        self.frame = Frame()

        self.tx = Tx(self.pcan, self.Tx_ID)
        self.rx = Rx(self.pcan, self.Rx_ID)

        self.queue = queue.Queue()

        event_thread = threading.Thread(target=self.__event_loop, daemon=True)
        event_thread.start()

    def __event_loop(self):
        while True:
            if not self.queue.empty():
                frame = self.queue.get()
                self.tx.transmit(frame)
                print(f"Frame {frame} transmitted")
            
            received_frame = self.rx.receive()
            try:
                frame_type = self.frame.validate_frame(received_frame)
            except UDSException as e:
                print(e)
            except Exception as e:
                print(e)
            else:
                if frame_type == Frame.SINGLE_FRAME:
                    print("Single Frame Received")
                else:
                    print("First Frame Received")
            '''

            if frame_type == "single frame":
                extract_data = received_frame
                if extract_data.recepient == "0x19":
                    # send data to 0x19 and trigger an event
                    pass
                elif extract_data.recepient == "0x19":
                    # send data to 0x10 and trigger an event
                    pass
            '''

            print(received_frame)
            time.sleep(1)

    def push_frame(self, frame):
        self.queue.put(frame)

class Ox10:
    START_SESSION = (0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00)

    def __init__(self, uds):
        self.uds = uds

    async def send_start_session_request(self):
        self.uds.push_frame(Ox10.START_SESSION)

class Ox3E:
    pass

class Ox22:
    pass

class Ox2E:
    pass

class Ox19:
    DTC_REQUEST = (0x03, 0x19, 0x02, 0x09, 0x00, 0x00, 0x00, 0x00)

    def __init__(self, uds):
        self.uds = uds

    async def send_dtc_request(self):
        self.uds.push_frame(Ox19.DTC_REQUEST)

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
