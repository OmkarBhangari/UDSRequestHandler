import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app import App
from ecupath import Colors

class MenuBar:
    def __init__(self, parent):
        self.menu_bar = ttk.Menu(parent)

        # File Menu
        self.file_menu = ttk.Menu(self.menu_bar, tearoff=False)
        self.file_menu.add_command(label="New")
        self.file_menu.add_command(label="Open")
        self.file_menu.add_command(label="Save")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=parent.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Edit Menu
        self.edit_menu = ttk.Menu(self.menu_bar, tearoff=False)
        self.edit_menu.add_command(label="Undo")
        self.edit_menu.add_command(label="Redo")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut")
        self.edit_menu.add_command(label="Copy")
        self.edit_menu.add_command(label="Paste")
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        # Selection Menu
        self.selection_menu = ttk.Menu(self.menu_bar, tearoff=False)
        self.selection_menu.add_command(label="Select All")
        self.selection_menu.add_command(label="Deselect All")
        self.menu_bar.add_cascade(label="Selection", menu=self.selection_menu)

        # View Menu
        self.view_menu = ttk.Menu(self.menu_bar, tearoff=False)
        self.view_menu.add_command(label="Zoom In")
        self.view_menu.add_command(label="Zoom Out")
        self.view_menu.add_command(label="Reset Zoom")
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)

        # Attach the menu_bar to the parent window
        parent.config(menu=self.menu_bar)
    
        # Create another frame below the menu bar
        self.settings_frame = ttk.Frame(parent)
        self.settings_frame.pack(fill='x')

        # Channel Selection
        ttk.Label(self.settings_frame, text="Channel:").pack(side="left", padx=5)
        self.channel_var = ttk.StringVar()
        self.channel_menu = ttk.OptionMenu(
            self.settings_frame, self.channel_var, "Select Channel", 
            "PCAN_USBBUS1", "PCAN_USBBUS2", "PCAN_USBBUS3", 
            "PCAN_USBBUS4", "PCAN_USBBUS5", "PCAN_USBBUS6"
        )
        self.channel_menu.pack(side="left", padx=5)

        # Baud Rate Selection
        ttk.Label(self.settings_frame, text="Baud Rate:").pack(side="left", padx=5)
        self.baud_var = ttk.StringVar()
        self.baud_menu = ttk.OptionMenu(
            self.settings_frame, self.baud_var, "Select Baud Rate", 
            "PCAN_BAUD_1M", "PCAN_BAUD_800K", "PCAN_BAUD_500K", 
            "PCAN_BAUD_250K", "PCAN_BAUD_125K", "PCAN_BAUD_100K",
            "PCAN_BAUD_95K", "PCAN_BAUD_83K", "PCAN_BAUD_50K", 
            "PCAN_BAUD_47K", "PCAN_BAUD_33K", "PCAN_BAUD_20K",
            "PCAN_BAUD_10K", "PCAN_BAUD_5K"
        )
        self.baud_menu.pack(side="left", padx=5)

        # Message Type Selection
        ttk.Label(self.settings_frame, text="Message Type:").pack(side="left", padx=5)
        self.msg_type_var = ttk.StringVar()
        self.msg_type_menu = ttk.OptionMenu(
            self.settings_frame, self.msg_type_var, "Select Message Type", 
            "PCAN_MESSAGE_STANDARD", "PCAN_MESSAGE_RTR", "PCAN_MESSAGE_EXTENDED",
            "PCAN_MESSAGE_FD", "PCAN_MESSAGE_BRS", "PCAN_MESSAGE_ESI",
            "PCAN_MESSAGE_ECHO", "PCAN_MESSAGE_ERRFRAME", "PCAN_MESSAGE_STATUS"
        )
        self.msg_type_menu.pack(side="left", padx=5)

class Ox19InputContent:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
       
        # Dropdown for sub function

        ttk.Label(self.frame, text="Sub Function:").pack(fill="x", padx="8")
        self.sub_function = ttk.Combobox(self.frame, values=["0x01", "0x02", "0x11", "0x0A","0x13","0x12"])
        self.sub_function.pack(fill="x", padx="8")
        self.sub_function.bind("<<ComboboxSelected>>", self.toggle_status_masks)
       
        # Frame for status masks
        self.status_mask_frame = ttk.Frame(self.frame)
        self.status_mask_frame.pack(fill="x")

        # 8 checkboxes for status mask
        self.status_masks = []
        for i in range(8):
            var = ttk.BooleanVar()
            cb = ttk.Checkbutton(self.status_mask_frame, text=f"Status Mask {i+1}", variable=var)
            cb.pack(anchor="w", padx="8", pady="4")
            self.status_masks.append(var)

    def toggle_status_masks(self, event):
        if self.sub_function.get() == "0x0A":
            self.status_mask_frame.pack_forget()
        else:
            self.status_mask_frame.pack(fill="x")

class Ox22InputContent:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
       
        # Inputbox for DID
        ttk.Label(self.frame, text="DID:").pack(fill="x", padx="8")
        self.did_entry = ttk.Entry(self.frame)
        self.did_entry.pack(fill="x", padx="8")

class Ox2EInputContent:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
       
        # Inputbox for DID
        ttk.Label(self.frame, text="DID:").pack(fill="x", padx="8")
        self.did_entry = ttk.Entry(self.frame)
        self.did_entry.pack(fill="x", padx="8")
       
        # Inputbox for Data
        ttk.Label(self.frame, text="Data:").pack(fill="x", padx="8")
        self.data_entry = ttk.Entry(self.frame)
        self.data_entry.pack(fill="x", padx="8")

class RequestDetailsWindow:
    def __init__(self, parent, uds, request_details, data):
        self.window = ttk.Toplevel(parent)
        self.window.title("Request Details")
        self.window.geometry("400x300")
        self.uds = uds

        for key, value in request_details.items():
            ttk.Label(self.window, text=f"{key}: {value}").pack(pady=5)
        print("getting response from UDS")
        if data:
            ttk.Label(self.window, text=f"{data}").pack(pady=5)

class NewReqInputBox:
    SID_options = ["0x19", "0x22", "0x2E"]

    def __init__(self, uds, parent, add_request_button_callback):
        self.frame = ttk.LabelFrame(parent, text="New Request")
        self.frame.pack(fill="x", padx="12", pady="12")
        self.add_request_button_callback = add_request_button_callback
        self.uds = uds

        # SID dropdown
        ttk.Label(self.frame, text="SID:").pack(fill="x", padx="8")
        self.sid = ttk.Combobox(self.frame, values=self.SID_options)
        self.sid.pack(expand=True, fill="x", padx="8")
        self.sid.bind("<<ComboboxSelected>>", self.update_input_content)

        # Frame to hold the input content
        self.content_frame = ttk.Frame(self.frame)
        self.content_frame.pack(fill="x")

        self.send_req_btn = ttk.Button(self.frame, text="Create Request", command=self.create_request)
        self.send_req_btn.pack(fill="x", padx="8", pady="8")

        # Initialize with default input content
        self.current_content = None
        self.update_input_content()

    def update_input_content(self, event=None):
        if self.current_content:
            self.current_content.frame.pack_forget()

        selected_sid = self.sid.get()
        if selected_sid == "0x19":
            self.current_content = Ox19InputContent(self.content_frame)
        elif selected_sid == "0x22":
            self.current_content = Ox22InputContent(self.content_frame)
        elif selected_sid == "0x2E":
            self.current_content = Ox2EInputContent(self.content_frame)
        else:
            self.current_content = None

        if self.current_content:
            self.current_content.frame.pack(fill="x")

    def create_request(self):
        # Gather request details
        request_details = {"SID": self.sid.get()}
        if isinstance(self.current_content, Ox19InputContent):
            request_details["Sub Function"] = self.current_content.sub_function.get()
            if request_details["Sub Function"] != "0x0A":
                request_details["Status Masks"] = [mask.get() for mask in self.current_content.status_masks]
        elif isinstance(self.current_content, Ox22InputContent):
            request_details["DID"] = self.current_content.did_entry.get()
        elif isinstance(self.current_content, Ox2EInputContent):
            request_details["DID"] = self.current_content.did_entry.get()
            request_details["Data"] = self.current_content.data_entry.get()

        self.converted_data = self.convert_request_details(request_details)
        print(self.converted_data)  # debug line
        self.uds.send_request(self.converted_data)
        self.add_request_button_callback(request_details)

    def convert_request_details(self, request_details):
        tuple_dict = [value for key, value in request_details.items()]
        print("For testing, below is the original form:")
        print(f'{Colors.red}{tuple_dict}{Colors.reset}')

        sid = int(tuple_dict[0], 16)
    
        if sid == 0x19:
            sub_function = tuple_dict[1]
            if sub_function == "0x0A":
                result = (sid, int(sub_function, 16))
            else:
                sub_function = int(sub_function, 16)
                status_masks = tuple_dict[2]
                status_byte = sum(1 << i for i, mask in enumerate(status_masks) if mask)
                result = (sid, sub_function, status_byte)
        elif sid == 0x22:
            did_parts = tuple_dict[1].split()
            did = [int(part, 16) for part in did_parts]
            result = (sid, *did)
        elif sid == 0x2E:
            did_parts = tuple_dict[1].split()
            did = [int(part, 16) for part in did_parts]
            if isinstance(tuple_dict[2], str):
                data_parts = tuple_dict[2].split()
                data = [int(part, 16) for part in data_parts]
            else:
                data = tuple_dict[2]
            result = (sid, *did, *data)
        else:
            raise ValueError(f"Unsupported SID: {hex(sid)}")

        print("Converted tuple form:")
        print(f'{Colors.red}{result}{Colors.reset}')
        return result

class GUI:
    def __init__(self):
        self.active_session = False
        self.new_req_input_box = None

        self.window = ttk.Window()
        self.window.title("Visteon")
        self.window.geometry("600x600")

        self.menu_bar = MenuBar(self.window)

        self.button = ttk.Button(self.window, text="Start Session", command=self.toggle_session, bootstyle="primary")
        self.button.pack(fill="both", padx="12", pady="12")

        self.new_req_input_box_placeholder = ttk.Frame(self.window)
        self.new_req_input_box_placeholder.pack(fill="x")

        self.requests_frame = None
        self.data = []
        self.index = 0

        tx_id = 0x743   #0x6A0
        rx_id = 0x763   #0x514
        channel = "PCAN_USBBUS1"
        baud_rate = "PCAN_BAUD_500K"
        message_type = "PCAN_MESSAGE_STANDARD"

        # Initialize the app and UDS
        self.app = App(tx_id, rx_id, channel, baud_rate, message_type)
        self.uds = self.app.get_uds()

    def toggle_session(self):
        if self.active_session:
            self.button.config(text="Start Session", bootstyle="primary")
            self.app.stop_monitoring()
            if self.new_req_input_box:
                self.new_req_input_box.frame.destroy()
                self.new_req_input_box = None
            self.new_req_input_box_placeholder.config(height=1)
        else:
            self.button.config(text="Stop Session", bootstyle="danger")
            self.app.start_monitoring()
            self.new_req_input_box = NewReqInputBox(self.uds, self.new_req_input_box_placeholder, self.add_request_button)

        self.active_session = not self.active_session
        self.window.update_idletasks()

    def add_request_button(self, request_details):
        if self.requests_frame is None:
            self.requests_frame = ttk.Labelframe(self.window, text="Requests Stack")
            self.requests_frame.pack(fill="x", padx="12")
        button = ttk.Button(
            self.requests_frame,
            text=f"Request: {request_details['SID']}",
            command=lambda index=self.index: self.open_request_details(request_details, index),
            bootstyle="info"
        )

        self.index += 1
        button.pack(fill="x", padx=8, pady=6)

    def open_request_details(self, request_details, index):
        while True:
            response = self.uds.get_response()
            if response is None:
                break
            self.data.append(response)
        RequestDetailsWindow(self.window, self.uds, request_details, self.data[index])

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    gui = GUI()
    gui.run()