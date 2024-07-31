from .UDSException import UDSException

ARBITRATION_ID                      = 0x763
SESSION_START_REQ                   = (0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00)
SESSION_START_REQ_NEG_RESPONSE      = (0x03, 0x7F, 0x10, 0x78, 0x00, 0x00, 0x00, 0x00)
SESSION_START_REQ_POS_RESPONSE      = (0x06, 0x50, 0x03, 0x32, 0x00, 0x13, 0x88, 0x00)
DTC_REQUEST                         = (0x03, 0x19, 0x02, 0x09, 0x00, 0x00, 0x00, 0x00)
DTC_REQUEST_NEG_RESPONSE            = (0x03, 0x7F, 0x19, 0x78, 0x00, 0x00, 0x00, 0x00)
FIRST_FRAME                         = (0x10, 0x29, 0x59, 0x02, 0x09, 0xE1, 0x4F, 0x87)
FLOW_CONTROL                        = (0x30, 0x02, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00)
CF_1                                = (0x21, 0x09, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00)
CF_2                                = (0x22, 0x09, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00)
CF_3                                = (0x23, 0x09, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00)
CF_4                                = (0x24, 0x09, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00)

class Frame:
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
    
    def validate_first_frame(self, response):
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

        # Check for positive response
        if response[0] == 0x10 and response[2] == 0x59:
            return True  # Valid positive response

        # If neither, raise an unexpected format exception
        raise Exception("Unexpected response format")
    
    def construct_flow_control(self, block_size, time_between_consecutive_frame):
        return (0x30, block_size, time_between_consecutive_frame, 0x00, 0x00, 0x00, 0x00, 0x00)