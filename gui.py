import tkinter as tk
import ttkbootstrap as ttk
from uds import pcan_constants
import asyncio
import threading
from app import UdsWrapper

class DTC_gui:

    def __init__(self) -> None:
        self.window = ttk.Window()
        self.window.title('Properties')
        self.window.geometry('1000x800')
        self.window.resizable(False, False)
        self.uds_wrap = UdsWrapper(0x743,0x763)

        self.style = ttk.Style()

        # Define a custom style for buttons
        self.style.configure('White.TButton',
                            background=self.style.colors.secondary,  # Set background color
                            foreground='black',  # Set text color to black
                            relief='flat')

        self.style.configure('Bold.TButton',
                            font=('Helvetica', 12, 'bold'),
                            background='lightblue', 
                            foreground='black',  # Set text color to black
                            relief='flat')      

        self.style.map('White.TButton',
                       background=[('active', 'grey')],
                       foreground=[('active', 'black')])
        
        self.style.map('Bold.TButton',
                       background=[('active', 'cyan')],  # Background color on hover
                       foreground=[('active', 'black')])  # Text color on hover

        # TOOLBAR
        # creating toolbar frame
        self.toolbar = ttk.Frame(self.window, width=1000, height=40, bootstyle="secondary")
        self.toolbar.grid(row=0, column=0, sticky="ew")

        # creating the toolbar buttons
        self.toolbar_dropdown = [
            ("File", ["Configure"]),
            ("Help", ["Help", "About"])
        ]

        for idx, (text, options) in enumerate(self.toolbar_dropdown):
            # Create button
            button = ttk.Button(self.toolbar, text=text, style='White.TButton')
            button.grid(row=0, column=idx, padx=5, pady=4, sticky="w")

            # Create menu
            menu = tk.Menu(self.toolbar, tearoff=0)
            for option in options:
                menu.add_command(label=option, command=lambda opt=option: self.on_option_select(opt)) 
            
            # Bind button to menu
            button.config(command=lambda m=menu, b=button: self.show_menu(m, b)) 

        # creating tabs for Configure and Main
        self.main_notebook = ttk.Notebook(self.window, bootstyle="dark")
        self.message_tab = ttk.Frame(self.main_notebook)
        self.trace_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.message_tab, text="Message")
        self.main_notebook.add(self.trace_tab, text="Trace")
        self.main_notebook.grid(row=1, column=0, sticky="nsew")

        # Adding widgets to the Trace Tab
        self.display_trace = tk.Text(self.trace_tab, state='normal')
        self.display_trace.grid(row=0, column=0, sticky="nsew")

        # Adding widgets to the Message Tab
        self.message_button = ttk.Button(self.message_tab, text="Start Session", width=90, command=self.run_async_function(self.start_session), style='Bold.TButton')
        self.message_button.grid(row=0, column=0, pady=7, sticky="w")

        # Update grid weights to ensure the notebook resizes properly
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.trace_tab.grid_rowconfigure(0, weight=1)
        self.trace_tab.grid_columnconfigure(0, weight=1)

        self.window.mainloop()

    def show_menu(self, menu, button):
        """Show the menu below the button."""
        self.x = button.winfo_rootx()
        self.y = button.winfo_rooty() + button.winfo_height()
        menu.post(self.x, self.y)

    def on_option_select(self, option):
        """Handle menu option selection."""
        if option == "Configure":
           self.open_new_window()
        else:
            print(f"Selected: {option}")

    # Configure window
    def open_new_window(self):
        self.configure_window = ttk.Toplevel(self.window)
        self.configure_window.title("Configure")
        self.configure_window.geometry("500x320")
        self.configure_window.resizable(False, False)

        # Interface label and dropdown
        ttk.Label(self.configure_window, text='Interface Type').grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.interface_list = ['PCAN', 'Vector']
        self.interfaceName = tk.StringVar(value=self.interface_list[0])
        self.interface_dropdown = ttk.Combobox(self.configure_window, textvariable=self.interfaceName, values=self.interface_list, width=40, state='readonly')
        self.interface_dropdown.grid(row=0, column=1, padx=10, pady=15)
        self.interface_dropdown.bind('<<ComboboxSelected>>', self.on_interface_change)

        # Channel label and dropdown
        ttk.Label(self.configure_window, text='Channel').grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.channel_list = list(pcan_constants.PCAN_CHANNELS.keys())
        self.channel_name = tk.StringVar(value="None")
        self.channel_dropdown = ttk.Combobox(self.configure_window, textvariable=self.channel_name, values=self.channel_list, width=40, state='readonly')
        self.channel_dropdown.grid(row=1, column=1, padx=10, pady=15)

        # Baudrate label and dropdown
        ttk.Label(self.configure_window, text='Baudrate').grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.baudrate_list = list(pcan_constants.PCAN_BAUD_RATES.keys())
        self.baudrate_name = tk.StringVar(value="None")
        self.baudrate_dropdown = ttk.Combobox(self.configure_window, textvariable=self.baudrate_name, values=self.baudrate_list, width=40, state='readonly')
        self.baudrate_dropdown.grid(row=2, column=1, padx=10, pady=15)

        # Submit button
        self.ok_button = ttk.Button(self.configure_window, text="OK", width=10, command=self.close_configure_window, style='White.TButton')
        self.ok_button.grid(row=3, column=0, padx=10, pady=20, sticky="w")

        self.on_interface_change(None)

    def on_interface_change(self, event):
        """Handle the change in interface selection."""
        selected_interface = self.interfaceName.get()
        if selected_interface == 'Vector':
            self.channel_dropdown.config(state='disabled')
            self.baudrate_dropdown.config(state='disabled')
        else:
            self.channel_dropdown.config(state='readonly')
            self.baudrate_dropdown.config(state='readonly')

    def close_configure_window(self):
        self.Interface = self.interfaceName.get()
        self.Channel = self.channel_name.get() 
        self.Baudrate = self.baudrate_name.get()  
        print(self.Interface, self.Channel, self.Baudrate)

        self.display_trace.config(state='normal')  # Make sure the widget is in normal state before inserting
        self.display_trace.delete("1.0", tk.END)  # Clear previous content
        self.display_trace.insert(tk.END, str(pcan_constants.PCAN_MESSAGE_TYPES.keys()))  # Insert new results
        self.display_trace.config(state='disabled')  # Set back to disabled

        self.configure_window.destroy()

    async def start_session(self):
        # druv's start session
        #self.run_async_function(self.start_session)
        await self.uds_wrap.start_session()
        # self.run_async_function(self.uds_wrap.start_session())

# 
        if not hasattr(self, 'message'):
            self.message = Message(self.message_tab, self.display_trace)
        
        if self.message_button['text'] == "Start Session":
            self.message_button['text'] = "Stop Session"
            self.message.start()  # Start the message functionality
        else:
            self.message_button['text'] = "Start Session"
            self.message.stop()  # Stop the message functionality

    """ def message_process(self):
        self.values = [self.vars[bit].get() for bit in range(8)]  # Get the value for each bit (0-7)

        # Reorder values to match the original bit order (from Bit 7 to Bit 0)
        self.arr = self.values[::-1]  # Reverse the list to match the original order

        self.binary_string = ''.join(map(str, self.arr))

        # User input values
        self.Transmit_CANID = self.canTX_name.get()
        self.Receive_CANID = self.canRX_name.get()
        self.Message_Type = self.msgtype_name.get()

        self.ServiceID = self.sid_name.get()[2:4]
        self.Subfunction = self.sfunc_name.get()[2:4]

        # Convert binary string to hexadecimal string
        self.DTC_StatusMask = hex(int(self.binary_string, 2))[2:].upper().zfill(2)

        # Update the text area with the results
        self.display_trace.delete("1.0", tk.END)  # Clear previous content
        self.display_trace.insert(tk.END, str(pcan_constants.PCAN_MESSAGE_TYPES.keys()))  # Insert new results

        print(self.Channel, self.Baudrate, self.Transmit_CANID, self.Receive_CANID, self.Message_Type, self.ServiceID, self.Subfunction, self.DTC_StatusMask) """

    def run_async_function(self, async_func):
        def wrapper():
            asyncio.run_coroutine_threadsafe(async_func(), asyncio_loop)
        return wrapper

class Message:
    count = 0
    

    def __init__(self, parent_frame, display_trace):
        self.parent_frame = parent_frame
        self.display_trace = display_trace
        Message.count += 1
        self.button_count = 0
        self.new_buttons = []

        # Create the "New Request" button
        self.new_request_button = ttk.Button(self.parent_frame, text="New Request", width=90, command=self.create_new_request, style='Bold.TButton')
        self.new_request_button.grid(row=1, column=0, pady=7, sticky="w")

    def start(self):
        # Any specific logic to start the message
        print("Session started")

    def stop(self):
        # Any specific logic to stop the message
        print("Session stopped")

    def create_new_request(self):
        self.button_count += 1

        # Open a new window for the new request details
        self.new_request_window = ttk.Toplevel()
        self.new_request_window.title(f"Request Details {self.button_count}")
        self.new_request_window.geometry("400x200")

        # Add labels and entry fields
        ttk.Label(self.new_request_window, text="Enter Details:").pack(pady=10)
        self.details_entry_name = tk.StringVar()
        self.details_entry = tk.Entry(self.new_request_window, width=40, textvariable=self.details_entry_name)
        self.details_entry.pack(pady=10)
        
        # Add OK button to close the window
        ttk.Button(self.new_request_window, text="OK", command=self.save_request_details).pack(pady=10)

    def save_request_details(self):
        button_text = self.details_entry_name.get()

        # Create a new button with the entered text
        new_button = ttk.Button(self.parent_frame, text=button_text, width=90, command=lambda: self.open_text_tab(button_text), style='Bold.TButton')
        new_button.grid(row=self.button_count, column=0, pady=7, sticky="w")

        # Save the button text to buttons_info
        #self.buttons_info[new_button] = button_text

        # Update the row configuration
        self.parent_frame.grid_rowconfigure(self.button_count, weight=0)

        self.new_request_button = ttk.Button(self.parent_frame, text="New Request", width=90, command=self.create_new_request, style='Bold.TButton')
        self.new_request_button.grid(row=self.button_count+1, column=0, pady=7, sticky="w")

        # Destroy the new request window
        self.new_request_window.destroy()

    def open_text_tab(self, text):
        """ # Create a new tab to display the button's text
        new_tab = ttk.Frame(self.notebook)
        self.notebook.add(new_tab, text=f"Request {len(self.notebook.tabs()) + 1}")

        text_widget = tk.Text(new_tab, wrap=tk.WORD, state='normal')
        text_widget.pack(expand=True, fill=tk.BOTH)
        text_widget.insert(tk.END, f"Details: {text}")
        text_widget.config(state='disabled') """
        print("NEwwwwwwww")

# Create and start the application
def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Create an asyncio event loop in a separate thread
asyncio_loop = asyncio.new_event_loop()
t = threading.Thread(target=start_async_loop, args=(asyncio_loop,), daemon=True)
t.start()

start = DTC_gui()
