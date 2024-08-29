from . import Colors
from .frame import Frame
from .event_manager import EventManager
from .Interface import get_hardware_interface
import queue

class Tx:
    def __init__(self, hardware_interface, tx_id, tx_buffer, event_manager):
        self.hardware_interface = hardware_interface
        self.tx_id = tx_id
        self._tx_buffer = tx_buffer
        self.event_manager = event_manager

    def transmit(self):
        if not self._tx_buffer.empty():
            data = self._tx_buffer.get()
            self.hardware_interface.send_frame(self.tx_id, data)
            print(f"{Colors.blue}Transmitted : {Frame.hex(data)}{Colors.reset}")
            self.event_manager.publish('terminal', ['transmitted', data])


class Rx:
    def __init__(self, hardware_interface, rx_id, rx_buffer, event_manager):
        self.hardware_interface = hardware_interface
        self.rx_id = rx_id
        self._rx_buffer = rx_buffer
        self.event_manager = event_manager

    def receive(self):
        data, id = self.hardware_interface.receive_frame()

        # TODO: Comment the following 3 lines of code later, it was written to prevent the terminal from getting populated by zero value frames
        # Check if the frame is all zeros
        if all(byte == 0 for byte in data):
            return  # Ignore the frame and do not print or publish it

        if(id == self.rx_id):
            print(data, "______", id)   # debug line
            self._rx_buffer.put(data) # this is not being used currently 
            print(f"{Colors.yellow}Received : {Frame.hex(data)}{Colors.reset}")
            self.event_manager.publish('data_received', data)
            self.event_manager.publish('terminal', ['received', data])


class CAN:
    def __init__(self, tx_id, channel, baudrate, msg_type, event_manager: EventManager):

        self.event_manager = event_manager
        self.hardware_interface = get_hardware_interface("pcan", channel, baudrate, msg_type)

        self._tx_buffer = queue.Queue()
        self._rx_buffer = queue.Queue()

        self.event_manager.subscribe('rx_id', self.get_rx_id)

        self.tx = Tx(self.hardware_interface, tx_id, self._tx_buffer, self.event_manager)
        

    # adds data to the tx_buffer to send data to ecu
    # method is called from can_tp.py
    def transmit_data(self, data):
        self._tx_buffer.put(data)

    def get_rx_id(self, id):
        self.rx_id = id
        self.rx = Rx(self.hardware_interface, self.rx_id, self._rx_buffer, self.event_manager)

    # this function is called from app.py for continuous monitoring
    def can_monitor(self):
        self.tx.transmit()
        self.rx.receive()