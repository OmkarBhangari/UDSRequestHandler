from .UDSException import UDSException

class Frame:
    SINGLE_FRAME: int = 0
    FIRST_FRAME: int = 1

    ARBITRATION_ID                      = 0x763
    SESSION_START_REQ                   = (0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00)
    DTC_REQUEST                         = (0x03, 0x19, 0x02, 0x09, 0x00, 0x00, 0x00, 0x00)

    def __init__(self):
        pass

    def validate_session_response(self, response):
        """Validates the response for the start extended diagnostic session request.

        Args:
            response (TPCANMsg.DATA): The response message to validate.

        Raises:
            UDSException: If an NRC is found in the response.
            Exception: If the response format is unexpected or not a positive response.
        """
        # Check for negative response (NRC)
        if response[0] == 0x03 and response[1] == 0x7F:
            nrc = response[3]
            raise UDSException(nrc)
        
        # If all bytes of the frame are zero
        if response[0] == 0x00 and response[1] == 0x00:
            raise Exception("Empty Frame")

        # Check for positive response
        if response[1] == 0x50 and response[2] == 0x03:
            return True  # Valid positive response

        # If neither, raise an unexpected format exception
        raise Exception("Unexpected response format")
    
    def validate_frame(self, response):
        """Validates the first frame of DTC request response

        Args:
            response (TPCANMsg.DATA): The response message to validate.

        Raises:
            UDSException: If an NRC is found in the response.
            Exception: If the response format is unexpected or not a positive response.
        """
        # Check for negative response (NRC)
        if response[0] == 0x03 and response[1] == 0x7F:
            nrc = response[3]
            raise UDSException(nrc)
        
        # If all bytes of the frame are zero
        if response[0] == 0x00 and response[1] == 0x00:
            raise Exception("Empty Frame")

        '''
            write logic to check if it is first frame of consecutive frame.
            if it is SF return 0 else if it is FF return 1
            Check for positive response

            if SF():
                return 0
            if FF():
                return 1
        '''

        if response[0] == 0x10 and response[2] == 0x59:
            return True  # Valid positive response

        # If neither, raise an unexpected format exception
        raise Exception("Unexpected response format")
    
    def construct_flow_control(self, block_size, time_between_consecutive_frame):
        return (0x30, block_size, time_between_consecutive_frame, 0x00, 0x00, 0x00, 0x00, 0x00)