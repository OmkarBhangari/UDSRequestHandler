import threading
import ttkbootstrap as ttk
import asyncio
from uds import UDS, Ox19, Ox10

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
