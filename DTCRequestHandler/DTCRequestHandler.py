import math
import time
from . import Frame
from . import PCANBasic
from .UDSException import UDSException
from .PCANConstants import PCAN_CHANNELS, PCAN_BAUD_RATES, PCAN_MESSAGE_TYPES

class PCAN:
    def __init__(self, channel, baud, message_type, arbitration_id) -> None:
        self.pcan = PCANBasic.PCANBasic()  # Initialize the PCANBasic instance
        self.channel = PCAN_CHANNELS[channel]  # Define the PCAN channel you are using (e.g., PCAN_USBBUS1 for the first USB channel)
        self.baudrate = PCAN_BAUD_RATES[baud]  # Define the baud rate (e.g., PCAN_BAUD_500K for 500 kbps)
        self.pcan_channel = self.pcan.Initialize(self.channel, self.baudrate)  # Initialize the PCAN channel
        self.message_type = PCAN_MESSAGE_TYPES[message_type]
        self.arbitration_id = arbitration_id

        # replace this with better error handling structure
        if self.pcan_channel != PCANBasic.PCAN_ERROR_OK:
            print("Error initializing PCAN channel:", self.pcan_channel)
            exit(1)

    def send_frame(self, data):
        # Define the CAN message with the specified arbitration ID and data
        frame = PCANBasic.TPCANMsg()
        frame.ID = self.arbitration_id
        frame.MSGTYPE = self.message_type  # Standard frame
        frame.LEN = len(data)  # Length of the data (no of non-zero bytes)
        frame.DATA = data  # Data (padded with zeros)

        # Transmit the CAN message
        result = self.pcan.Write(self.channel, frame)
        if result != PCANBasic.PCAN_ERROR_OK:
            print("Error transmitting CAN message:", result)
    
    def receive_frame(self) -> None:
        result, msg, timestamp = self.pcan.Read(self.channel)
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

class DTCRequestHandler:
    INACTIVE: int = 1
    IDLE: int = 2
    RECEIVE: int = 3

    def __init__(self, channel, baud, message_type, arbitration_id) -> None:
        self.state = DTCRequestHandler.INACTIVE
        self.pcan = PCAN(channel, baud, message_type, arbitration_id)  # Initialize PCAN instance
        self.frame = Frame.Frame() # Initialize Frame Instance

        self.block_count = 0x03 # ms
        self.time_between_consecutive_frame = 0x14 # ms
        self.current_pos = 0x20

        self.p2: float = 0.0 # in miliseconds
        self.p2_star: float = 0.0 # in miliseconds

    def set_state(self, new_state) -> None:
        self.state = new_state

    def extract_time(self, msg):
        p2 = msg[3]
        p2_star = msg[4:7]
        p2_star = (p2_star[0] << 16) | (p2_star[1] << 8) | p2_star[2]
        return p2, p2_star
    
    def send_control_frame(self, block_size, time_between_consecutive_frame) -> None:
        self.pcan.send_frame(self.frame.construct_flow_control(block_size, time_between_consecutive_frame))

    def send_tester_frame(self) -> None:
        # write logic to send a control frame
        pass

    def extract_data_length(self,msg):
        length = (((msg[0] & 0x0F) << 8) | msg[1]) - 3 # to account for 3 bytes in FF
        data = list(msg[5:])
        return length, data


    def start_session(self):
        self.pcan.send_frame(Frame.SESSION_START_REQ)
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
        
        self.p2, self.p2_star = self.extract_time(received_frame)
        self.set_state(DTCRequestHandler.IDLE)
    
    def request_for_DTC(self): # sends the frame and combines the response and returns it
        self.pcan.send_frame(Frame.DTC_REQUEST) # sends the DTC req frame
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
        
        data_length, data = self.extract_data_length(received_frame)
        total_frames = math.ceil(data_length / 7)

        for i in range(total_frames, 0, -self.block_count):
            self.send_control_frame(i if i < self.block_count else self.block_count, self.time_between_consecutive_frame)

            while True:
                time.sleep(self.pcan.seconds(int("14", 16)))
                received_frame = self.pcan.receive_frame()
                data.extend(received_frame[1:])
                if received_frame[0] == self.pcan.increment(self.current_pos, self.block_count):
                    break
            
            self.current_pos = self.pcan.increment(self.current_pos, self.block_count)
        return data