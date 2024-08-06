from UDSException import UDSException

class Frame:
    SINGLE_FRAME: int = 0
    FIRST_FRAME: int = 1
    
    def validate_frame(self, response):
        # Check for negative response (NRC)
        if response[1] == 0x7F:
            nrc = response[3]
            raise UDSException.create_exception(nrc)
        
        # If all bytes of the frame are zero
        if response[0] == 0x00 and response[1] == 0x00:
            raise Exception("Empty Frame")

        if (response[0] & 0xF0) == 0x00 :
            return  Frame.SINGLE_FRAME
        
        if (response[0] & 0xF0) == 0x10:
            return Frame.FIRST_FRAME  # Valid positive response

        # If neither, raise an unexpected format exception
        raise Exception("Unexpected response format")

    def get_sid(self, frame, frame_type):
        if frame_type == Frame.SINGLE_FRAME:
            # return SID
            pass
        if frame_type == Frame.FIRST_FRAME:
            # return SID
            pass