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
    current_instance = None  # Class-level reference to the current instance

    def __init__(self, channel, baud, message_type):
        # Check if an instance already exists and update it if necessary
        if PCAN.current_instance:
            # If the parameters are different, update the existing instance
            if (PCAN.current_instance._channel != PCAN_CHANNELS[channel] or
                PCAN.current_instance._baudrate != PCAN_BAUD_RATES[baud] or
                PCAN.current_instance._message_type != PCAN_MESSAGE_TYPES[message_type]):
                
                print("Updating existing PCAN instance")
                PCAN.current_instance.update_config(channel, baud, message_type)
            else:
                print("Existing PCAN instance already has these parameters")
                return  # Skip initialization if parameters are the same
        else:
            # Initialize a new instance
            print(channel, baud, message_type)
            self.pcan = PCANBasic()  # Initialize the PCANBasic instance
            self._channel = PCAN_CHANNELS[channel]  # Define the PCAN channel
            self._baudrate = PCAN_BAUD_RATES[baud]  # Define the baud rate
            self.pcan_channel = self.pcan.Initialize(self._channel, self._baudrate)  # Initialize the PCAN channel
            print(self.pcan_channel, "sknfkdnfkhweifokmenfksndjfks")
            self._message_type = PCAN_MESSAGE_TYPES[message_type]

            # Check for initialization errors
            if self.pcan_channel != PCAN_ERROR_OK:
                print("Error initializing PCAN channel:", self.pcan_channel)
                exit(1)
            else:
                print("PCAN channel initialized")

            # Set the current instance to this instance
            PCAN.current_instance = self

    def update_config(self, channel, baud, message_type):
        # Update the current instance configuration
        self._channel = PCAN_CHANNELS[channel]
        self._baudrate = PCAN_BAUD_RATES[baud]
        self._message_type = PCAN_MESSAGE_TYPES[message_type]
        self.pcan_channel = self.pcan.Initialize(self._channel, self._baudrate)
        if self.pcan_channel != PCAN_ERROR_OK:
            print("Error re-initializing PCAN channel:", self.pcan_channel)
        else:
            print("PCAN channel re-initialized with new configuration")

    def send_frame(self, arbitration_id, data):
        # Define the CAN message with the specified arbitration ID and data
        frame = TPCANMsg()
        frame.ID = arbitration_id
        frame.MSGTYPE = self._message_type  # Standard frame
        frame.LEN = len(data)  # Length of the data (no of non-zero bytes)
        frame.DATA = data  # Data (padded with zeros)

        # Transmit the CAN message
        result = self.pcan.Write(self._channel, frame)
        if result != PCAN_ERROR_OK:
            print("Error transmitting CAN message:", result)
        else:
            print("Message transmitted from PCAN")
    
    def receive_frame(self):
        result, msg, timestamp = self.pcan.Read(self._channel)
        return tuple(msg.DATA), msg.ID
    
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