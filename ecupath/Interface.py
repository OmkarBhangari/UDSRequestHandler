from abc import ABC, abstractmethod
from .PCANBasic import *
from .pcan_constants import *

class HardwareInterface(ABC):
    @abstractmethod
    def send_frame(self, arbitration_id, data):
        pass

    @abstractmethod
    def receive_frame(self):
        pass

class PCAN(HardwareInterface):
    def __init__(self, channel, baud, message_type):
        self.pcan = PCANBasic()  # Initialize the PCANBasic instance
        self.channel = PCAN_CHANNELS[channel]  # Define the PCAN channel you are using (e.g., PCAN_USBBUS1 for the first USB channel)
        self.baudrate = PCAN_BAUD_RATES[baud]  # Define the baud rate (e.g., PCAN_BAUD_500K for 500 kbps)
        self.pcan_channel = self.pcan.Initialize(self.channel, self.baudrate)  # Initialize the PCAN channel
        self.message_type = PCAN_MESSAGE_TYPES[message_type]

        # replace this with better error handling structure
        if self.pcan_channel != PCAN_ERROR_OK:
            print("Error initializing PCAN channel:", self.pcan_channel)
            exit(1)
        else:
            print("PCAN channel initialized")

    def send_frame(self, arbitration_id, data):
        # Define the CAN message with the specified arbitration ID and data
        frame = TPCANMsg()
        frame.ID = arbitration_id
        frame.MSGTYPE = self.message_type  # Standard frame
        frame.LEN = len(data)  # Length of the data (no of non-zero bytes)
        frame.DATA = data  # Data (padded with zeros)

        # Transmit the CAN message
        result = self.pcan.Write(self.channel, frame)
        if result != PCAN_ERROR_OK:
            print("Error transmitting CAN message:", result)
        else:
            print("Message transmitted from PCAN")
    
    def receive_frame(self):
        result, msg, timestamp = self.pcan.Read(self.channel)
        return tuple(msg.DATA)
    
class Vector(HardwareInterface):
    def __init__(self, channel, baud, message_type):
        # Initialize Vector 
        pass

    def send_frame(self, arbitration_id, data):
        # Implement Vector frame sending
        pass

    def receive_frame(self):
        # Implement Vector frame receiving
        pass

def get_hardware_interface(choice, *args):
    if choice.lower() == "pcan":
        return PCAN(*args)
    else:
        return Vector(*args)