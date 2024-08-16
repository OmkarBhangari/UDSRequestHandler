from .can_tp import CAN_TP
from .event_manager import EventManager
from .UDSException import UDSException
from .frame import Frame
from .Ox19 import Ox19
from .Ox22 import Ox22
import queue

class UDS:
    def __init__(self, tx_id, rx_id, channel, baud_rate, message_type, event_manager: EventManager):
        #self.can_tp = can_tp
        self.event_manager = event_manager
        self.can_tp = CAN_TP(tx_id, rx_id, channel, baud_rate, message_type, self.event_manager)
        self.event_manager.subscribe('data_to_uds', self.process_response)
        self.buffer_to_cantp = queue.Queue()
        self.response_buffer = queue.Queue()
        self.frame = Frame()

        self.handlers = {
            #0x10: Ox10(self),
            0x19: Ox19(self),
            0x22: Ox22(self)
        }

    def send_request(self, data):
        """ request = bytes([service_id]) + data
        self.buffer_to_cantp.put(request) """
        # Put the request tuple into the buffer
        print(data)  # debug line
        self.buffer_to_cantp.put(data)

    def process_request_queue(self):
        while not self.buffer_to_cantp.empty():
            request = self.buffer_to_cantp.get()
            print(request)  # debug line
            self.can_tp.receive_data_from_uds(request)

    # data received from can_tp
    def process_response(self, response):
        try:
            print("process_response", response)
            if response[0] == '0x7F':  # Negative response
                print("Negative Response Detected:", response)
                nrc = response[2]
                print("NRC:", nrc)
                raise UDSException.create_exception(nrc)
            # self.response_buffer.put(response)
            self.direct_to_sid(response)
        except UDSException as e:
            print(f"UDS Error: {e}")
            self.response_buffer.put(e)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            # You might want to handle the exception differently based on your requirements

    # method is called from gui.py to display the results
    def get_response(self):
        if not self.response_buffer.empty():
            return self.response_buffer.get()
        return None

    def direct_to_sid(self, response):
        self.Frame_response = response
        print("direct_to_sid", self.Frame_response)
        """ self.sid = self.frame.hex(self.Frame_response)
        print(self.sid) """
        self.sid = self.frame.get_sid(self.Frame_response)
        print("sid received: ",self.sid)

        handler = self.handlers.get(self.sid)
        if handler: handler.buffer_frame(self.Frame_response)
        else: print(f"No handler for SID {self.sid}")
        
    # called from sid
    def add_from_sid(self, data):
        self.response_buffer.put(data)