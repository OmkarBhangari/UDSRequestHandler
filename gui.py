import tkinter as tk
from tkinter import ttk
from app import App

class DiagnosticGUI:
    START_SESSION = (0x10, 0x03)
    SEND_DTC = (0x19, 0x02, 0x09)

    def __init__(self, master):
        self.master = master
        master.title("Diagnostic Tool")

        self.app = None 
        self.uds = None 

        self.start_button = ttk.Button(master, text="Start Session", command=self.start_session)
        self.start_button.pack()

        self.send_button = ttk.Button(master, text="Send Request", command=self.send_request, state=tk.DISABLED)
        self.send_button.pack()

        self.response_text = tk.Text(master, height=10, width=50)
        self.response_text.pack()

    def start_session(self):
        # Parameters to initialize the app
        tx_id = 0x743
        rx_id = 0x763
        channel = "PCAN_USBBUS1"
        baud_rate = "PCAN_BAUD_500K"
        message_type = "PCAN_MESSAGE_STANDARD"

        # Initialize the app and UDS
        self.app = App(tx_id, rx_id, channel, baud_rate, message_type)
        self.uds = self.app.get_uds()

        # Start monitoring in a separate thread
        self.app.start_monitoring()

        self.uds.send_request(DiagnosticGUI.START_SESSION)
        # Enable the Send Request button
        self.send_button['state'] = tk.NORMAL

        # Start updating the GUI with responses
        self.master.after(100, self.update_response)

    # sends data to uds for processing
    def send_request(self):
        try:
            self.uds.send_request(DiagnosticGUI.SEND_DTC)  
        except Exception as e:
            self.response_text.insert(tk.END, f"UDS Error: {e}\n")

    def update_response(self):
        response = self.uds.get_response()
        if response:
            self.response_text.insert(tk.END, f"Response: {response}\n")
            self.response_text.see(tk.END)
        self.master.after(100, self.update_response)

    def on_close(self):
        if self.app:
            self.app.stop_monitoring()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    gui = DiagnosticGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close)
    root.mainloop()
