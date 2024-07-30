class UDSException(Exception):
    """Exception for UDS errors"""
    def __init__(self, nrc):
        self.nrc = nrc
        self.message = self.get_error_message(nrc)
        super().__init__(self.message)

    def get_error_message(self, nrc):
        error_messages = {
            0x10: "General reject",
            0x11: "Service not supported",
            0x12: "Sub-function not supported",
            0x13: "Incorrect message length or invalid format",
            0x14: "Response too long",
            0x21: "Busy repeat request",
            0x22: "Conditions not correct",
            0x24: "Request sequence error",
            0x25: "No response from subnet component",
            0x26: "Failure prevents execution of requested action",
            0x31: "Request out of range",
            0x33: "Security access denied",
            0x35: "Invalid key",
            0x36: "Exceed number of attempts",
            0x37: "Required time delay not expired",
            0x38: "Secure data transmission not supported",
            0x39: "Secure data transmission not allowed",
            0x3A: "Secure data transmission error",
            0x3B: "Secure data transmission busy",
            0x3F: "General programming failure",
            0x41: "Wrong block sequence counter",
            0x42: "Response pending",
            0x43: "Sub-function not supported in active session",
            0x45: "General programming failure",
            0x71: "Transfer aborted",
            0x72: "Incorrect block sequence counter",
            0x73: "Unsupported transfer type",
            0x78: "Request correctly received, response pending",
            0x7E: "Sub-function not supported in active session",
            0x7F: "Service not supported in active session"
        }
        return error_messages.get(nrc, f"Unknown NRC: {nrc}")