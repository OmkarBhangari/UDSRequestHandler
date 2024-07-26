class Inactive:
    def __init__(self) -> None:
        pass

    def activate_session() -> None:
        # write logic to start session
        pass

class Idle:
    def __init__(self) -> None:
        pass
    
    def send_DTC_request() -> None:
        # write logic to send DTC Req (0x19) and change state to Receive
        pass

class Receive:
    def __init__(self) -> None:
        pass

    def recieve_frame() -> None:
        # write logic to get the next frame on the Receive Queue
        pass

    def send_control_frame() -> None:
        # write logic to send a control frame
        pass

    def send_tester_frame() -> None:
        # write logic to send a control frame
        pass

class DTCRequestHandler:
    def __init__(self) -> None:
        pass