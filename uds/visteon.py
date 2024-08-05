import time
import queue
import threading
import tkinter as tk
from pcan import PCAN  # Ensure the pcan module is correctly installed

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
            print("Hello")

            time.sleep(1)

    def push_frame(self, frame):
        self.queue.put(frame)

class Ox10:
    START_SESSION = (0x02, 0x10, 0x03, 0x09, 0x00, 0x00, 0x00, 0x00)

    def __init__(self, uds):
        self.uds = uds

    def send_start_session_request(self):
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

    def send_dtc_request(self):
        self.uds.push_frame(Ox19.DTC_REQUEST)

class GuiInterface:
    def __init__(self, master):
        self.master = master
        master.title("UDS Interface")

        self.uds = UDS(0x743, 0x763)
        self.ox19 = Ox19(self.uds)
        self.ox10 = Ox10(self.uds)

        self.start_session_button = tk.Button(master, text="Start Session", command=self.start_session)
        self.start_session_button.pack()

        self.send_dtc_button = tk.Button(master, text="Send DTC Request", command=self.send_dtc_request)
        self.send_dtc_button.pack()

        self.log = tk.Text(master)
        self.log.pack()

    def start_session(self):
        self.ox10.send_start_session_request()
        self.log.insert(tk.END, "Session started\n")

    def send_dtc_request(self):
        self.ox19.send_dtc_request()
        self.log.insert(tk.END, "DTC Request sent\n")

# Set up the GUI
root = tk.Tk()
gui = GuiInterface(root)
root.mainloop()
