import PCANBasic

class PCAN:
    def __init__(self) -> None:
        self.pcan = PCANBasic.PCANBasic() # Initialize the PCANBasic instance
        self.channel = PCANBasic.PCAN_USBBUS1 # Define the PCAN channel you are using (e.g., PCAN_USBBUS1 for the first USB channel)
        self.baudrate = PCANBasic.PCAN_BAUD_500K # Define the baud rate (e.g., PCAN_BAUD_500K for 500 kbps)
        self.pcan_channel = self.pcan.Initialize(self.channel, self.baudrate) # Initialize the PCAN channel

        # replace this with better error handling structure
        if self.pcan_channel != PCANBasic.PCAN_ERROR_OK:
            print("Error initializing PCAN channel:", self.pcan_channel)
            exit(1)

    def send_frame(self, arbitration_id, data):
        # Define the CAN message with the specified arbitration ID and data
        frame = PCANBasic.TPCANMsg()
        frame.ID = arbitration_id
        frame.MSGTYPE = PCANBasic.PCAN_MESSAGE_STANDARD  # Standard frame
        frame.LEN = len(data) - data.count(0x00)  # Length of the data (no of non-zero bytes)
        frame.DATA = data  # Data (padded with zeros)

        # Transmit the CAN message
        result = self.pcan.Write(self.channel, frame)
        if result != PCANBasic.PCAN_ERROR_OK:
            print("Error transmitting CAN message:", result)
        else:
            print("CAN message transmitted successfully")

class Inactive:
    def __init__(self) -> None:
        pass

    def activate_session() -> None:
        # write logic to start session
        pass

class Idle:
    def __init__(self) -> None:
        pass
    
    def send_DTC_request() -> None:
        # write logic to send DTC Req (0x19) and change state to Receive
        pass

class Receive:
    def __init__(self) -> None:
        pass

    def recieve_frame() -> None:
        # write logic to get the next frame on the Receive Queue
        pass

    def send_control_frame() -> None:
        # write logic to send a control frame
        pass

    def send_tester_frame() -> None:
        # write logic to send a control frame
        pass

class DTCRequestHandler:
    def __init__(self) -> None:
        pass

pcan = PCAN()

pcan.send_frame(0x743, (0x03, 0x19, 0x02, 0x09, 0x00, 0x00, 0x00, 0x00))