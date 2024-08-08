import threading
import ttkbootstrap as ttk
import asyncio
from uds import UDS, Ox19, Ox10

class GuiInterface:
    def __init__(self, master):
        self.master = master
        master.title("UDS Interface")

        self.uds_wrapper = UdsWrapper(0x743, 0x763)

        self.start_session_button = ttk.Button(master, text="Start Session", command=self.run_async_function(self.start_session))
        self.start_session_button.pack()

        self.send_dtc_button = ttk.Button(master, text="Send DTC Request", command=self.run_async_function(self.send_dtc_request))
        self.send_dtc_button.pack()

        self.log = ttk.Text(master)
        self.log.pack()

    async def start_session(self):
        result = await self.uds_wrapper.execute_sid(0x10)
        self.log.insert(ttk.END, f"Session started: {result}\n")

    async def send_dtc_request(self):
        result = await self.uds_wrapper.execute_sid(0x19)
        self.log.insert(ttk.END, f"DTC Request sent: {result}\n")

    def run_async_function(self, async_func):
        def wrapper():
            asyncio.run_coroutine_threadsafe(async_func(), asyncio_loop)
        return wrapper

class UdsWrapper:
    def __init__(self, tx_ID, rx_ID):
        self.uds = UDS(tx_ID, rx_ID)
        self.ox19 = Ox19(self.uds)
        self.ox10 = Ox10(self.uds)
        self.sid_handlers = {}

    async def start_session(self, session_type=1):
        """Start a diagnostic session."""
        return await self.ox10.start_session(session_type)

    async def send_dtc_request(self, dtc_type=0):
        """Send a DTC request."""
        return await self.ox19.send_dtc_request(dtc_type)

    def sid_handler(self, sid, handler):
        self.sid_handlers[sid] = handler

    async def execute_sid(self, sid, *args, **kwargs):
        if sid == 0x10:
            return await self.start_session(*args, **kwargs)
        elif sid == 0x19:
            return await self.send_dtc_request(*args, **kwargs)
        elif sid in self.sid_handlers:
            return await self.sid_handlers[sid](*args, **kwargs)
        else:
            raise ValueError(f"Unsupported SID: 0x{sid:02X}")

    async def close(self):
        """Close the UDS connection."""
        await self.uds.close()

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
