from .Can import CAN
from .event_manager import EventManager
from .frame import Frame
import queue

class CAN_TP:
    def __init__(self, tx_id, rx_id, channel, baud_rate, message_type, event_manager: EventManager) -> None:
        self.event_manager = event_manager
        self.can = CAN(tx_id, rx_id, channel, baud_rate, message_type, self.event_manager)
        self.event_manager.subscribe('data_received', self.get_data)
        self.store_data = []  # to store data received from can.py
        self.buffer_to_can = queue.Queue()
        self.buffer_from_uds = queue.Queue()
        self.frame = Frame()

        self.bytes = None  # stores the number of bytes to be sent by ECU
        self.no_of_frames = 0  # stores the number of frames to be received from ECU
        self.frames_received = 0  # initialize frames_received
        self.counter = 0
        self.block_size = 4
        self.time_between_consecutive_frames = 20

        # State for multi-frame transmission
        self.remaining_data = None
        self.sequence_number = 1

    def get_data(self, incoming_frame):
        self.process_frame(incoming_frame)

    # sending data to the tx_buffer of can.py
    def send_data(self, data):
        print("send_data:", data)  # debug line
        self.can.transmit_data(data)

    # processes the frames received from the ECU
    def process_frame(self, incoming_frame):
        # Ignore frames that are all zeros
        if all(byte == 0 for byte in incoming_frame):
            print("Ignoring frame with all zeros")
            return

        # Validate the incoming frame and determine its type
        self.frame_type = self.frame.validate_frame(incoming_frame)

        if self.frame_type == self.frame.SINGLE_FRAME:
            # If the frame is a single frame, route it directly
            self.store_data = []
            self.temp = list(incoming_frame[1:])  # Convert to list
            self.store_data.extend(self.temp)
            print("Sending data from single frame")
            self.route_frame()

        elif self.frame_type == self.frame.FIRST_FRAME:
            # Extract the number of bytes and data from FF
            self.bytes = self.frame.extract_length(incoming_frame)
            self.no_of_frames = (self.bytes + 6) // 7  # Calculate total frames needed
            self.frames_received = 1  # We've received the first frame

            # Initialize counter and store data
            self.counter = min(self.no_of_frames - 1, self.block_size)  # Subtract 1 as we've already received the first frame
            self.store_data = list(incoming_frame[2:])  # Convert to list

            # Send Flow Control Frame after receiving the First Frame
            self.FC_frame = self.frame.construct_flow_control(self.counter, self.time_between_consecutive_frames)
            self.send_data(self.FC_frame)

            print(f"First frame received. Expecting {self.no_of_frames - 1} more frames.")

        elif self.frame_type == self.frame.CONSECUTIVE_FRAME:
            # Process consecutive frames
            self.frames_received += 1
            self.counter -= 1

            # Extract data from Consecutive Frames
            self.temp = list(incoming_frame[1:])  # Convert to list
            self.store_data.extend(self.temp)

            print(f"Consecutive frame received. Total frames received: {self.frames_received}/{self.no_of_frames}")

            # Check if we've received all frames
            if self.frames_received == self.no_of_frames:
                print("All frames received. Sending data from consecutive frames.")
                self.route_frame()
            elif self.counter == 0:
                # Send a new Flow Control Frame only if more frames are expected
                if self.frames_received < self.no_of_frames:
                    self.counter = min(self.no_of_frames - self.frames_received, self.block_size)
                    self.FC_frame = self.frame.construct_flow_control(self.counter, self.time_between_consecutive_frames)
                    self.send_data(self.FC_frame)
                    print(f"Sent Flow Control frame, expecting {self.counter} more frames")

        elif self.frame_type == self.frame.FLOW_CONTROL_FRAME:
            # Process the Flow Control frame and send consecutive frames
            self.rec_block_size = incoming_frame[1]
            self.time_between_consecutive_frames = incoming_frame[2]
            print(f"Flow control frame received: block size = {self.rec_block_size}, time between frames = {self.time_between_consecutive_frames} ms")
            self.send_consecutive_frames(self.rec_block_size)

    def route_frame(self):
        self.store_data = self.frame.hex(self.store_data)
        self.store_data = tuple(self.store_data)
        print("Publishing data to uds")
        self.event_manager.publish('data_to_uds', self.store_data)
        self.store_data = []  # Clear stored data after routing

    # Processes the frames to be sent to the ECU
    def process_uds_data(self, data):
        print(data)  # debug line
        if len(data) <= 7:
            # Single Frame
            frame = bytearray([len(data)])  # First byte indicates length
            frame.extend(data)
            frame.extend([0] * (8 - len(frame)))  # Pad with zeros
            frame_tuple = tuple(frame)
            print("buffer_to_can: ", frame_tuple)
            self.buffer_to_can.put(frame_tuple)
        else:
            # Multi Frame
            self.send_multi_frame(data)

    def send_multi_frame(self, data):
        total_length = len(data)

        # First Frame
        first_frame = bytearray([0x10 | (total_length >> 8), total_length & 0xFF])
        first_frame.extend(data[:6])
        first_frame_tuple = tuple(first_frame)
        self.buffer_to_can.put(first_frame_tuple)

        # Prepare for sending Consecutive Frames
        self.remaining_data = data[6:]
        self.sequence_number = 1

    def send_consecutive_frames(self, received_block_size):
        self.received_block_size = received_block_size
        if not self.remaining_data:
            return

        for _ in range(self.received_block_size):
            if not self.remaining_data:
                break
            frame = bytearray([0x20 | (self.sequence_number & 0x0F)])
            frame.extend(self.remaining_data[:7])
            self.remaining_data = self.remaining_data[7:]
            if len(frame) < 8:
                frame.extend([0xAA] * (8 - len(frame)))  # Pad with AA if needed
            frame_tuple = tuple(frame)
            self.buffer_to_can.put(frame_tuple)
            self.sequence_number = (self.sequence_number + 1) & 0x0F

        # If we are out of data but receive a Flow Control asking for more frames
        if not self.remaining_data and self.received_block_size > 0:
            print("No more data to send. Sending 'AA' as padding data.")
            while self.received_block_size > 0:
                frame = bytearray([0x20 | (self.sequence_number & 0x0F)])
                frame.extend([0xAA] * 7)  # Send "AA" as padding
                frame_tuple = tuple(frame)
                self.buffer_to_can.put(frame_tuple)
                self.sequence_number = (self.sequence_number + 1) & 0x0F
                self.received_block_size -= 1

        # Reset block size to 0 to wait for the next Flow Control
        self.received_block_size = 0

    # sends data from the buffer_to_can to the buffer present in can.py
    def send_data_to_can(self):
        while not self.buffer_to_can.empty():
            self.frame_to_can = self.buffer_to_can.get()
            print("sending data to can: ", self.frame_to_can)   # debug line
            self.send_data(self.frame_to_can)

    # this function is called from the uds.py
    def receive_data_from_uds(self, data):
        print("Data received from uds: ", data)  # debug line
        self.buffer_from_uds.put(data)

    # processes data received from uds.py
    def process_uds_queue(self):
        while not self.buffer_from_uds.empty():
            data = self.buffer_from_uds.get()
            print("process uds data: ", data)  # debug line
            self.process_uds_data(data)

    # this function is called from app.py for continuous monitoring
    def cantp_monitor(self):
        self.process_uds_queue()
        self.send_data_to_can()
