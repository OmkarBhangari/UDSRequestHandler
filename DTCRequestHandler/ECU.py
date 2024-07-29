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

ARBITRATION_ID = 0x763
SESSION_START_REQ = (0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00)
SESSION_START_REQ_NEG_RESPONSE = (0x7F, 0x10, 0x78, 0x00, 0x00, 0x00, 0x00, 0x00)
SESSION_START_REQ_POS_RESPONSE = (0x06, 0x50, 0x03, 0x32, 0x00, 0x13, 0x88, 0x00)
DTC_REQUEST = (0x03, 0x19, 0x02, 0x09, 0x00, 0x00, 0x00, 0x00)
DTC_REQUEST_NEG_RESPONSE = (0x7F, 0x19, 0x78, 0x09, 0x00, 0x00, 0x00, 0x00)
FIRST_FRAME = (0x10, 0x29, 0x59, 0x02, 0x09, 0x00, 0x00, 0x00)
FLOW_CONTROL = (0x30, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00)
CF_1 = (0x21, 0x09, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00)
CF_2 = (0x22, 0x09, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00)
CF_3 = (0x23, 0x09, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00)
CF_4 = (0x24, 0x09, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00)

pcan = PCAN()

while True:
    received_frame = pcan.receive_frame()
    
    if received_frame == SESSION_START_REQ:
        print("SESSION_START_REQ")
        pcan.send_frame(ARBITRATION_ID, SESSION_START_REQ_NEG_RESPONSE)
        pcan.send_frame(ARBITRATION_ID, SESSION_START_REQ_POS_RESPONSE)

    elif received_frame == DTC_REQUEST:
        print("DTC_REQUEST")
        pcan.send_frame(ARBITRATION_ID, DTC_REQUEST)
        pcan.send_frame(ARBITRATION_ID, FIRST_FRAME)

    elif received_frame == FLOW_CONTROL:
        print("FLOW_CONTROL")
        pcan.send_frame(ARBITRATION_ID, CF_1)
        pcan.send_frame(ARBITRATION_ID, CF_2)
        pcan.send_frame(ARBITRATION_ID, CF_3)
        pcan.send_frame(ARBITRATION_ID, CF_4)
    
    time.sleep(0.1)