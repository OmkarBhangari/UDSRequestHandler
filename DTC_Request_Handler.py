ARBITRATION_ID = 0x743

REQUEST         =   (0x03, 0x19, 0x02, 0x09, 0x00, 0x00, 0x00, 0x00)    # len = 4
FLOW_CONTROL    =   (0x30, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00)    # len = 3

class DTCRequestHandler:
    def __init__(self, ARBITRATION_ID, REQUEST, FLOW_CONTROL) -> None:
        self.ARBITRATION_ID = ARBITRATION_ID

        self.REQUEST = REQUEST
        self.FLOW_CONTROL = FLOW_CONTROL

        self.SESSION_ACTIVE = False

    def start_session(self):
        # write logic to initiate a session
        self.SESSION_ACTIVE = True

    def end_session(self):
        # write logic to initiate a session
        self.SESSION_ACTIVE = False
