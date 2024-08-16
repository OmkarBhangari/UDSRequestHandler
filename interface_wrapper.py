from abc import ABC, abstractmethod

class CommunicationInterface(ABC):
    @abstractmethod
    def initialize(self, channel, baudrate, message_type):
        pass

    @abstractmethod
    def send_frame(self, arbitration_id, data):
        pass

    @abstractmethod
    def receive_frame(self):
        pass

class PCANWrapper(CommunicationInterface):
    def __init__(self):
        self.pcan = None

    def initialize(self, channel, baudrate, message_type):
        from .pcan import PCAN
        self.pcan = PCAN(channel, baudrate, message_type)

    def send_frame(self, arbitration_id, data):
        return self.pcan.send_frame(arbitration_id, data)

    def receive_frame(self):
        return self.pcan.receive_frame()

# This class can be implemented in the future when you want to use another hardware
class OtherInterface(CommunicationInterface):
    def initialize(self, channel, baudrate, message_type):
        # Implement LIN initialization
        pass

    def send_frame(self, arbitration_id, data):
        # Implement LIN frame sending
        pass

    def receive_frame(self):
        # Implement LIN frame receiving
        pass