from .pcan import PCAN
from .frame import Frame
from .TP import TP
import threading
import queue
from . import Colors
import time
from .UDSException import *
from .Ox10 import Ox10
from .Ox19 import Ox19


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

class UDS:
    def __init__(self, Tx_ID, Rx_ID):
        self.Tx_ID = Tx_ID
        self.Rx_ID = Rx_ID

        self.pcan = PCAN("PCAN_USBBUS1", "PCAN_BAUD_500K", "PCAN_MESSAGE_STANDARD")
        self.frame = Frame()
        self.tp = TP(self.frame, self)

        self.tx = Tx(self.pcan, self.Tx_ID)
        self.rx = Rx(self.pcan, self.Rx_ID)

        self.active_transation = None
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
                    sid = self.frame.get_sid(received_frame, Frame.FIRST_FRAME)
                    self.tp.active_transation = self.handlers.get(sid)
                    self.tp.push_to_buffer(received_frame, Frame.FIRST_FRAME)

                elif frame_type == Frame.CONSECUTIVE_FRAME:
                    print("CONNNNSECUTIVE FRAMMMMMMMMMME")
                    self.tp.push_to_buffer(received_frame, Frame.CONSECUTIVE_FRAME)

            self.tp.main()
            self.handlers.get(0x19).main()

            time.sleep(1)

    def push_frame(self, frame):
        self.queue.put(frame)

    def push_to_buffer(self, sid, frame):
        handler = self.handlers.get(sid)
        if handler:
            handler.push_frame_to_buffer(frame)
        else:
            print(f"No handler for SID {sid}")