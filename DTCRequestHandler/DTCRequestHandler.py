import time
import PCANBasic

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
        else:
            print("CAN message transmitted successfully")
    
    def equals(self, msg1, msg2):
        return msg1 == msg2

class Inactive:
    def __init__(self, pcan) -> None:
        self.pcan = pcan

    def start_session(self) -> None:
        self.pcan.send_frame(0x743, (0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00))
        print("Activating session")

class Idle:
    def __init__(self, pcan) -> None:
        self.pcan = pcan

    def send_DTC_request(self) -> None:
        # write logic to send DTC Req (0x19) and change state to Receive
        print("Sending DTC request")
        self.pcan.send_frame(0x743, (0x03, 0x19, 0x02, 0x09, 0x00, 0x00, 0x00, 0x00))

class Receive:
    def __init__(self, pcan) -> None:
        self.pcan = pcan

    def receive_frame(self) -> None:
        # write logic to get the next frame on the Receive Queue
        result, msg, timestamp = self.pcan.pcan.Read(self.pcan.channel)
        return tuple(msg.DATA)

    def send_control_frame(self) -> None:
        # write logic to send a control frame
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
        self.receive = Receive(self.pcan)

    def set_state(self, new_state) -> None:
        self.state = new_state
        print(f"Changed state to {new_state}")

    def start_session(self):
        msg = (0, 0, 0, 0, 0, 0, 0, 0)
        # msg = (16, 11, 89, 2, 9, 225, 79, 135)
        self.inactive.start_session()
        self.set_state(DTCRequestHandler.RECEIVE)
        time.sleep(2)
        result = self.receive.receive_frame()
        print(result)
        print(self.pcan.equals(result, msg))
            
    
    def request_for_DTC(self): # sends the frame and combines the response and returns it
        self.idle.send_DTC_request() # sends the DTC req frame
        self.set_state(DTCRequestHandler.RECEIVE)

    def handle_request(self) -> None:
        # Example of handling request based on the current state
        if self.state == DTCRequestHandler.INACTIVE:
            self.start_session()
        elif self.state == DTCRequestHandler.IDLE:
            self.idle.send_DTC_request()
            self.set_state(DTCRequestHandler.RECEIVE)
        elif self.state == DTCRequestHandler.RECEIVE:
            self.receive.receive_frame()
            # Additional handling logic for Receive state

# Example usage
handler = DTCRequestHandler()
handler.start_session()  # Activates session and changes state to IDLE
# handler.request_for_DTC()  # Sends DTC request and changes state to RECEIVE
