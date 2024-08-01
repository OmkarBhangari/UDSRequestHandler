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

# Remove trailing 170 values
while data and data[-1] == 170:
    data.pop()

# Initialize table and console
table = Table(title="Hex Values and Status Mask")
table.add_column("Hex Values", justify="left")
table.add_column("Status Mask", justify="left")
console = Console()

# Process the data
for i in range(0, len(data), 4):
    if i + 3 < len(data):
        combined_hex_value = (data[i] << 16) | (data[i+1] << 8) | data[i+2]
        status_mask = data[i+3]
        
        hex_value_str = hex(combined_hex_value)
        status_mask_str = hex(status_mask)
        
        table.add_row(hex_value_str, status_mask_str)

# Print the table
console.print(table)
