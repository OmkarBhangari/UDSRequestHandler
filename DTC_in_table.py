from DTCRequestHandler import DTCRequestHandler
from rich.console import Console
from rich.table import Table

# self.pcan = PCANBasic.PCANBasic()  # Initialize the PCANBasic instance
# self.channel = PCANBasic.PCAN_USBBUS1  # Define the PCAN channel you are using (e.g., PCAN_USBBUS1 for the first USB channel)
# self.baudrate = PCANBasic.PCAN_BAUD_500K  # Define the baud rate (e.g., PCAN_BAUD_500K for 500 kbps)
# self.pcan_channel = self.pcan.Initialize(self.channel, self.baudrate)

arbitration_id = 0x743

handler = DTCRequestHandler("PCAN_USBBUS1", "PCAN_BAUD_500K", "PCAN_MESSAGE_STANDARD", arbitration_id)
handler.start_session()  # Activates session and changes state to IDLE
DTC_codes = handler.request_for_DTC()  # Sends DTC request and changes state to RECEIVE
print(DTC_codes)
console = Console()
formatted_output=[]
result=[]
table = Table(show_header=True, header_style="bold magenta")
table.add_column("Hex Values", style="cyan")
table.add_column("Status Mask", style="yellow")

for i in range(0, len(DTC_codes), 4):
    # Get the first three values in hex format
    hex_values = [hex(DTC_codes[j]) for j in range(i, min(i + 3, len(DTC_codes)))]
    
    # Join the first three values with a space
    hex_part = ' '.join(hex_values)
    
    # Check if there is a fourth value
    if i + 3 < len(DTC_codes):
        status_mask = hex(DTC_codes[i + 3])
        table.add_row(hex_part, status_mask)
        
    else:
        table.add_row(hex_part, "")  # Add empty status mask if no fourth value

# Print the table with rich
console.print(table)