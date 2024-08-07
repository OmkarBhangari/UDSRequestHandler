import queue
from . import Colors
from .TP import TP 
from rich.table import Table
from rich.console import Console

class Ox19:
    DTC_REQUEST = (0x03, 0x19, 0x02, 0x09, 0x00, 0x00, 0x00, 0x00)

    def __init__(self, uds):
        self.uds = uds
        self.buffer = queue.Queue()

    async def send_dtc_request(self):
        self.uds.queue_frame(Ox19.DTC_REQUEST)

    def buffer_frame(self, frame):
        self.buffer.put(frame)

    def main(self):
        if not self.buffer.empty():
            data = self.buffer.get()
            DTC_data = TP.extract_data(data)
            DTC_data = DTC_data[2:]
            print(f"{Colors.green}{DTC_data}{Colors.reset}")
            self.decoder(DTC_data)

    def decoder(self, data) -> None:
        self.table = Table(title="Hex Values and Status Mask")
        self.table.add_column("Hex Values", justify="left")
        self.table.add_column("Status Mask", justify="left")
        self.console = Console()

        for i in range(0, len(data), 4):
            if i + 3 < len(data):
                combined_hex_value = (data[i] << 16) | (data[i + 1] << 8) | data[i + 2]
                status_mask = data[i + 3]
                
                hex_value_str = f"{combined_hex_value:06X}"
                status_mask_str = f"{status_mask:02X}"
                self.decode_table(hex_value_str, status_mask_str)

        self.console.print(self.table)

    def hex_to_bin(self, hex_value):
        # Ensure hex_value is an integer
        if isinstance(hex_value, str):
            hex_value = int(hex_value, 16)
        # Convert integer to binary string and remove '0b' prefix
        binary_string = bin(hex_value)[2:].zfill(8)
        return binary_string    

    def decode_table(self, hex_value_str, status_mask_str) -> None:
        system_specific_dtc = int(hex_value_str, 16) & 0xF00000
        system_specific_value = self.hex_to_bin(system_specific_dtc)[:2]
        
        my_dict = {
            '00': 'Power Train',
            '01': 'Chassis',
            '10': 'Body',
            '11': 'Network'
        }
        
        system_type = my_dict.get(system_specific_value, "Unknown")
        
        status_mask_dict = {
            '00': 'Test Not Complete Since Last Clear',
            '01': 'Test Failed Since Last Clear',
            '02': 'Test Not Complete This Monitoring Cycle',
            '03': 'Pending DTC',
            '04': 'Confirmed DTC',
            '05': 'Test Failed This Monitoring Cycle',
            '06': 'Warning Indicator Requested',
            '07': 'Test Not Completed Due to Condition',
            '08': 'Test Failed Due to Condition',
            '09': 'Warning Indicator Off',
            '0A': 'Previously Active',
            '0B': 'Test Completed This Monitoring Cycle',
            '0C': 'Test Not Supported',
            '0D': 'Test Not Enabled',
            '0E': 'Test Currently Active',
            '0F': 'Test Complete',
        }
        
        status = status_mask_dict.get(status_mask_str, "Unknown")
        
        self.table.add_row(f"{hex_value_str} ({system_type})", f"{status_mask_str} ({status})")