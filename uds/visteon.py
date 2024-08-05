from pcan import PCAN
import time
import queue
import threading

class Ox10:
    pass
class Ox3E:
    pass
class Ox22:
    pass
class Ox2E:
    pass
class Ox19:
    pass

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
        """ 
        Summary:
            This function checks to see if there are any frames on the 
            bus that we are interested in
        TODO: 
            check to see if the Rx_ID matches with the receiving frames 
            arbitration ID; if not then ignore frame and return false 
            (Indicating that there are no frames)
        Returns:
            data(tuple): data received from the bus
        """
        data = self.pcan.receive_frame()
        return data

class TP:
    pass

# UDS Class will run the event loop
class UDS:
    def __init__(self, Tx_ID, Rx_ID):

        self.Tx_ID = Tx_ID
        self.Rx_ID = Rx_ID

        self.pcan = PCAN("PCAN_USBBUS1", "PCAN_BAUD_500K", "PCAN_MESSAGE_STANDARD")

        self.tx = Tx(self.pcan, self.Tx_ID)
        self.rx = Rx(self.pcan, self.Rx_ID)

        self.queue = queue.Queue()

        event_thread = threading.Thread(target=self.event_loop)
        event_thread.start()
        
    def event_loop(self):
        while True:
            if not self.queue.empty():
                frame = self.main_queue.get()
                self.pcan.send_frame(frame)
                print(frame)

            time.sleep(1)

    def push_frame(self, frame):
        self.main_queue.put(frame)

uds = UDS(0x743, 0x763)