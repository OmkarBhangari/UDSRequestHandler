from . import Colors
from .frame import Frame
from .event_manager import EventManager
from .interface_wrapper import PCANWrapper
from .pcan import PCAN
import queue

class Tx:
    def __init__(self, comm_interface, Tx_ID):
        self.comm_interface = comm_interface
        self.Tx_ID = Tx_ID

    def transmit(self):
        if not CAN.tx_buffer.empty():
            self.data = CAN.tx_buffer.get()
            self.comm_interface.send_frame(self.Tx_ID, self.data)
            print(f"{Colors.blue}Transmitted : {Frame.hex(self.data)}{Colors.reset}")


class Rx:
    def __init__(self, comm_interface, Rx_ID, event_manager):
        self.comm_interface = comm_interface
        self.Rx_ID = Rx_ID
        self.event_manager = event_manager

    def receive(self):
        self.data = self.comm_interface.receive_frame()

        # Check if the frame is all zeros
        if all(byte == 0 for byte in self.data):
            return  # Ignore the frame and do not print or publish it

        CAN.rx_buffer.put(self.data)
        print(f"{Colors.yellow}Received : {Frame.hex(self.data)}{Colors.reset}")
        self.event_manager.publish('data_received', self.data)


class CAN:
    tx_buffer = queue.Queue()
    rx_buffer = queue.Queue()
    #def __init__(self, TX_ID, RX_ID, channel, baudrate, msg_type, event_manager: EventManager) -> None:
    def __init__(self, TX_ID, RX_ID, channel, baudrate, msg_type, event_manager: EventManager) -> None:
        self.comm_interface = PCANWrapper()
        self.comm_interface.initialize(channel, baudrate, msg_type)
        #self.comm_interface = pcan
        self.event_manager = event_manager

        self.tx = Tx(self.comm_interface, TX_ID)
        self.rx = Rx(self.comm_interface, RX_ID, self.event_manager)

        

    # adds data to the tx_buffer to send data to ecu
    # method is called from can_tp.py
    def transmit_data(self, data):
        print(f"Transmitting data: {data}")  # Debug line
        CAN.tx_buffer.put(data)

    # this function is called from app.py for continuous monitoring
    def can_monitor(self):
        self.tx.transmit()
        self.rx.receive()