from typing import Callable, Dict, List
import queue
import threading
import time
from rich.table import Table
from rich.console import Console
from abc import ABC, abstractmethod
from PCANBasic import *
from pcan_constants import *

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

class HardwareInterface(ABC):
    @abstractmethod
    def __init__(self, event_manager: EventManager, **kwargs):
        pass

    @abstractmethod
    def send_frame(self, arbitration_id, data):
        pass

    @abstractmethod
    def receive_frame(self):
        pass

class PCAN(HardwareInterface):
    def __init__(self, event_manager: EventManager, channel, baud, message_type):
        super().__init__(event_manager)
        self.event_manager = event_manager
        self.pcan = PCANBasic()
        self.channel = PCAN_CHANNELS[channel]
        self.baudrate = PCAN_BAUD_RATES[baud]
        self.pcan_channel = self.pcan.Initialize(self.channel, self.baudrate)
        self.message_type = PCAN_MESSAGE_TYPES[message_type]
        
        if self.pcan_channel != PCAN_ERROR_OK:
            raise RuntimeError(f"Error initializing PCAN channel: {self.pcan_channel}")

    def send_frame(self, arbitration_id, data):
        frame = TPCANMsg()
        frame.ID = arbitration_id
        frame.MSGTYPE = self.message_type
        frame.DATA = data
        frame.LEN = len(data)

        result = self.pcan.Write(self.channel, frame)
        if result != PCAN_ERROR_OK:
            raise RuntimeError(f"Error transmitting CAN message: {result}")

    def receive_frame(self):
        result, msg, timestamp = self.pcan.Read(self.channel)
        if result == PCAN_ERROR_OK:
            frame = {
                'id': msg.ID,
                'data': tuple(msg.DATA[:msg.LEN])
            }
            self.event_manager.publish("FRAME_RECEIVED", frame)
        else:
            raise RuntimeError(f"Error receiving frame: {result}")

class HardwareWrapper:
    def __init__(self, event_manager: EventManager, hardware_type: str, **kwargs):
        self.event_manager = event_manager
        self.hardware = self._create_hardware(hardware_type, **kwargs)
        self.event_manager.subscribe("SEND_FRAME", self.send_frame)
        self.event_manager.subscribe("RECEIVE_FRAME", self.receive_frame)

    def _create_hardware(self, hardware_type: str, **kwargs):
        if hardware_type.upper() == "PCAN":
            return PCAN(self.event_manager, **kwargs)
        # Add more hardware types here as needed
        else:
            raise ValueError(f"Unsupported hardware type: {hardware_type}")

    def send_frame(self, data):
        self.hardware.send_frame(data['id'], data['data'])

    def receive_frame(self):
        self.hardware.receive_frame()

class Tx:
    def __init__(self, event_manager: EventManager, Tx_ID):
        self.event_manager = event_manager
        self.Tx_ID = Tx_ID
        self.frame_queue = queue.Queue()

    def queue_frame(self, data):
        self.frame_queue.put(data)

    def dispatch_frame(self):
        if not self.frame_queue.empty():
            frame = self.frame_queue.get()
            self.transmit(frame)

    def transmit(self, data):
        self.event_manager.publish("SEND_FRAME", {"id": self.Tx_ID, "data": data})

class Rx:
    def __init__(self, event_manager: EventManager, Rx_ID):
        self.event_manager = event_manager
        self.Rx_ID = Rx_ID
        self.event_manager.subscribe("FRAME_RECEIVED", self.handle_received_frame)

    def handle_received_frame(self, frame):
        if frame['id'] == self.Rx_ID:
            self.event_manager.publish("INCOMING_FRAME", frame['data'])

class TP:
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.buffer = queue.Queue()
        self.event_manager.subscribe("INCOMING_FRAME", self.handle_incoming_frame)
        # Add more initializations and subscriptions as needed

    def handle_incoming_frame(self, frame):
        # Implement frame handling logic
        pass

    # Add more TP-related methods here
def main():
    event_manager = EventManager()
    #hardware = HardwareWrapper(event_manager, "PCAN", channel="PCAN_USBBUS1", baud="500K", message_type="STANDARD")
    tx = Tx(event_manager, 0x743)  # Example Tx ID
    rx = Rx(event_manager, 0x763)  # Example Rx ID
    tp = TP(event_manager)

    def run():
        while True:
            event_manager.publish("RECEIVE_FRAME")
            tx.dispatch_frame()
            time.sleep(1)

    

if __name__ == "__main__":
    main()