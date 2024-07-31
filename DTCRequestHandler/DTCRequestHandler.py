import math
import time
from . import Frame
from . import PCANBasic
from .UDSException import UDSException


class PCAN:
    def __init__(self) -> None:
        self.pcan = PCANBasic.PCANBasic()  # Initialize the PCANBasic instance
        self.channel = PCANBasic.PCAN_USBBUS1  # Define the PCAN channel you are using (e.g., PCAN_USBBUS1 for the first USB channel)
        self.baudrate = PCANBasic.PCAN_BAUD_500K  # Define the baud rate (e.g., PCAN_BAUD_500K for 500 kbps)
        self.pcan_channel = self.pcan.Initialize(self.channel, self.baudrate)  # Initialize the PCAN channel

        # replace this with better error handling structure
        if self.pcan_channel != PCANBasic.PCAN_ERROR_OK:
            print("Error initializing PCAN channel:", self.pcan_channel)
            exit(1)

    def send_frame(self, arbitration_id, data):
        # Define the CAN message with the specified arbitration ID and data
        frame = PCANBasic.TPCANMsg()
        frame.ID = arbitration_id
        frame.MSGTYPE = PCANBasic.PCAN_MESSAGE_STANDARD  # Standard frame
        frame.LEN = len(data)  # Length of the data (no of non-zero bytes)
        frame.DATA = data  # Data (padded with zeros)

        # Transmit the CAN message
        result = self.pcan.Write(self.channel, frame)
        if result != PCANBasic.PCAN_ERROR_OK:
            print("Error transmitting CAN message:", result)
    
    def receive_frame(self) -> None:
        # write logic to get the next frame on the Receive Queue
        result, msg, timestamp = self.pcan.Read(self.channel)
        # print(msg)
        return tuple(msg.DATA)

    def increment(self, current, step):
        start = 0x20
        end = 0x2F
        current += step
        if current > end:
            current = start + (current - end - 1)
        return current
        

    
    def equals(self, msg1, msg2):
        return msg1 == msg2
    
    def hex(self, msg):
        return tuple([hex(m) for m in msg])
    
    def seconds(self, ms):
        return ms / 1000.0

class Inactive:
    def __init__(self, pcan, frame) -> None:
        self.pcan = pcan
        self.frame = frame

    def send_start_session_frame(self) -> None:
        self.pcan.send_frame(Frame.ARBITRATION_ID, Frame.SESSION_START_REQ)

    def extract_time(self, msg):
        p2 = msg[3]
        p2_star = msg[4:7]
        p2_star = (p2_star[0] << 16) | (p2_star[1] << 8) | p2_star[2]
        return p2, p2_star

class Idle:
    def __init__(self, pcan, frame) -> None:
        self.pcan = pcan
        self.frame = frame

    def send_DTC_request(self) -> None:
        self.pcan.send_frame(Frame.ARBITRATION_ID, Frame.DTC_REQUEST)

class ResponseManager:
    def __init__(self, pcan, frame) -> None:
        self.pcan = pcan
        self.frame = frame

    def send_control_frame(self, block_size, time_between_consecutive_frame) -> None:
        self.pcan.send_frame(Frame.ARBITRATION_ID, self.frame.construct_flow_control(block_size, time_between_consecutive_frame))

    def send_tester_frame(self) -> None:
        # write logic to send a control frame
        pass

    def extract_data_length(self, msg) -> None:
        return msg[1], list(msg[5:])

class DTCRequestHandler:
    INACTIVE: int = 1
    IDLE: int = 2
    RECEIVE: int = 3

    def __init__(self) -> None:
        self.state = DTCRequestHandler.INACTIVE
        self.pcan = PCAN()  # Initialize PCAN instance
        self.frame = Frame.Frame() # Initialize Frame Instance
        self.inactive = Inactive(self.pcan, self.frame)
        self.idle = Idle(self.pcan, self.frame)
        self.response_manager = ResponseManager(self.pcan, self.frame)

        self.block_count = 0x03 # ms
        self.time_between_consecutive_frame = 0x14 # ms
        self.current_pos = 0x20

        self.p2: float = 0.0 # in miliseconds
        self.p2_star: float = 0.0 # in miliseconds

    def set_state(self, new_state) -> None:
        self.state = new_state

    def start_session(self):
        self.inactive.send_start_session_frame()
        self.set_state(DTCRequestHandler.RECEIVE)

        # Wait till we get positive response
        while True:
            time.sleep(0.1)
            received_frame = self.pcan.receive_frame()
            try:
                self.frame.validate_session_response(received_frame)
            except UDSException as udse:
                print(udse)
            else:
                break
        
        self.p2, self.p2_star = self.inactive.extract_time(received_frame)
        self.set_state(DTCRequestHandler.IDLE)
    
    def request_for_DTC(self): # sends the frame and combines the response and returns it
        self.idle.send_DTC_request() # sends the DTC req frame
        self.set_state(DTCRequestHandler.RECEIVE)

        # start_time = time.time()

        # waits till first frame is received
        while True: # time.time() - start_time < self.pcan.seconds(self.p2_star)
            time.sleep(0.1) # self.pcan.seconds(self.p2)
            received_frame = self.pcan.receive_frame()
            try:
                self.frame.validate_first_frame(received_frame)
            except UDSException as udse:
                print(udse)
            else:
                break
        
        data_length, data = self.response_manager.extract_data_length(received_frame)
        for i in range(math.ceil(data_length / (self.block_count * 7))):
            self.response_manager.send_control_frame(self.block_count, self.time_between_consecutive_frame)

            while True:
                time.sleep(self.pcan.seconds(int("14", 16)))
                received_frame = self.pcan.receive_frame()
                print(received_frame)
                data.extend(received_frame[1:])
                if received_frame[0] == self.pcan.increment(self.current_pos, self.block_count):
                    break
            
            self.current_pos = self.pcan.increment(self.current_pos, self.block_count)
            print(hex(self.current_pos))
        print(self.pcan.hex(data))

