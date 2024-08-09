from .pcan import PCAN  
from .frame import Frame  
from .TP import TP  
from .UDSException import *  

from .Ox10 import Ox10  
from .Ox19 import Ox19

import time  # Importing the time module for sleep functionality
import queue  # Importing the queue module for thread-safe data exchange
import threading  # Importing the threading module for concurrent operations

from . import Colors

class Tx:
    """
    Transmission class to handle sending frames via PCAN.
    """

    def __init__(self, pcan, Tx_ID):
        """
        Initializes the Tx class with a PCAN instance and transmission ID.

        :param pcan: PCAN instance for CAN communication.
        :param Tx_ID: ID used for transmission.
        """
        self.pcan = pcan
        self.Tx_ID = Tx_ID

    def transmit(self, data):
        """
        Sends a frame with the specified data.

        :param data: Data to be transmitted.
        """
        self.pcan.send_frame(self.Tx_ID, data)
        print(f"{Colors.blue}Transmitted : {Frame.hex(data)}{Colors.reset}")


class Rx:
    """
    Reception class to handle receiving frames via PCAN.
    """

    def __init__(self, pcan, Rx_ID):
        """
        Initializes the Rx class with a PCAN instance and reception ID.

        :param pcan: PCAN instance for CAN communication.
        :param Rx_ID: ID used for reception.
        """
        self.pcan = pcan
        self.Rx_ID = Rx_ID

    def receive(self):
        """
        Receives a frame and returns the data.

        :return: Data received from the frame.
        """
        data = self.pcan.receive_frame()
        print(f"{Colors.yellow}Received : {Frame.hex(data)}{Colors.reset}")
        return data


class UDS:
    """
    UDS (Unified Diagnostic Services) class to manage CAN communication and handle different frames.
    """

    def __init__(self, Tx_ID, Rx_ID):
        """
        Initializes the UDS class with transmission and reception IDs.

        :param Tx_ID: Transmission ID.
        :param Rx_ID: Reception ID.
        """
        self.pcan = PCAN("PCAN_USBBUS1", "PCAN_BAUD_500K", "PCAN_MESSAGE_STANDARD")
        self.frame = Frame()
        self.tp = TP(self.frame, self)

        self.tx = Tx(self.pcan, Tx_ID)
        self.rx = Rx(self.pcan, Rx_ID)

        self.queue = queue.Queue()  # Queue to store frames to be transmitted

        self.handlers = {
            0x10: Ox10(self),
            0x19: Ox19(self)
        }

        event_thread = threading.Thread(target=self.__event_loop, daemon=True)
        event_thread.start()  # Start the event loop in a separate thread

    def __event_loop(self):
        """
        Event loop to continuously process incoming frames and handle transmission.
        """
        while True:
            self.dispatch_frame()  # Dispatch frame from the queue if available
            incoming_frame = self.rx.receive()  # Receive incoming frame
            self.handle_incoming_frame(incoming_frame)  # Handle the received frame
            self.tp.main()  # Process Transport Protocol main function
            self.handlers.get(0x19).main()  # Process handler for SID 0x19
            time.sleep(1)  # Sleep to reduce CPU usage

    def handle_incoming_frame(self, incoming_frame):
        """
        Handles the incoming frame and routes it based on its type.

        :param incoming_frame: The incoming frame to handle.
        """
        try:
            # Validate the incoming frame and determine its type
            frame_type = self.frame.validate_frame(incoming_frame)

        except UDSException as exception:
            # Handle specific UDSException errors
            print(f"{Colors.red}{exception}{Colors.reset}")
            # Get the Service ID (SID) for an error frame
            sid = self.frame.get_sid(incoming_frame, Frame.ERROR_FRAME)
            # Route the frame based on the error SID
            self.route_frame(sid, incoming_frame)

        except Exception as exception:
            # Handle any other exceptions
            print(f"{Colors.red}{exception}{Colors.reset}")
        else:
            # If no exceptions, process the frame based on its type

            # Get the SID for the validated frame
            sid = self.frame.get_sid(incoming_frame, frame_type)

            if frame_type == Frame.SINGLE_FRAME:
                # If the frame is a single frame, route it directly
                self.route_frame(sid, incoming_frame)

            elif frame_type == Frame.FIRST_FRAME:
                # If the frame is the first frame of a multi-frame message, buffer it to TP class and
                # set the requesting class corresponding to sid
                self.tp.requesting_class = self.handlers.get(sid)
                self.tp.buffer_frame_data(incoming_frame, frame_type)  # Buffer the first frame data

            elif frame_type == Frame.CONSECUTIVE_FRAME:
                # If the frame is a consecutive frame of a multi-frame message, buffer it to TP class
                self.tp.buffer_frame_data(incoming_frame, frame_type)

    def dispatch_frame(self):
        """
        Dispatches a frame from the queue for transmission.
        """
        if not self.queue.empty():
            frame = self.queue.get()
            self.tx.transmit(frame)

    def queue_frame(self, frame):
        """
        Adds a frame to the queue for later transmission.

        :param frame: The frame to queue.
        """
        self.queue.put(frame)

    def route_frame(self, sid, frame):
        """
        Routes the frame to the appropriate handler based on its Service ID (SID).

        :param sid: Service ID of the frame.
        :param frame: The frame to route.
        """
        handler = self.handlers.get(sid)
        if handler: handler.buffer_frame(frame)
        else: print(f"No handler for SID {sid}")
