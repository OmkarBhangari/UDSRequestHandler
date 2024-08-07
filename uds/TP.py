import queue
from .frame import Frame

class TP:
    CONTROL_FRAME = (0x30, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00)
    def __init__(self, frame, uds):
        self.block_size = 4
        self.temp_block_size = 0
        self.time_between_consecutive_frames = 20
        self.frame = frame
        self.requesting_class = None
        self.uds = uds

        self.buffer = queue.Queue()

        self.data = []
        self.bytes = None # stores the number of bytes to be sent by ECU
        self.no_of_frames = None # stores the number of bytes to be send by ECU
        self.counter = 0

    def buffer_frame_data(self, frame, frame_type):
        self.buffer.put({"frame_type": frame_type, "frame": frame})  
              
    @staticmethod   
    def  extract_data(data):
        all_data = []
        all_data.extend(data[0][2:])
        for i in range(1, len(data)):
            #print(f"Consecutive frame: {data[i]}")
            all_data.extend(data[i][1:] ) # Exclude the first byte (frame identifier)
        return all_data

    def main(self):
        if self.requesting_class is not None:
            if not self.buffer.empty():
                frame_data = self.buffer.get()
                self.data.append(frame_data['frame'])

                if frame_data['frame_type'] == Frame.FIRST_FRAME:
                    # extract the number of bytes and 3 bytes of data from FF
                    self.bytes = self.frame.extract_length(frame_data['frame'])

                    # calculate the total number of frames to be sent by ECU
                    self.no_of_frames = self.bytes // 7

                    # Initialize counter to 0
                    self.counter = 0

                elif frame_data['frame_type'] == Frame.CONSECUTIVE_FRAME:
                    self.counter -= 1
                    self.no_of_frames -= 1
                
                # after we have received all frames we can terminate the transaction
                if self.no_of_frames == 0:
                    self.requesting_class.buffer_frame(self.data)
                    self.data = []
                    self.requesting_class = None
                    return

                # if counter is 0; it means that we need to start a new block cycle by sending a flow control frame
                if self.counter == 0:
                    self.counter = min(self.no_of_frames, self.block_size)
                    self.uds.queue_frame(self.frame.construct_flow_control(self.counter, self.time_between_consecutive_frames))