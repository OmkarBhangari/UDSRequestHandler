from typing import Callable, Dict, List
import queue
import threading
import time
from rich.table import Table
from rich.console import Console
from PCANBasic import *
from pcan_constants import *
from abc import ABC, abstractmethod

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

class CANInterface(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def send_frame(self, arbitration_id, data):
        pass

    @abstractmethod
    def receive_frame(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

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

    def send_frame(self, frame_data):
        frame = TPCANMsg()
        frame.ID = frame_data['id']
        frame.MSGTYPE = self.message_type
        frame.DATA = frame_data['data']
        frame.LEN = len(frame_data['data'])

        result = self.pcan.Write(self.channel, frame)
        if result != PCAN_ERROR_OK:
            print(f"Error transmitting CAN message: {result}")

    def receive_frame(self):
        result, msg, timestamp = self.pcan.Read(self.channel)
        
        if result == PCAN_ERROR_OK:
            frame = {
                'id': msg.ID,
                'data': tuple(msg.DATA[:msg.LEN])
            }
            self.event_manager.publish("FRAME_RECEIVED", frame)
            self.event_manager.publish("data_received", msg.DATA[:msg.LEN])
        else:
            print(f"Error receiving frame: {result}")

    def cleanup(self):
        self.pcan.Uninitialize(self.channel)

class Tx:
    def __init__(self, event_manager, Tx_ID):
        self.event_manager = event_manager
        self.Tx_ID = Tx_ID
        self.event_manager.subscribe("SEND_FRAME", self.transmit)

    def transmit(self, frame_data):
        self.event_manager.publish("SEND_FRAME", {"id": self.Tx_ID, "data": frame_data['data']})

class Rx:
    def __init__(self, event_manager, Rx_ID):
        self.event_manager = event_manager
        self.Rx_ID = Rx_ID
        self.event_manager.subscribe("FRAME_RECEIVED", self.handle_received_frame)

    def handle_received_frame(self, frame):
        if frame['id'] == self.Rx_ID:
            self.event_manager.publish("data_received", frame['data'])

'''class Frame:
    SINGLE_FRAME = 0
    FIRST_FRAME = 1
    CONSECUTIVE_FRAME = 2

    @staticmethod
    def validate_frame(frame):
        if frame[0] & 0xF0 == 0x00:
            return Frame.SINGLE_FRAME
        elif frame[0] & 0xF0 == 0x10:
            return Frame.FIRST_FRAME
        elif frame[0] & 0xF0 == 0x20:
            return Frame.CONSECUTIVE_FRAME
        else:
            return None

    @staticmethod
    def extract_length(frame_type,frame):
        if frame_type == Frame.SINGLE_FRAME:
            return frame[0] & 0x0F
        elif frame_type == Frame.FIRST_FRAME:
            return (frame[0] & 0x0F) << 8 | frame[1]
        else:
            return None

    @staticmethod
    def construct_flow_control(block_size, separation_time):
        return bytes([0x30, block_size, separation_time])

    @staticmethod
    def hex(data):
        return [hex(byte) for byte in data]
'''
class CAN_TP:
    def __init__(self, TX_ID, RX_ID, channel, baudrate, msg_type, event_manager: EventManager) -> None:
        self.TX_ID = TX_ID
        self.RX_ID = RX_ID
        self.event_manager = event_manager
        self.event_manager.subscribe('data_received', self.get_data)
        self.store_data = []
        self.buffer_to_can = queue.Queue()
        self.buffer_from_uds = queue.Queue()

        self.bytes = None
        self.no_of_frames = None
        self.counter = 0
        self.block_size = 4
        self.time_between_consecutive_frames = 20

    def get_data(self, frame):
        self.process_frame(frame)

    def send_data(self, data):
        self.event_manager.publish("SEND_FRAME", {"id": self.TX_ID, "data": data})

    def process_frame(self, frame):
        self.frame_type = Frame.validate_frame(frame)

        if self.frame_type == Frame.SINGLE_FRAME:
            self.store_data = []
            self.temp = frame[1:]
            self.store_data.extend(self.temp)
            self.route_frame()

        elif self.frame_type == Frame.FIRST_FRAME:
            self.bytes = Frame.extract_length(self.frame_type,frame)
            self.no_of_frames = self.bytes // 7
            self.counter = 0
            self.temp = frame[2:]
            self.store_data.extend(self.temp)

        elif self.frame_type == Frame.CONSECUTIVE_FRAME:
            self.counter -= 1
            self.no_of_frames -= 1
            self.temp = frame[1:]
            self.store_data.extend(self.temp)
        
        if self.no_of_frames == 0:
            self.route_frame()

        if self.counter == 0:
            self.counter = min(self.no_of_frames, self.block_size)
            self.FC_frame = Frame.construct_flow_control(self.counter, self.time_between_consecutive_frames)
            self.send_data(self.FC_frame)

    def route_frame(self):
        self.store_data = Frame.hex(self.store_data)
        self.store_data = tuple(self.store_data)
        self.event_manager.publish('data_to_uds', self.store_data)

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
    event_manager = EventManager()

    can_channel = "PCAN_USBBUS1"
    can_baud = "PCAN_BAUD_500K"
    can_msg_type = "PCAN_MESSAGE_EXTENDED"

    can_interface = PCANWrapper(event_manager, can_channel, can_baud, can_msg_type)

    TX_ID = 0x743
    RX_ID = 0x763
    can_tp = CAN_TP(TX_ID, RX_ID, can_channel, can_baud, can_msg_type, event_manager)

    tx = Tx(event_manager, TX_ID)
    rx = Rx(event_manager, RX_ID)

    def handle_incoming_frame(data):
        print(f"Received frame data: {data}")

    event_manager.subscribe("INCOMING_FRAME", handle_incoming_frame)

    try:
        while True:
            can_interface.receive_frame()
            can_tp.cantp_monitor()
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Stopping CAN communication.")
    finally:
        can_interface.cleanup()

if __name__ == "__main__":
    main()