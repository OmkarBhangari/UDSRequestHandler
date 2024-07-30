import time
import PCANBasic
import Frame


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
    
    def equals(self, msg1, msg2):
        return msg1 == msg2
    
    def hex(self, msg):
        return tuple([hex(m) for m in msg])
    
    def seconds(self, ms):
        return ms / 1000.0

class Inactive:
    def __init__(self, pcan) -> None:
        self.pcan = pcan

    def send_start_session_frame(self) -> None:
        self.pcan.send_frame(0x743, (0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00))
        print("Activating session")

    def extract_time(self, msg):
        p2 = msg[3]
        p2_star = msg[4:7]
        p2_star = (p2_star[0] << 16) | (p2_star[1] << 8) | p2_star[2]
        return p2, p2_star

class Idle:
    def __init__(self, pcan) -> None:
        self.pcan = pcan

    def send_DTC_request(self) -> None:
        # write logic to send DTC Req (0x19) and change state to Receive
        self.pcan.send_frame(0x743, (0x03, 0x19, 0x02, 0x09, 0x00, 0x00, 0x00, 0x00))

class ResponseManager:
    def __init__(self, pcan) -> None:
        self.pcan = pcan

    def send_control_frame(self) -> None:
        # write logic to send a control frame
        self.pcan.send_frame(0x743, (0x30, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00))
        pass

    def send_tester_frame(self) -> None:
        # write logic to send a control frame
        pass

class DTCRequestHandler:
    INACTIVE: int = 1
    IDLE: int = 2
    RECEIVE: int = 3

    def __init__(self) -> None:
        self.state = DTCRequestHandler.INACTIVE
        self.pcan = PCAN()  # Initialize PCAN instance
        self.inactive = Inactive(self.pcan)
        self.idle = Idle(self.pcan)
        self.response_manager = ResponseManager(self.pcan)

        self.p2: float = 0.0 # in miliseconds
        self.p2_star: float = 0.0 # in miliseconds

    def set_state(self, new_state) -> None:
        self.state = new_state

    def start_session(self):
        # request correctly recieved positive response pending
        RCRPRP = (0x03, 0x7F, 0x10, 0x78, 0x00, 0x00, 0x00, 0x00)
        negative = (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)

        self.inactive.send_start_session_frame()
        self.set_state(DTCRequestHandler.RECEIVE)

        while True:
            time.sleep(0.1)
            received_frame = self.pcan.receive_frame()
            # if I didn't receive RCRPRP frame then I must have gotten correct frame. although 
            # this won't work if there are multiple frames that I can receive
            print("Response to Start Session", self.pcan.hex(received_frame))

            if self.pcan.equals(received_frame, Frame.SESSION_START_REQ_POS_RESPONSE):
                break
            
        self.p2, self.p2_star = self.inactive.extract_time(received_frame)
        self.set_state(DTCRequestHandler.IDLE)
    
    def request_for_DTC(self): # sends the frame and combines the response and returns it
        # request correctly recieved positive response pending
        RCRPRP = (0x03, 0x7F, 0x19, 0x78, 0x00, 0x00, 0x00, 0x00)
        negative = (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)

        self.idle.send_DTC_request() # sends the DTC req frame
        self.set_state(DTCRequestHandler.RECEIVE)

        start_time = time.time()
        while True: # time.time() - start_time < self.pcan.seconds(self.p2_star)
            time.sleep(0.1) # self.pcan.seconds(self.p2)
            received_frame = self.pcan.receive_frame()
            # if I didn't receive RCRPRP frame then I must have gotten correct frame. although 
            # this won't work if there are multiple frames that I can receive
            print("Response to DTC Req", self.pcan.hex(received_frame))

            if self.pcan.equals(received_frame, Frame.FIRST_FRAME):
                break
        print("SENDING FLOW CONTROL")
        self.response_manager.send_control_frame()
        while True:
            time.sleep(self.pcan.seconds(int("14", 16)))
            received_frame = self.pcan.receive_frame()
            # if I didn't receive RCRPRP frame then I must have gotten correct frame. although 
            # this won't work if there are multiple frames that I can receive
            print(self.pcan.hex(received_frame))

            if received_frame[0] == int(0x24):
                break

        

    def handle_request(self) -> None:
        # Example of handling request based on the current state
        if self.state == DTCRequestHandler.INACTIVE:
            self.start_session()
        elif self.state == DTCRequestHandler.IDLE:
            self.idle.send_DTC_request()
            self.set_state(DTCRequestHandler.RECEIVE)
        elif self.state == DTCRequestHandler.RECEIVE:
            self.pcan.receive_frame()
            # Additional handling logic for Receive state

# Example usage
handler = DTCRequestHandler()
handler.start_session()  # Activates session and changes state to IDLE
handler.request_for_DTC()  # Sends DTC request and changes state to RECEIVE
