from rich.table import Table
from rich.console import Console


# Initialize PCANBasic instance and channel
# self.pcan = PCANBasic.PCANBasic()
# self.channel = PCANBasic.PCAN_USBBUS1
# self.baudrate = PCANBasic.PCAN_BAUD_500K
# self.pcan_channel = self.pcan.Initialize(self.channel, self.baudrate)



class DECODE:
    def __init__(self, data) -> None:
        # Remove trailing 170 values
       

        # Initialize table and console
        self.table = Table(title="Hex Values and Status Mask")
        self.table.add_column("Hex Values", justify="left")
        self.table.add_column("Status Mask", justify="left")
        self.console = Console()

        # Process the data
        for i in range(0, len(data), 4):
            if i + 3 < len(data):
                combined_hex_value = (data[i] << 16) | (data[i + 1] << 8) | data[i + 2]
                status_mask = data[i + 3]
                
                hex_value_str = hex(combined_hex_value)[2:].upper().zfill(6)  # Convert to hex and format
                status_mask_str = hex(status_mask)[2:].zfill(2).upper()  # Convert to hex and format
                self.decode_table(hex_value_str, status_mask_str)

        # Print the table
        self.console.print(self.table)

    def hex_to_bin(self, hex_value):
        # Convert hex string to integer
        integer_value = int(hex_value, 16)
        # Convert integer to binary string and remove '0b' prefix
        binary_string = bin(integer_value)[2:]
        return binary_string    

    def decode_table(self, hex_value_str_1, status_mask_str_1) -> None:
        system_specific_dtc = int(hex_value_str_1, 16) & 0xF00000
        system_specific_value = self.hex_to_bin(system_specific_dtc)
        system_specific_value = system_specific_value.zfill(2)
        
        my_dict = {
            '00': 'Power Train',
            '01': 'Chassis',
            '10': 'Body',
            '11': 'Network'
        }
        
        if system_specific_value in my_dict:
            print(f"{system_specific_value}: {my_dict[system_specific_value]}")
        else:
            print(f"{system_specific_value} is not present in the dictionary")
        
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
        
        if status_mask_str_1 in status_mask_dict:
            print(f"{status_mask_str_1}: {status_mask_dict[status_mask_str_1]}")
        else:
            print(f"{status_mask_str_1} is not present in the dictionary")

# Example usage
data=[0xE1, 0x4F, 0x87, 0x09, 0xE1, 0x5B, 0x87, 0x09, 0xFF, 0x59, 0x02, 0x09]
decode = DECODE(data)
