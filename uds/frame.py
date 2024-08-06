from UDSException import UDSException

class Frame:
    SINGLE_FRAME: int = 0
    FIRST_FRAME: int = 1
    CONSECUTIVE_FRAMES: int=2
    ERROR_FRAME: int = 3
    
    def validate_frame(self, response):
        # Check for negative response (NRC)
        if response[1] == 0x7F:
            nrc = response[3]
            raise UDSException.create_exception(nrc)
        
        # If all bytes of the frame are zero
        if all(frame == 0x00 for frame in response):
             raise Exception("Empty Frame")

        if (response[0] & 0xF0) == 0x00 :
            return  Frame.SINGLE_FRAME
        
        if (response[0] & 0xF0) == 0x10:
            return Frame.FIRST_FRAME  # Valid positive response
            
        if (response[0] & 0xF0) == 0x20:
            return Frame.CONSECUTIVE_FRAME
        
        # If neither, raise an unexpected format exception
        raise Exception("Unexpected response format")

    def get_sid(self, frame, frame_type):
        if frame_type == Frame.SINGLE_FRAME:
            sid = frame[1] - 0x40
            return sid
            
        if frame_type == Frame.FIRST_FRAME:
            sid = frame[2] - 0x40
            return sid
            
        if frame_type == Frame.ERROR_FRAME:
            sid = frame[2]
            return sid
        
    def extract_length_and_data(self, frame):
        return  ( (frame[0] & 0x0F)<<8 )  |  frame[1],frame[5:]
    
    def hex(self, msg):
        return tuple([hex(m) for m in msg])
    
    def construct_flow_control(self, block_size, time_between_consecutive_frame):
        return (0x30, block_size, time_between_consecutive_frame, 0x00, 0x00, 0x00, 0x00, 0x00)
