from rich.table import Table
from rich.console import Console

from DTCRequestHandler import UDS

# self.pcan = PCANBasic.PCANBasic()  # Initialize the PCANBasic instance
# self.channel = PCANBasic.PCAN_USBBUS1  # Define the PCAN channel you are using (e.g., PCAN_USBBUS1 for the first USB channel)
# self.baudrate = PCANBasic.PCAN_BAUD_500K  # Define the baud rate (e.g., PCAN_BAUD_500K for 500 kbps)
# self.pcan_channel = self.pcan.Initialize(self.channel, self.baudrate)

arbitration_id = 0x743

handler = UDS("PCAN_USBBUS1", "PCAN_BAUD_500K", "PCAN_MESSAGE_STANDARD", arbitration_id)
handler.start_session()  # Activates session and changes state to IDLE
data = handler.request_for_DTC()  # Sends DTC request and changes state to RECEIVE

print(data)