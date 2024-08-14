from typing import Callable, Dict, List
import queue
import threading
import time
from rich.table import Table
from rich.console import Console
from PCANBasic import *
from pcan_constants import *
from abc import ABC ,abstractmethod
from frame import Frame
from UDSException import UDSException
class CANInterface(ABC):


    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def send_frame(self):
        pass

    @abstractmethod
    def receive_frame(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

class Colors:
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    RESET = "\033[0m"


class EventManager:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)

    def publish(self, event_type: str, data: any = None):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(data)
class PCANWrapper(CANInterface):
    def __init__(self, event_manager, channel, baud, message_type):
        self.event_manager = event_manager
        self.pcan = PCANBasic()
        self.channel = PCAN_CHANNELS[channel]
        self.baudrate = PCAN_BAUD_RATES[baud]
        self.message_type = PCAN_MESSAGE_TYPES[message_type]
        self.initialize() 

    def initialize(self):
        result = self.pcan.Initialize(self.channel, self.baudrate)
        if result != PCAN_ERROR_OK:
            raise Exception(f"Error initializing PCAN channel: {result}")
        self.event_manager.subscribe("SEND_FRAME", self.send_frame)
        self.event_manager.subscribe("RECEIVE_FRAME", self.receive_frame)


    def send_frame(self, frame_data):
        frame = TPCANMsg()
        frame.ID = frame_data['id']
        frame.MSGTYPE = self.message_type
        frame.DATA = frame_data['data']
        frame.LEN = len(frame_data['data'])

        result = self.pcan.Write(self.channel, frame)
        if result != PCAN_ERROR_OK:
            print("Error transmitting CAN message:", result)
    def receive_frame(self)-> None:
        result, msg, timestamp = self.pcan.Read(self.channel)
        
        if result == PCAN_ERROR_OK:
            self.event_manager.publish("DATA_RECEIVED", msg.DATA)
        else:
            print(f"Error receiving frame: {result}")     

    def cleanup(self):
        self.pcan.Uninitialize(self.channel)                  
    
class Tx:
    def __init__(self,event_manager,Tx_ID) :
        self.event_manager=event_manager
        self.Tx_ID=Tx_ID
        self.frame_queue = queue.Queue()  


    def queue_frame(self, data):
      self.frame_queue.put(data) 

    def dispatch_frame(self):
        if not self.frame_queue.empty():
            frame = self.frame_queue.get()
            self.transmit(frame)

    def transmit(self, data):
        self.event_manager.publish("SEND_FRAME",{"id": self.Tx_ID,"data" : data})
       # print(f"{Colors.BLUE}Transmitted : {Frame.hex(data)}{Colors.RESET}")


class Rx:
    def __init__(self,event_manager,Rx_ID):
        self.event_manager=event_manager
        self.Rx_ID = Rx_ID
        self.event_manager.subscribe("FRAME_RECEIVED", self.handle_received_frame)


    def handle_received_frame(self, frame):
        if frame['id'] == self.Rx_ID:
           # print(f"{Colors.YELLOW}Received : {Frame.hex(frame['data'])}{Colors.RESET}")
            self.event_manager.publish("INCOMING_FRAME", frame['data'])
              
#now hardware part is done we have to start with TP part now for validation of the received frames  
class CAN_TP:
    def __init__(self, TX_ID, RX_ID, channel, baudrate, msg_type, event_manager: EventManager) -> None:
        self.frame_validator = Frame()
        self.TX_ID = TX_ID
        self.RX_ID = RX_ID
        self.event_manager = event_manager
        self.event_manager.subscribe('DATA_RECEIVED', self.process_frame)
        self.store_data = []
        self.buffer_to_can = queue.Queue()
        self.buffer_from_uds = queue.Queue()

        self.bytes = None
        self.no_of_frames = None
        self.counter = 0
        self.block_size = 4
        self.time_between_consecutive_frames = 20

    def send_data(self, data):
        self.event_manager.publish("SEND_FRAME", {"id": self.TX_ID, "data": data})

    def process_frame(self, frame):
        try:
            self.frame_type = self.frame_validator.validate_frame(frame)
            
            if self.frame_type == Frame.SINGLE_FRAME:
                print("single frame received")
                self.store_data = []
                self.temp = frame[1:]
                self.store_data.extend(self.temp)
                self.route_frame()

            elif self.frame_type == Frame.FIRST_FRAME:
                print("first frame received")
                self.bytes = self.frame_validator.extract_length(frame)
                self.no_of_frames = self.bytes // 7
                self.counter = 0
                self.temp = frame[2:]
                self.store_data.extend(self.temp)

            elif self.frame_type == Frame.CONSECUTIVE_FRAME:
                print("consecutive frame received")
                self.counter -= 1
                self.no_of_frames -= 1
                self.temp = frame[1:]
                self.store_data.extend(self.temp)
            
            if self.no_of_frames == 0:
                self.route_frame()

            if self.counter == 0:
                self.counter = min(self.no_of_frames, self.block_size)
                self.FC_frame = self.frame_validator.construct_flow_control(self.counter, self.time_between_consecutive_frames)
                self.send_data(self.FC_frame)

        except UDSException as e:
            print(f"UDS Exception: {e}")
            # Handle UDS exception (e.g., log it, notify user, etc.)
        except Exception as e:
            print(f"Error processing frame: {e}")
            

    def route_frame(self):
        self.store_data = self.store_data
        self.event_manager.publish('DATA_TO_UDS', self.store_data)

    def process_uds_data(self, data):
        if len(data) <= 7:
            frame = bytearray([len(data)])
            frame.extend(data)
            frame.extend([0] * (8 - len(frame)))
            self.buffer_to_can.put(frame)
        else:
            self.send_multi_frame(data)

    def send_multi_frame(self, data):
        total_length = len(data)
        
        first_frame = bytearray([0x10 | (total_length >> 8), total_length & 0xFF])
        first_frame.extend(data[:6])
        self.buffer_to_can.put(first_frame)

        remaining_data = data[6:]
        sequence_number = 1
        while remaining_data:
            frame = bytearray([0x20 | (sequence_number & 0x0F)])
            frame.extend(remaining_data[:7])
            if len(frame) < 8:
                frame.extend([0] * (8 - len(frame)))
            self.buffer_to_can.put(frame)
            remaining_data = remaining_data[7:]
            sequence_number = (sequence_number + 1) & 0x0F

    def send_data_to_can(self):
        while not self.buffer_to_can.empty():
            self.frame = self.buffer_to_can.get()
            self.send_data(self.frame)

    def receive_data_from_uds(self, data):
        self.buffer_from_uds.put(data)

    def process_uds_queue(self):
        while not self.buffer_from_uds.empty():
            data = self.buffer_from_uds.get()
            self.process_uds_data(data)

    def cantp_monitor(self):
        self.process_uds_queue()
        self.send_data_to_can()
          
def main():
    # Initialize EventManager
    event_manager = EventManager()

    # Define PCAN configuration
    channel_used = "PCAN_USBBUS1"  # Change as per your setup
    baud_rate = "PCAN_BAUD_500K"  # Change as per your setup
    msg_type = "PCAN_MESSAGE_EXTENDED"  # Change to "EXTENDED" if using extended IDs

    # Initialize PCAN
    pcan = PCANWrapper(event_manager, channel_used, baud_rate, msg_type)

    # Initialize Tx and Rx
    tx = Tx(event_manager, Tx_ID=0x743)  # Example Tx ID, change as needed
    rx = Rx(event_manager, Rx_ID=0x763)  # Example Rx ID, change as needed
    TX_ID=0x743
    RX_ID=0x763
    can_tp = CAN_TP(TX_ID, RX_ID, channel_used, baud_rate, msg_type, event_manager)

    # Main loop to read from ECU
    try:
        while True:
            # Check for incoming frames (non-blocking)
            pcan.receive_frame()
            can_tp.cantp_monitor()
            time.sleep(1)  # Red

            # Add any additional logic here (e.g., processing received frames)
            # Sleep to avoid busy-waiting
    except KeyboardInterrupt:
        print("Stopping CAN communication.")
    finally:
     pcan.cleanup()
if __name__ == "__main__":
    main()