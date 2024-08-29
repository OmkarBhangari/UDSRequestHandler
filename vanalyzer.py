import webview
import os
from app import App
from ecupath import EventManager, Frame
import json
from datetime import datetime

class Api:
    START_SESSION = (0x10, 0x03)
    
    def __init__(self):
        tx_id = 0x743
        rx_id = 0x763
        channel = "PCAN_USBBUS1"
        baud_rate = "PCAN_BAUD_500K"
        message_type = "PCAN_MESSAGE_STANDARD"
        self.event_manager = EventManager()
        self.app = App(tx_id, rx_id, channel, baud_rate, message_type, self.event_manager)
        self.uds = self.app.get_uds()
        self.event_manager.subscribe('response_received', self.update_output_stack)
        self.event_manager.subscribe('terminal', self.update_terminal_output)

    def ask_directory(self):
        directory = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
        if directory and len(directory) > 0:
            return directory[0]
        return None

    def save_file(self, content):
        # Get the current date and time
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        
        # Construct the filename with the software name and timestamp
        filename = f"vanalyzer_{timestamp}.txt"
        
        # Ask for the directory
        directory = self.ask_directory()
        if directory:
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"File saved successfully at {file_path}"
            except Exception as e:
                return f"Error saving file: {e}"
        return "No directory selected"

    def exportLog(self, terminalStack, requestStack, outputStack):
        content = self.format_terminal_stack(terminalStack)
        content += self.format_request_and_output_stack(requestStack, outputStack)
        self.save_file(content)

    def format_terminal_stack(self, terminalStack):
        formatted_stack = "Frame Transmissions\n\n"
        for entry in terminalStack:
            action = 'tx' if entry[0] == 'transmitted' else 'rx'
            data = " ".join(entry[1])
            formatted_stack += f"{action}\t{data}\n"
        formatted_stack += '\n\n'
        return formatted_stack

    def format_request_and_output_stack(self, requestStack, outputStack):
        content = ""
        for request, output in zip(requestStack, outputStack):
            content += f"{request}\n{output}\n\n"

        return content

    def update_terminal_output(self, data):
        if Frame.negative_response(data[1]):
            data[0] = 'error'
        
        data[1] = Frame.hex(data[1])
        json_name = json.dumps(data)  # Properly escape the string
        window.evaluate_js(f"window.updateTerminalStack({json_name});")

    def start_session(self):
        print("Start Session Clicked")
        self.app.start_monitoring()
        self.uds.send_request(Api.START_SESSION)

    def update_output_stack(self, data):
        print(data)
        json_name = json.dumps(data)  # Properly escape the string
        window.evaluate_js(f"window.updateOutputStack({json_name});")

    def send_request(self, request_data):
        self.uds.send_request(self.process_request_data(request_data))

    def process_request_data(self, request_data):
        sid = int(request_data['sid'], 16)  # Convert SID to integer from hexadecimal
        request = [sid]  # Start with SID in the request

        if sid == 0x19:
            # Process Sub Functions
            sub_function = int(request_data['Sub Functions'], 16)
            request.append(sub_function)  # Add sub_function at the beginning

            try:
                # Process Status Mask
                status_mask_dict = request_data['Status Mask']
                status_mask_bits = ''.join(['1' if status_mask_dict[key] else '0' for key in reversed(status_mask_dict)])
                status_mask = int(status_mask_bits, 2)  # Convert binary string to integer
                request.append(status_mask)
            except Exception as e:
                print(e)
        
        elif sid == 0x2E:
            # Process High Byte, Low Byte, and Data
            high_byte = int(request_data['High Byte'])
            low_byte = int(request_data['Low Byte'])
            data = int(request_data['Data'])

            request.extend([high_byte, low_byte, data])

        elif sid == 0x22:
            # Process High Byte and Low Byte
            high_byte = int(request_data['High Byte'])
            low_byte = int(request_data['Low Byte'])

            request.extend([high_byte, low_byte])

        else:
            raise ValueError("Unsupported SID")

        return tuple(request)

if __name__ == '__main__':
    api = Api()
    app_path = os.path.abspath('vanalyzer/dist/index.html')
    window = webview.create_window('JS API example', url=app_path, js_api=api)
    webview.start(debug=True)
