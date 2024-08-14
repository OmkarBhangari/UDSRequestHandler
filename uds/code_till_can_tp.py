from typing import Callable, Dict, List
import queue
import threading
import time
from rich.table import Table
from rich.console import Console
from PCANBasic import *
from pcan_constants import *
from abc import ABC ,abstractmethod
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


    def send_frame(self, arbitration_id, data):
        frame=TPCANMsg ()
        frame.ID=arbitration_id
        frame.MSGTYPE=self.message_type
        frame.DATA=data
        frame.LEN=len(data)

        result = self.pcan.Write(self.channel, frame)  
        if result != PCAN_ERROR_OK:
            print("Error transmitting CAN message:", result) 

    def receive_frame(self)-> None:
        result, msg, timestamp = self.pcan.Read(self.channel)
        
        if result == PCAN_ERROR_OK:
            frame = {
                'id': msg.ID,
                'data': tuple(msg.DATA[:msg.LEN])
            }
            self.event_manager.publish("FRAME_RECEIVED", frame)
        else:
            print(f"Error receiving frame: {result}")     

    def cleanup(self):
        self.pcan.Uninitialize(self.channel)                  
    
class Tx:
    def __init__(self,event_manager,Tx_ID) :
        self.event_manager=event_manager
        self.Tx_ID=Tx_ID
        self.frame_queue=queue.Queue


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
#now hardware part is done we have to start with TP part now for vallidation of the received frames            
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

    # Subscribe to the "INCOMING_FRAME" event to handle received frames
    def handle_incoming_frame(data):
        print(f"Received frame data: {data}")
        # Add validation logic here

    event_manager.subscribe("INCOMING_FRAME", handle_incoming_frame)

    # Main loop to read from ECU
    try:
        while True:
            # Check for incoming frames (non-blocking)
            pcan.receive_frame()

            # Add any additional logic here (e.g., processing received frames)
            time.sleep(1)  # Sleep to avoid busy-waiting
    except KeyboardInterrupt:
        print("Stopping CAN communication.")

if __name__ == "__main__":
    main()